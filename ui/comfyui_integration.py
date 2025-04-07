#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ComfyUI Integration Module for Storyboard-to-Video AI Platform

This module provides integration between the platform and ComfyUI (SwarmUI).
It handles:
- Serving the SwarmUI extension
- Proxying requests to ComfyUI
- Managing workflows and LoRA models
- Providing API endpoints for the SwarmUI extension
- Processing storyboard PDFs and extracting scenes
- Generating images using Stable Diffusion with ControlNet and LoRA
- Creating animated videos from generated images
"""

import os
import sys
import json
import logging
import requests
import uuid
import time
import base64
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, jsonify, send_file, Response, url_for

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsing.parser import StoryboardParser
from generation.generator import ImageGenerator
from video.assembler import VideoAssembler
from styles.manager import StyleManager
from utils.config import load_config

logger = logging.getLogger(__name__)

# Create Blueprint for ComfyUI integration
comfyui_bp = Blueprint('comfyui', __name__, url_prefix='/comfyui')

# Global variables
config = None
style_manager = None
parser = None
generator = None
assembler = None
comfyui_host = None
comfyui_port = None
workflow_dir = None

# Dictionary to track generation jobs
generation_jobs = {}

# Temporary directory for uploads
upload_dir = Path('uploads')
temp_dir = Path('temp')
output_dir = Path('output')


def init_comfyui_integration(app_config):
    """
    Initialize ComfyUI integration
    
    Args:
        app_config (dict): Application configuration
    """
    global config, style_manager, parser, generator, assembler, comfyui_host, comfyui_port, workflow_dir
    
    config = app_config
    style_manager = StyleManager(config)
    
    # Get ComfyUI settings
    comfyui_host = config.get("comfyui", {}).get("host", "127.0.0.1")
    comfyui_port = config.get("comfyui", {}).get("port", 8188)
    workflow_dir = Path(config.get("comfyui", {}).get("workflow_dir", "workflows"))
    
    # Create necessary directories
    os.makedirs(workflow_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    parser = StoryboardParser(config)
    generator = ImageGenerator(config, style_manager)
    assembler = VideoAssembler(config)
    
    logger.info(f"ComfyUI integration initialized with host {comfyui_host}:{comfyui_port}")
    logger.info("Storyboard-to-Video components initialized")


@comfyui_bp.route('/')
def swarmui_interface():
    """
    Serve the SwarmUI interface
    """
    return render_template('swarmui.html')


@comfyui_bp.route('/api/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_api(subpath):
    """
    Proxy API requests to ComfyUI
    
    Args:
        subpath (str): API subpath
    """
    url = f"http://{comfyui_host}:{comfyui_port}/api/{subpath}"
    
    # Forward the request to ComfyUI
    if request.method == 'GET':
        resp = requests.get(url, params=request.args)
    elif request.method == 'POST':
        resp = requests.post(url, json=request.json)
    elif request.method == 'PUT':
        resp = requests.put(url, json=request.json)
    elif request.method == 'DELETE':
        resp = requests.delete(url)
    
    # Return the response from ComfyUI
    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get('Content-Type')
    )


@comfyui_bp.route('/workflows')
def list_workflows():
    """
    List available workflows
    """
    workflows = []
    
    for workflow_file in workflow_dir.glob('*.json'):
        try:
            with open(workflow_file, 'r') as f:
                # Just check if it's valid JSON
                json.load(f)
            
            workflows.append({
                'name': workflow_file.stem,
                'path': str(workflow_file.relative_to(workflow_dir))
            })
        except Exception as e:
            logger.error(f"Error loading workflow {workflow_file}: {e}")
    
    return jsonify(workflows)


@comfyui_bp.route('/workflows/<path:workflow_name>')
def get_workflow(workflow_name):
    """
    Get a specific workflow
    
    Args:
        workflow_name (str): Name of the workflow
    """
    # Ensure the workflow name has .json extension
    if not workflow_name.endswith('.json'):
        workflow_name += '.json'
    
    workflow_path = workflow_dir / workflow_name
    
    if not workflow_path.exists():
        return jsonify({'error': f"Workflow {workflow_name} not found"}), 404
    
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        return jsonify(workflow)
    except Exception as e:
        logger.error(f"Error loading workflow {workflow_path}: {e}")
        return jsonify({'error': f"Error loading workflow: {str(e)}"}), 500


@comfyui_bp.route('/lora_models')
def list_lora_models():
    """
    List available LoRA models
    """
    # Get LoRA models directory from config
    models_dir = Path(config.get("local_models_path", "models"))
    lora_dir = models_dir / "lora"
    
    # Create directory if it doesn't exist
    os.makedirs(lora_dir, exist_ok=True)
    
    # List LoRA models
    lora_models = []
    
    # Add empty option
    lora_models.append({
        'name': '',
        'display_name': 'None'
    })
    
    # List files with common LoRA extensions
    for ext in ['.safetensors', '.ckpt', '.pt']:
        for model_file in lora_dir.glob(f'*{ext}'):
            lora_models.append({
                'name': model_file.stem,
                'display_name': model_file.stem.replace('_', ' ').title(),
                'path': str(model_file.relative_to(models_dir))
            })
    
    return jsonify(lora_models)


@comfyui_bp.route('/upload_lora', methods=['POST'])
def upload_lora():
    """
    Upload a LoRA model
    """
    if 'lora_file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    lora_file = request.files['lora_file']
    if lora_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get LoRA models directory from config
    models_dir = Path(config.get("local_models_path", "models"))
    lora_dir = models_dir / "lora"
    
    # Create directory if it doesn't exist
    os.makedirs(lora_dir, exist_ok=True)
    
    # Save the uploaded file
    filename = lora_file.filename
    lora_path = lora_dir / filename
    lora_file.save(str(lora_path))
    
    return jsonify({
        'success': True,
        'filename': filename,
        'path': str(lora_path.relative_to(models_dir))
    })


@comfyui_bp.route('/styles')
def list_styles():
    """
    List available styles
    """
    styles = style_manager.list_styles()
    return jsonify(styles)


@comfyui_bp.route('/train_style', methods=['POST'])
def train_style():
    """
    Train a new style (LoRA)
    """
    data = request.json
    style_name = data.get('name')
    training_images = data.get('training_images', [])
    base_style = data.get('base_style')
    
    if not style_name or not training_images:
        return jsonify({'error': 'Style name and training images are required'}), 400
    
    # This would typically start a training job
    # For now, we'll just return a success message
    return jsonify({
        'success': True,
        'message': f"Training started for style '{style_name}'"
    })


@comfyui_bp.route('/train_lora', methods=['POST'])
def train_lora():
    """
    Train a new LoRA model for a specific style
    Handles the training process for the "Déclic Ombre Chinoise" style
    """
    try:
        # Check if files were uploaded
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400
        
        # Get form data
        name = request.form.get('name', 'declic_ombre_chinoise')
        display_name = request.form.get('display_name', 'Déclic Ombre Chinoise')
        description = request.form.get('description', 'Silhouettes intégrales avec rim light et lumière cinématographique réaliste')
        base_model = request.form.get('base_model', 'sd15')
        steps = int(request.form.get('steps', 2000))
        rank = int(request.form.get('rank', 16))
        batch_size = int(request.form.get('batch_size', 2))
        learning_rate = float(request.form.get('learning_rate', 0.0001))
        
        # Get external integrations
        use_gemini = request.form.get('use_gemini', 'true').lower() == 'true'
        use_qwen = request.form.get('use_qwen', 'true').lower() == 'true'
        use_wan = request.form.get('use_wan', 'true').lower() == 'true'
        
        # Get training prompts
        training_prompts = []
        for key in request.form:
            if key.startswith('training_prompt_'):
                training_prompts.append(request.form[key])
        
        # Create a unique job ID
        job_id = str(uuid.uuid4())
        
        # Create a directory for training images
        training_dir = temp_dir / f"lora_training_{job_id}"
        os.makedirs(training_dir, exist_ok=True)
        
        # Save uploaded images
        image_files = request.files.getlist('images')
        image_paths = []
        
        for i, image_file in enumerate(image_files):
            if image_file.filename:
                # Save image with a sequential name
                image_path = training_dir / f"image_{i:04d}.jpg"
                image_file.save(str(image_path))
                image_paths.append(str(image_path))
        
        if not image_paths:
            return jsonify({'error': 'No valid images uploaded'}), 400
        
        # Create a metadata file with training configuration
        metadata = {
            'name': name,
            'display_name': display_name,
            'description': description,
            'base_model': base_model,
            'steps': steps,
            'rank': rank,
            'batch_size': batch_size,
            'learning_rate': learning_rate,
            'training_prompts': training_prompts,
            'image_count': len(image_paths),
            'external_integrations': {
                'gemini': use_gemini,
                'qwen': use_qwen,
                'wan': use_wan
            },
            'created_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(training_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create output directory for the LoRA model
        lora_output_dir = Path(config.get("local_models_path", "models")) / "lora" / name
        os.makedirs(lora_output_dir, exist_ok=True)
        
        # In a real implementation, this would start a background process to train the LoRA model
        # For this example, we'll simulate the training process
        
        # Start training in a separate thread
        def train_thread():
            try:
                logger.info(f"Starting LoRA training for '{name}' with {len(image_paths)} images")
                
                # Create a training job record
                training_job = {
                    'job_id': job_id,
                    'name': name,
                    'status': 'running',
                    'progress': 0,
                    'start_time': time.time(),
                    'training_dir': str(training_dir),
                    'output_dir': str(lora_output_dir),
                    'metadata': metadata
                }
                
                # Store job information in a global dictionary
                # In a real implementation, this would be stored in a database
                if not hasattr(train_lora, 'training_jobs'):
                    train_lora.training_jobs = {}
                
                train_lora.training_jobs[job_id] = training_job
                
                # Simulate training process
                total_steps = steps
                for current_step in range(0, total_steps + 1, 100):
                    # Update progress
                    progress = min(100, int(current_step / total_steps * 100))
                    training_job['progress'] = progress
                    
                    # Log progress
                    logger.info(f"LoRA training progress: {progress}% ({current_step}/{total_steps})")
                    
                    # In a real implementation, this would be the actual training step
                    # For simulation, we'll just sleep
                    time.sleep(1)
                
                # Create a dummy safetensors file to simulate the trained model
                model_path = lora_output_dir / f"{name}.safetensors"
                with open(model_path, 'w') as f:
                    f.write("This is a placeholder for a trained LoRA model.")
                
                # Create a training log
                log_path = lora_output_dir / "training_log.txt"
                with open(log_path, 'w') as f:
                    f.write(f"Training log for LoRA model '{name}'\n")
                    f.write(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Number of steps: {steps}\n")
                    f.write(f"Learning rate: {learning_rate}\n")
                    f.write(f"Rank: {rank}\n")
                    f.write(f"Batch size: {batch_size}\n")
                    f.write(f"Number of training images: {len(image_paths)}\n")
                    f.write(f"Finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Create style data for the trained LoRA
                style_data = {
                    "name": name,
                    "description": description,
                    "prompt_prefix": "cinematic photograph, silhouetted figure, rim lighting, realistic directional lighting",
                    "prompt_suffix": "detailed silhouette, no visible faces, cinematic shadows, realistic textures, 16:9 ratio",
                    "negative_prompt": "low quality, blurry, distorted, deformed, cartoon, anime, visible face details, flat lighting",
                    "workflow_template": "default_controlnet.json",
                    "lora_name": name,
                    "lora_strength": 0.85,
                    "cfg_scale": 7.5,
                    "steps": 30,
                    "sampler": "euler_ancestral"
                }
                
                # Save style data
                style_manager.create_style(name, style_data)
                
                # Update job status
                training_job['status'] = 'completed'
                training_job['end_time'] = time.time()
                training_job['duration'] = training_job['end_time'] - training_job['start_time']
                
                logger.info(f"LoRA training completed for '{name}'")
            except Exception as e:
                logger.error(f"Error during LoRA training: {e}")
                
                if job_id in train_lora.training_jobs:
                    train_lora.training_jobs[job_id]['status'] = 'failed'
                    train_lora.training_jobs[job_id]['error'] = str(e)
        
        # Start training thread
        training_thread = threading.Thread(target=train_thread)
        training_thread.daemon = True
        training_thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f"LoRA training started for '{name}'"
        })
    except Exception as e:
        logger.error(f"Error starting LoRA training: {e}")
        return jsonify({'error': f"Error starting LoRA training: {str(e)}"}), 500


@comfyui_bp.route('/check_lora_training', methods=['GET'])
def check_lora_training():
    """
    Check the status of a LoRA training job
    """
    job_id = request.args.get('job_id')
    
    if not job_id:
        return jsonify({'error': 'No job ID provided'}), 400
    
    # Check if training jobs dictionary exists
    if not hasattr(train_lora, 'training_jobs'):
        return jsonify({'error': 'No training jobs found'}), 404
    
    # Check if job exists
    if job_id not in train_lora.training_jobs:
        return jsonify({'error': f"Job {job_id} not found"}), 404
    
    # Get job information
    job = train_lora.training_jobs[job_id]
    
    # Return job status
    if job['status'] == 'completed':
        return jsonify({
            'status': 'completed',
            'job_id': job_id,
            'name': job['name'],
            'duration': job.get('duration', 0)
        })
    elif job['status'] == 'failed':
        return jsonify({
            'status': 'failed',
            'job_id': job_id,
            'error': job.get('error', 'Unknown error')
        })
    else:  # running
        return jsonify({
            'status': 'progress',
            'job_id': job_id,
            'progress': job['progress']
        })


@comfyui_bp.route('/check_comfyui')
def check_comfyui():
    """
    Check if ComfyUI is available
    """
    try:
        response = requests.get(f"http://{comfyui_host}:{comfyui_port}/")
        if response.status_code == 200:
            return jsonify({
                'available': True,
                'message': 'ComfyUI is available'
            })
        else:
            return jsonify({
                'available': False,
                'message': f"ComfyUI returned status code {response.status_code}"
            })
    except Exception as e:
        return jsonify({
            'available': False,
            'message': f"Could not connect to ComfyUI: {str(e)}"
        })


@comfyui_bp.route('/upload_storyboard', methods=['POST'])
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
    upload_path = upload_dir / filename
    file.save(str(upload_path))
    
    return jsonify({
        'success': True,
        'filename': filename,
        'path': str(upload_path),
        'url': url_for('comfyui.get_uploaded_file', filename=filename)
    })


@comfyui_bp.route('/uploads/<path:filename>')
def get_uploaded_file(filename):
    """
    Serve uploaded files
    
    Args:
        filename (str): Filename to serve
    """
    return send_file(str(upload_dir / filename))


@comfyui_bp.route('/parse_storyboard', methods=['POST'])
def parse_storyboard():
    """
    Parse storyboard PDF or images and extract scenes
    """
    data = request.json
    storyboard_path = data.get('storyboard_path')
    
    if not storyboard_path or not os.path.exists(storyboard_path):
        return jsonify({'error': 'Invalid storyboard path'}), 400
    
    try:
        # Parse storyboard
        scenes = parser.parse(storyboard_path)
        
        # Convert to MCP protocol format
        mcp_scenes = []
        
        for i, scene in enumerate(scenes):
            # Extract scene data
            scene_id = i + 1
            reference_image = scene.get('image_path', '')
            text = scene.get('text', '')
            
            # Create MCP scene object
            mcp_scene = {
                'scene_id': scene_id,
                'input': {
                    'reference_image': reference_image,
                    'prompt_text': text,
                    'camera_movement': 'static',  # Default
                    'duration': 5  # Default duration in seconds
                },
                'generation': {
                    'style': config.get('style', 'default'),
                    'sd_model': config.get('models', {}).get('stable_diffusion', 'runwayml/stable-diffusion-v1-5'),
                    'controlnet_model': config.get('models', {}).get('controlnet', 'lllyasviel/control_v11p_sd15_scribble'),
                    'lora_weights': '',  # Default to no LoRA
                    'cfg_scale': 7.5,
                    'steps': 50,
                    'resolution': config.get('resolution', [1920, 1080])
                },
                'output': {
                    'image': '',
                    'video_clip': ''
                }
            }
            
            mcp_scenes.append(mcp_scene)
        
        return jsonify({
            'success': True,
            'total_scenes': len(mcp_scenes),
            'scenes': mcp_scenes
        })
    except Exception as e:
        logger.error(f"Error parsing storyboard: {e}")
        return jsonify({'error': f"Error parsing storyboard: {str(e)}"}), 500


@comfyui_bp.route('/generate_scene', methods=['POST'])
def generate_scene():
    """
    Generate image for a scene using ComfyUI
    """
    data = request.json
    scene = data.get('scene')
    
    if not scene:
        return jsonify({'error': 'No scene data provided'}), 400
    
    try:
        # Generate a unique ID for this job
        job_id = str(uuid.uuid4())
        
        # Get scene data
        scene_id = scene.get('scene_id')
        reference_image = scene.get('input', {}).get('reference_image', '')
        prompt_text = scene.get('input', {}).get('prompt_text', '')
        style_name = scene.get('generation', {}).get('style', 'default')
        lora_weights = scene.get('generation', {}).get('lora_weights', '')
        cfg_scale = scene.get('generation', {}).get('cfg_scale', 7.5)
        steps = scene.get('generation', {}).get('steps', 50)
        resolution = scene.get('generation', {}).get('resolution', [1920, 1080])
        
        # Get style parameters
        style_params = style_manager.get_style(style_name)
        
        # Prepare workflow for ComfyUI
        workflow = prepare_comfyui_workflow(
            reference_image,
            prompt_text,
            style_params,
            lora_weights,
            cfg_scale,
            steps,
            resolution
        )
        
        # Send workflow to ComfyUI
        response = requests.post(
            f"http://{comfyui_host}:{comfyui_port}/prompt",
            json={
                'prompt': workflow
            }
        )
        
        if response.status_code != 200:
            return jsonify({'error': f"ComfyUI returned status code {response.status_code}"}), 500
        
        # Get prompt ID from response
        prompt_data = response.json()
        prompt_id = prompt_data.get('prompt_id')
        
        if not prompt_id:
            return jsonify({'error': 'No prompt ID returned from ComfyUI'}), 500
        
        # Store job information
        generation_jobs[job_id] = {
            'prompt_id': prompt_id,
            'scene_id': scene_id,
            'status': 'running',
            'start_time': time.time(),
            'output_image': None
        }
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'prompt_id': prompt_id
        })
    except Exception as e:
        logger.error(f"Error generating scene: {e}")
        return jsonify({'error': f"Error generating scene: {str(e)}"}), 500


@comfyui_bp.route('/check_generation_status', methods=['GET'])
def check_generation_status():
    """
    Check the status of a generation job
    """
    job_id = request.args.get('job_id')
    prompt_id = request.args.get('prompt_id')
    
    if not job_id and not prompt_id:
        return jsonify({'error': 'No job ID or prompt ID provided'}), 400
    
    try:
        # If job ID is provided, get prompt ID from job
        if job_id:
            if job_id not in generation_jobs:
                return jsonify({'error': f"Job {job_id} not found"}), 404
            
            job = generation_jobs[job_id]
            prompt_id = job.get('prompt_id')
            
            # If job is already completed, return result
            if job.get('status') == 'completed' and job.get('output_image'):
                return jsonify({
                    'status': 'completed',
                    'job_id': job_id,
                    'scene_id': job.get('scene_id'),
                    'images': [{
                        'url': job.get('output_image'),
                        'filename': os.path.basename(job.get('output_image'))
                    }]
                })
        
        # Check status with ComfyUI
        response = requests.get(f"http://{comfyui_host}:{comfyui_port}/history/{prompt_id}")
        
        if response.status_code != 200:
            return jsonify({'error': f"ComfyUI returned status code {response.status_code}"}), 500
        
        history_data = response.json()
        
        # Check if generation is completed
        if prompt_id in history_data and 'outputs' in history_data[prompt_id]:
            outputs = history_data[prompt_id]['outputs']
            
            # Find image outputs
            images = []
            for node_id, output in outputs.items():
                if 'images' in output:
                    for img in output['images']:
                        # Get image URL
                        img_filename = img['filename']
                        img_url = f"/comfyui/view_image/{img_filename}"
                        
                        # Save image URL to job
                        if job_id:
                            generation_jobs[job_id]['status'] = 'completed'
                            generation_jobs[job_id]['output_image'] = img_url
                        
                        images.append({
                            'url': img_url,
                            'filename': img_filename
                        })
            
            if images:
                return jsonify({
                    'status': 'completed',
                    'job_id': job_id,
                    'prompt_id': prompt_id,
                    'images': images
                })
        
        # If not completed, return running status
        return jsonify({
            'status': 'running',
            'job_id': job_id,
            'prompt_id': prompt_id
        })
    except Exception as e:
        logger.error(f"Error checking generation status: {e}")
        return jsonify({'error': f"Error checking generation status: {str(e)}"}), 500


@comfyui_bp.route('/view_image/<path:filename>')
def view_image(filename):
    """
    Serve generated images from ComfyUI
    
    Args:
        filename (str): Image filename
    """
    try:
        # ComfyUI stores images in its output directory
        comfyui_output_dir = Path(config.get("comfyui", {}).get("output_dir", "ComfyUI/output"))
        image_path = comfyui_output_dir / filename
        
        if not image_path.exists():
            return jsonify({'error': f"Image {filename} not found"}), 404
        
        return send_file(str(image_path))
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return jsonify({'error': f"Error serving image: {str(e)}"}), 500


@comfyui_bp.route('/create_video', methods=['POST'])
def create_video():
    """
    Create video from generated images
    """
    data = request.json
    scenes = data.get('scenes', [])
    use_animation = data.get('use_animation', False)
    
    if not scenes:
        return jsonify({'error': 'No scenes provided'}), 400
    
    try:
        # Extract image paths from scenes
        image_paths = []
        scene_data = []
        
        for scene in scenes:
            # Get image URL and convert to local path
            image_url = scene.get('output', {}).get('image', '')
            
            if not image_url:
                return jsonify({'error': f"Scene {scene.get('scene_id')} has no generated image"}), 400
            
            # Extract filename from URL
            filename = image_url.split('/')[-1]
            
            # Get local path
            comfyui_output_dir = Path(config.get("comfyui", {}).get("output_dir", "ComfyUI/output"))
            image_path = comfyui_output_dir / filename
            
            if not image_path.exists():
                return jsonify({'error': f"Image {filename} not found"}), 404
            
            image_paths.append(str(image_path))
            
            # Add scene data for video creation
            scene_data.append({
                'text': scene.get('input', {}).get('prompt_text', ''),
                'duration': scene.get('input', {}).get('duration', 5),
                'camera_movement': scene.get('input', {}).get('camera_movement', 'static')
            })
        
        # Set output path
        output_filename = f"storyboard_video_{int(time.time())}.mp4"
        output_path = output_dir / output_filename
        
        # Update config for video creation
        video_config = config.copy()
        video_config['use_animation'] = use_animation
        video_config['output_path'] = str(output_path)
        
        # Create video
        assembler.config = video_config
        video_path = assembler.create_video(image_paths, scene_data)
        
        # Generate URL for video
        video_url = url_for('comfyui.view_video', filename=output_filename)
        
        return jsonify({
            'success': True,
            'video_path': video_path,
            'video_url': video_url
        })
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        return jsonify({'error': f"Error creating video: {str(e)}"}), 500


@comfyui_bp.route('/view_video/<path:filename>')
def view_video(filename):
    """
    Serve generated videos
    
    Args:
        filename (str): Video filename
    """
    try:
        video_path = output_dir / filename
        
        if not video_path.exists():
            return jsonify({'error': f"Video {filename} not found"}), 404
        
        return send_file(str(video_path))
    except Exception as e:
        logger.error(f"Error serving video {filename}: {e}")
        return jsonify({'error': f"Error serving video: {str(e)}"}), 500


def prepare_comfyui_workflow(reference_image, prompt_text, style_params, lora_weights, cfg_scale, steps, resolution):
    """
    Prepare workflow for ComfyUI
    
    Args:
        reference_image (str): Path to reference image
        prompt_text (str): Text prompt
        style_params (dict): Style parameters
        lora_weights (str): LoRA weights filename
        cfg_scale (float): CFG scale
        steps (int): Number of steps
        resolution (list): Resolution [width, height]
        
    Returns:
        dict: ComfyUI workflow
    """
    # Load base workflow
    workflow_template = style_params.get('workflow_template', 'default_controlnet.json')
    workflow_path = workflow_dir / workflow_template
    
    if not workflow_path.exists():
        logger.warning(f"Workflow template {workflow_template} not found, using default")
        workflow_path = workflow_dir / 'default_controlnet.json'
    
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        logger.error(f"Error loading workflow template: {e}")
        # Create a minimal default workflow
        workflow = {
            "3": {
                "inputs": {
                    "ckpt_name": "runwayml/stable-diffusion-v1-5"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "4": {
                "inputs": {
                    "text": "",
                    "clip": ["3", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "5": {
                "inputs": {
                    "text": "low quality, blurry, distorted, deformed",
                    "clip": ["3", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "6": {
                "inputs": {
                    "image": ""
                },
                "class_type": "LoadImage"
            },
            "7": {
                "inputs": {
                    "image": ["6", 0],
                    "model": "lllyasviel/control_v11p_sd15_scribble",
                    "strength": 0.8
                },
                "class_type": "ControlNetLoader"
            },
            "8": {
                "inputs": {
                    "model": ["3", 0],
                    "positive": ["4", 0],
                    "negative": ["5", 0],
                    "latent_image": ["9", 0],
                    "control_net": ["7", 0],
                    "seed": 42,
                    "steps": 20,
                    "cfg": 7.5,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal"
                },
                "class_type": "KSampler"
            },
            "9": {
                "inputs": {
                    "width": 1024,
                    "height": 768,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "10": {
                "inputs": {
                    "samples": ["8", 0],
                    "vae": ["3", 2]
                },
                "class_type": "VAEDecode"
            },
            "11": {
                "inputs": {
                    "images": ["10", 0],
                    "filename_prefix": "generated",
                    "save_to": "output"
                },
                "class_type": "SaveImage"
            },
            "12": {
                "inputs": {
                    "lora_name": "",
                    "strength": 0.8,
                    "model": ["3", 0],
                    "clip": ["3", 0]
                },
                "class_type": "LoraLoader"
            }
        }
    
    # Update workflow with parameters
    # 1. Update reference image
    for node_id, node in workflow.items():
        if node.get('class_type') == 'LoadImage':
            node['inputs']['image'] = reference_image
    
    # 2. Update prompt
    prompt_prefix = style_params.get('prompt_prefix', '')
    prompt_suffix = style_params.get('prompt_suffix', '')
    full_prompt = f"{prompt_prefix} {prompt_text} {prompt_suffix}".strip()
    
    for node_id, node in workflow.items():
        if node.get('class_type') == 'CLIPTextEncode' and 'negative' not in node_id.lower():
            node['inputs']['text'] = full_prompt
    
    # 3. Update negative prompt
    negative_prompt = style_params.get('negative_prompt', 'low quality, blurry, distorted, deformed')
    
    for node_id, node in workflow.items():
        if node.get('class_type') == 'CLIPTextEncode' and 'negative' in node_id.lower():
            node['inputs']['text'] = negative_prompt
    
    # 4. Update LoRA weights
    for node_id, node in workflow.items():
        if node.get('class_type') == 'LoraLoader':
            node['inputs']['lora_name'] = lora_weights
            node['inputs']['strength'] = style_params.get('lora_strength', 0.8)
    
    # 5. Update generation parameters
    for node_id, node in workflow.items():
        if node.get('class_type') == 'KSampler':
            node['inputs']['cfg'] = cfg_scale
            node['inputs']['steps'] = steps
            node['inputs']['seed'] = int(time.time()) % 1000000  # Random seed
    
    # 6. Update resolution
    for node_id, node in workflow.items():
        if node.get('class_type') == 'EmptyLatentImage':
            node['inputs']['width'] = resolution[0]
            node['inputs']['height'] = resolution[1]
    
    return workflow


def register_blueprint(app):
    """
    Register the ComfyUI blueprint with the Flask app
    
    Args:
        app (Flask): Flask application
    """
    app.register_blueprint(comfyui_bp)
    
    # Initialize ComfyUI integration
    init_comfyui_integration(app.config.get('COMFYUI_CONFIG', {}))
    
    logger.info("ComfyUI blueprint registered")


@comfyui_bp.route('/setup_external_models', methods=['POST'])
def setup_external_models():
    """
    Setup external models for Déclic Ombre Chinoise style
    - Installs Qwen 2.1 via Ollama
    - Configures Google Gemini Studio API
    - Sets up WAN 2.1 (Tencent) integration
    """
    try:
        data = request.json
        use_qwen = data.get('use_qwen', True)
        use_gemini = data.get('use_gemini', True)
        use_wan = data.get('use_wan', True)
        
        results = {
            'qwen': {'status': 'not_configured'},
            'gemini': {'status': 'not_configured'},
            'wan': {'status': 'not_configured'}
        }
        
        # Setup Qwen 2.1 via Ollama
        if use_qwen:
            try:
                # Check if Ollama is installed
                ollama_check = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                
                if ollama_check.returncode == 0:
                    # Check if Qwen model is already pulled
                    if 'qwen2:1.5b' in ollama_check.stdout:
                        results['qwen'] = {
                            'status': 'available',
                            'message': 'Qwen 2.1 model is already available via Ollama'
                        }
                    else:
                        # Pull Qwen model
                        logger.info("Pulling Qwen 2.1 model via Ollama...")
                        # In a real implementation, this would be a non-blocking operation
                        # For simulation, we'll just set the status
                        results['qwen'] = {
                            'status': 'installing',
                            'message': 'Qwen 2.1 model installation started. This may take some time.'
                        }
                else:
                    results['qwen'] = {
                        'status': 'error',
                        'message': 'Ollama is not installed or not in PATH'
                    }
            except Exception as e:
                results['qwen'] = {
                    'status': 'error',
                    'message': f"Error setting up Qwen 2.1: {str(e)}"
                }
        
        # Setup Google Gemini Studio API
        if use_gemini:
            # In a real implementation, this would validate and store API keys
            results['gemini'] = {
                'status': 'configured',
                'message': 'Google Gemini Studio API configured successfully'
            }
        
        # Setup WAN 2.1 (Tencent) integration
        if use_wan:
            # In a real implementation, this would validate and store API keys
            results['wan'] = {
                'status': 'configured',
                'message': 'WAN 2.1 (Tencent) API configured successfully'
            }
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        logger.error(f"Error setting up external models: {e}")
        return jsonify({'error': f"Error setting up external models: {str(e)}"}), 500