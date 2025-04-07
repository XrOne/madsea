#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web Interface for Storyboard-to-Video AI Platform

This module provides a simple Flask web interface for the platform, allowing users to:
- Upload storyboard PDFs or images
- Select visual styles
- Run the generation process
- View progress and preview results
"""

import os
import sys
import logging
import time
import json
import threading
from pathlib import Path
from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsing.parser import StoryboardParser
from generation.generator import ImageGenerator
from styles.manager import StyleManager
from video.assembler import VideoAssembler
from utils.config import load_config, save_config

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'results'

# Global variables for tracking generation progress
generation_status = {
    'running': False,
    'progress': 0,
    'total': 0,
    'current_scene': 0,
    'message': '',
    'result_video': None,
    'scenes': []
}

# Global configuration
config = None

# Global component instances
parser = None
style_manager = None
generator = None
assembler = None


def init_app(config_path=None):
    """
    Initialize the application components
    
    Args:
        config_path (str, optional): Path to configuration file
    """
    global config, parser, style_manager, generator, assembler
    
    # Load configuration
    config = load_config(config_path)
    
    # Create upload and result directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    
    # Initialize components
    parser = StoryboardParser(config)
    style_manager = StyleManager(config)
    generator = ImageGenerator(config, style_manager)
    assembler = VideoAssembler(config)
    
    logger.info("Application initialized")


@app.route('/')
def index():
    """
    Render the main page
    """
    # Get available styles
    styles = style_manager.list_styles() if style_manager else []
    
    return render_template(
        'index.html',
        styles=styles,
        status=generation_status,
        config=config
    )


@app.route('/upload', methods=['POST'])
def upload_storyboard():
    """
    Handle storyboard upload
    """
    if 'storyboard' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['storyboard']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save the uploaded file
    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'path': upload_path
    })


@app.route('/generate', methods=['POST'])
def generate():
    """
    Start the generation process
    """
    global generation_status
    
    # Check if generation is already running
    if generation_status['running']:
        return jsonify({'error': 'Generation already in progress'}), 400
    
    # Get parameters
    data = request.json
    storyboard_path = data.get('storyboard_path')
    style_name = data.get('style', 'default')
    use_cloud = data.get('use_cloud', False)
    
    # Validate parameters
    if not storyboard_path or not os.path.exists(storyboard_path):
        return jsonify({'error': 'Invalid storyboard path'}), 400
    
    # Update config
    config['storyboard_path'] = storyboard_path
    config['style'] = style_name
    config['use_cloud'] = use_cloud
    
    # Start generation in a separate thread
    generation_thread = threading.Thread(
        target=run_generation,
        args=(storyboard_path, style_name, use_cloud)
    )
    generation_thread.daemon = True
    generation_thread.start()
    
    return jsonify({'success': True, 'message': 'Generation started'})


def run_generation(storyboard_path, style_name, use_cloud):
    """
    Run the generation process in a separate thread
    
    Args:
        storyboard_path (str): Path to the storyboard
        style_name (str): Name of the style to apply
        use_cloud (bool): Whether to use cloud resources
    """
    global generation_status
    
    try:
        # Update status
        generation_status['running'] = True
        generation_status['progress'] = 0
        generation_status['message'] = 'Parsing storyboard...'
        generation_status['result_video'] = None
        generation_status['scenes'] = []
        
        # Parse storyboard
        scenes = parser.parse(storyboard_path)
        generation_status['total'] = len(scenes)
        generation_status['scenes'] = scenes
        
        # Generate images for each scene
        generated_images = []
        for i, scene in enumerate(scenes):
            generation_status['current_scene'] = i + 1
            generation_status['progress'] = (i / len(scenes)) * 100
            generation_status['message'] = f"Generating image for scene {i+1}/{len(scenes)}..."
            
            # Generate image
            image = generator.generate(scene['image'], scene['text'], style_name)
            generated_images.append(image)
            
            # Update scene with generated image
            scene['generated_image'] = image
        
        # Assemble video
        generation_status['message'] = "Assembling video..."
        output_path = os.path.join(app.config['RESULT_FOLDER'], f"storyboard_video_{int(time.time())}.mp4")
        config['output_path'] = output_path
        
        video_path = assembler.create_video(generated_images, scenes)
        
        # Update status
        generation_status['progress'] = 100
        generation_status['message'] = "Generation completed successfully!"
        generation_status['result_video'] = video_path
    except Exception as e:
        logger.error(f"Error during generation: {e}")
        generation_status['message'] = f"Error: {str(e)}"
    finally:
        generation_status['running'] = False


@app.route('/status')
def get_status():
    """
    Get the current generation status
    """
    return jsonify(generation_status)


@app.route('/preview/<path:filename>')
def preview_file(filename):
    """
    Preview a generated file
    
    Args:
        filename (str): Path to the file
    """
    return send_file(filename)


@app.route('/styles')
def list_styles():
    """
    List available styles
    """
    styles = style_manager.list_styles()
    return jsonify(styles)


@app.route('/styles/create', methods=['POST'])
def create_style():
    """
    Create a new style
    """
    data = request.json
    style_name = data.get('name')
    style_data = data.get('data', {})
    
    if not style_name:
        return jsonify({'error': 'Style name is required'}), 400
    
    success = style_manager.create_style(style_name, style_data)
    
    if success:
        return jsonify({'success': True, 'message': f"Style '{style_name}' created successfully"})
    else:
        return jsonify({'error': f"Failed to create style '{style_name}'"}), 500


@app.route('/styles/train', methods=['POST'])
def train_style():
    """
    Train a new style
    """
    data = request.json
    style_name = data.get('name')
    training_images_dir = data.get('training_images_dir')
    base_style = data.get('base_style')
    
    if not style_name or not training_images_dir:
        return jsonify({'error': 'Style name and training images directory are required'}), 400
    
    if not os.path.exists(training_images_dir):
        return jsonify({'error': f"Training images directory '{training_images_dir}' not found"}), 400
    
    # Start training in a separate thread
    def train_thread():
        success = style_manager.train_style(style_name, training_images_dir, base_style)
        logger.info(f"Style training {'completed successfully' if success else 'failed'}")
    
    training_thread = threading.Thread(target=train_thread)
    training_thread.daemon = True
    training_thread.start()
    
    return jsonify({'success': True, 'message': f"Style training started for '{style_name}'"})


@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """
    Get or update configuration
    """
    global config
    
    if request.method == 'POST':
        # Update config
        data = request.json
        config.update(data)
        
        # Save config
        save_config(config, 'config/user.yaml')
        
        return jsonify({'success': True, 'message': 'Configuration updated'})
    else:
        # Get config
        return jsonify(config)


def start_web_app(config_path=None, host='127.0.0.1', port=5000, debug=False):
    """
    Start the Flask web application
    
    Args:
        config_path (str, optional): Path to configuration file
        host (str, optional): Host to bind to
        port (int, optional): Port to bind to
        debug (bool, optional): Whether to run in debug mode
    """
    # Initialize the application
    init_app(config_path)
    
    # Start the Flask app
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("web_app.log"),
        ],
    )
    
    # Start the web app
    start_web_app(debug=True)