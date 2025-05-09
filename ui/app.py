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
import asyncio
import uuid
from pathlib import Path
from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for, current_app, send_from_directory
from werkzeug.utils import secure_filename

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsing.parser import StoryboardParser
from generation.generator import ImageGenerator
from styles.manager import StyleManager
from video.assembler import VideoAssembler
from utils.config import load_config, save_config
from utils.api_manager import APIManager
from utils.model_manager import ModelManager
from utils.cache_manager import CacheManager
from utils.security import SecurityManager

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
app.config['UPLOAD_FOLDER'] = Path('uploads')
app.config['RESULT_FOLDER'] = Path('results')
app.config['PROJECTS_BASE_DIR'] = Path('projects') # Base directory for projects

# Global dictionary to track running generation tasks
# Key: task_id (str), Value: dict with status, progress, message, result_path, etc.
background_tasks = {}

@app.before_request
def ensure_managers_initialized():
    # This check ensures managers are available for every request
    # It relies on start_web_app having populated app.config
    required_managers = ['config', 'api_manager', 'model_manager', 'cache_manager', 'security_manager']
    if not all(mgr in current_app.config for mgr in required_managers):
        # This should ideally not happen if started via startup.py
        logger.critical("Managers not initialized in Flask app config!")
        # You might want to return an error response here
        return jsonify({"error": "Application not properly initialized"}), 500

@app.route('/')
def index():
    """
    Render the main page
    """
    try:
        style_manager = current_app.config['style_manager']
        config = current_app.config['config']
        styles = style_manager.list_styles() if style_manager else []
        # Get status of recent/running tasks (simplified view for index)
        # Maybe show the latest task or a summary
        latest_task_id = None
        latest_task_status = {"running": False, "message": "Ready"} # Default
        if background_tasks:
            # Find the most recently started task (requires storing timestamp)
            # Simple approach: just take the last one added (not reliable)
            latest_task_id = list(background_tasks.keys())[-1] # Example: get latest ID
            latest_task_status = background_tasks[latest_task_id]

        # TODO: Add project listing/selection here
        projects = list_projects()
    
    except Exception as e:
        logger.error(f"Error rendering index page: {e}", exc_info=True)
        return f"An internal error occurred: {e}", 500

    return render_template(
        'index.html',
        styles=styles,
        status=latest_task_status,
        task_id=latest_task_id,
        config=config,
        projects=projects
    )

# --- Project Management --- 
def get_project_dir(project_name):
    """ Returns the sanitized directory path for a project. """
    if not project_name or '.' in project_name or '/' in project_name or '\\' in project_name:
         raise ValueError("Invalid project name")
    return app.config['PROJECTS_BASE_DIR'] / secure_filename(project_name)

def list_projects():
    """ Returns a list of existing project names. """
    base_dir = app.config['PROJECTS_BASE_DIR']
    projects = []
    if base_dir.exists():
        for item in base_dir.iterdir():
            if item.is_dir():
                 # Check for a marker file or config to confirm it's a project?
                 projects.append({"name": item.name})
    return projects

@app.route('/projects', methods=['GET'])
def get_projects():
     return jsonify(list_projects())

@app.route('/projects', methods=['POST'])
def create_project():
    try:
        project_name = request.json.get('name')
        if not project_name:
            return jsonify({"error": "Project name required"}), 400
        project_dir = get_project_dir(project_name)
        if project_dir.exists():
            return jsonify({"error": "Project already exists"}), 409
        os.makedirs(project_dir / 'uploads', exist_ok=True)
        os.makedirs(project_dir / 'generated', exist_ok=True)
        os.makedirs(project_dir / 'results', exist_ok=True)
        os.makedirs(project_dir / 'temp', exist_ok=True)
        logger.info(f"Created project '{project_name}' at {project_dir}")
        return jsonify({"success": True, "name": project_name, "path": str(project_dir)}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating project '{project_name}': {e}", exc_info=True)
        return jsonify({"error": "Failed to create project"}), 500

# --- Uploads within Project Context --- 
@app.route('/projects/<project_name>/upload', methods=['POST'])
def upload_storyboard(project_name):
    """
    Handle storyboard upload for a specific project.
    """
    try:
        project_dir = get_project_dir(project_name)
        if not project_dir.exists():
            return jsonify({"error": "Project not found"}), 404

        upload_folder = project_dir / 'uploads'

        if 'storyboard' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['storyboard']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        upload_path = upload_folder / filename
        file.save(upload_path)
        logger.info(f"Uploaded '{filename}' to project '{project_name}'")
        return jsonify({
            'success': True,
            'filename': filename,
            'path': str(upload_path) # Return path relative to project?
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error uploading to project '{project_name}': {e}", exc_info=True)
        return jsonify({"error": "File upload failed"}), 500


# Make generate async
@app.route('/projects/<project_name>/generate', methods=['POST'])
async def generate(project_name):
    """
    Start the generation process for a specific project.
    """
    global background_tasks

    try:
        project_dir = get_project_dir(project_name)
        if not project_dir.exists():
            return jsonify({"error": "Project not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Get managers from app context
    config = current_app.config['config']
    api_manager = current_app.config['api_manager']
    model_manager = current_app.config['model_manager']
    cache_manager = current_app.config['cache_manager']
    security_manager = current_app.config['security_manager']
    style_manager = current_app.config['style_manager']
    # Create component instances specific to this request/project if needed,
    # or reuse if they are stateless and configured via managers.
    try:
        # For now, assume they can be created here using config + managers
        parser = StoryboardParser(config, cache_manager=cache_manager)
        generator = ImageGenerator(config, style_manager, model_manager, api_manager, cache_manager, security_manager)
        assembler = VideoAssembler(config, cache_manager=cache_manager)

        # Get parameters from request
        data = request.json
        storyboard_filename = data.get('storyboard_filename') # Filename within project uploads
        style_name = data.get('style', config.get("style", "default"))
        use_cloud = data.get('use_cloud', config.get("use_cloud", False))
        output_filename = data.get('output_filename', f"{project_name}_video_{int(time.time())}.mp4")
        
        # Validate parameters
        if not storyboard_filename:
            return jsonify({'error': 'Storyboard filename required'}), 400

        storyboard_path = project_dir / 'uploads' / secure_filename(storyboard_filename)
        if not storyboard_path.exists():
            return jsonify({'error': f'Storyboard file {storyboard_filename} not found in project {project_name}'}), 404

        # --- Task Management --- 
        task_id = str(uuid.uuid4())
        background_tasks[task_id] = {
            'status': 'queued',
            'progress': 0,
            'total': 0,
            'current_scene': 0,
            'message': 'Generation queued',
            'result_video': None,
            'project_name': project_name,
            'start_time': time.time()
        }

        # Define project-specific paths for this task
        project_config = config.copy() # Use a copy to avoid modifying global config
        project_config["project_dir"] = project_dir # Store project path
        project_config["temp_dir"] = project_dir / 'temp'
        project_config["output_path"] = project_dir / 'results' / secure_filename(output_filename)
        project_config["style"] = style_name
        project_config["use_cloud"] = use_cloud
        # Ensure these paths exist
        os.makedirs(project_config["temp_dir"], exist_ok=True)
        os.makedirs(project_config["output_path"].parent, exist_ok=True)

        logger.info(f"Starting generation task {task_id} for project '{project_name}'...")
        # Start generation in background using asyncio
        asyncio.create_task(run_generation_pipeline(
            task_id,
            project_dir,
            parser,
            generator,
            assembler,
            storyboard_path,
            project_config
        ))

        return jsonify({'success': True, 'message': 'Generation started', 'task_id': task_id})
    except Exception as e:
        logger.error(f"Error starting generation for project '{project_name}': {e}", exc_info=True)
        return jsonify({"error": "Failed to start generation"}), 500

async def run_generation_pipeline(task_id, project_dir, parser, generator, assembler, storyboard_path, config):
    """ The actual pipeline logic, runs in background. NO VIDEO ASSEMBLY YET """
    global background_tasks
    # Log the start with task_id
    logger.info(f"[Task {task_id}] Starting pipeline for storyboard: {storyboard_path}")
    try:
        # 1. Parse (get scene data including original image paths)
        # --- PARSE THE STORYBOARD HERE --- 
        background_tasks[task_id]['status'] = 'parsing'
        background_tasks[task_id]['message'] = 'Parsing storyboard...'
        logger.info(f"[Task {task_id}] Parsing storyboard...")
        scenes = parser.parse(storyboard_path)
        if not scenes:
            logger.error(f"[Task {task_id}] Parsing failed or returned no scenes.")
            raise ValueError("Parsing failed or storyboard is empty.")
        
        logger.info(f"[Task {task_id}] Parsing complete. Found {len(scenes)} scenes.")

        # --- STORE PARSED SCENES IN TASK DATA --- 
        background_tasks[task_id]['scenes'] = scenes
        background_tasks[task_id]['total'] = len(scenes)

        if not scenes:
             raise ValueError("Scene data not found in task.")
        
        background_tasks[task_id]['status'] = 'generating'
        total_scenes = len(scenes)
        generated_image_paths = [None] * total_scenes # Initialize list for results

        # 2. Generate images sequentially (can be parallelized later)
        for i, scene_data in enumerate(scenes):
             current_scene_num = i + 1
             background_tasks[task_id]['message'] = f'Generating image for scene {current_scene_num}/{total_scenes}'
             background_tasks[task_id]['progress'] = i # Progress based on starting scene
             background_tasks[task_id]['current_scene'] = current_scene_num
             if scenes[i]: scenes[i]['status'] = 'generating' # Update scene status

             logger.info(f"Task {task_id}: Generating scene {i}")
             # Ensure paths are strings
             original_img_path = str(scene_data.get('image', ''))
             scene_text = scene_data.get('text', '')
             
             if not original_img_path or not Path(original_img_path).exists():
                 logger.error(f"Task {task_id}: Original image path invalid or missing for scene {i}: {original_img_path}")
                 if scenes[i]: scenes[i]['status'] = 'error'
                 if scenes[i]: scenes[i]['error'] = 'Original image missing'
                 continue # Skip this scene

             try:
                 # Call the main generator's generate method
                 # Pass style from the config used for this task
                 generated_path = await generator.generate(
                     original_img_path,
                     scene_text,
                     style_name=config.get('style', 'default'), 
                     scene_index=i
                 )
                 
                 if generated_path:
                     generated_image_paths[i] = generated_path
                     # --- IMPORTANT: Update the scene data with the path --- 
                     if scenes[i]: scenes[i]['generated_image_path'] = generated_path 
                     if scenes[i]: scenes[i]['status'] = 'complete'
                     logger.info(f"Task {task_id}: Scene {i} generated: {generated_path}")
                 else:
                      logger.error(f"Task {task_id}: Failed to generate image for scene {i}")
                      if scenes[i]: scenes[i]['status'] = 'error'
                      if scenes[i]: scenes[i]['error'] = 'Generation failed'
             except Exception as scene_e:
                 logger.error(f"Task {task_id}: Error during generation for scene {i}: {scene_e}", exc_info=True)
                 if scenes[i]: scenes[i]['status'] = 'error'
                 if scenes[i]: scenes[i]['error'] = f'Error: {scene_e}'

        # 3. Update final task status (NO VIDEO ASSEMBLY)
        background_tasks[task_id]['status'] = 'complete'
        background_tasks[task_id]['message'] = 'Image generation complete.'
        background_tasks[task_id]['progress'] = total_scenes
        # Result is the list of generated image paths (or None)
        # background_tasks[task_id]['result_images'] = generated_image_paths 

    except Exception as e:
        logger.error(f"Error in background generation pipeline for task {task_id}: {e}", exc_info=True)
        background_tasks[task_id]['status'] = 'error'
        background_tasks[task_id]['message'] = str(e)

# --- Status Endpoint ---
@app.route('/status/<task_id>')
def get_status(task_id):
    """
    Get the status for a specific generation task.
    """
    global background_tasks
    if task_id in background_tasks:
        # Optionally include scene details if requested?
        return jsonify(background_tasks[task_id])
    else:
        return jsonify({"error": "Task not found"}), 404

@app.route('/tasks')
def get_tasks():
    """ Returns a summary of all current tasks. """
    # Avoid sending potentially large scene data in the summary
    tasks_summary = {}
    for task_id, task_data in background_tasks.items():
        summary = task_data.copy()
        summary.pop('scenes', None) # Remove scenes from summary
        tasks_summary[task_id] = summary
    return jsonify(tasks_summary)

@app.route('/projects/<project_name>/temp/<path:filename>')
def get_temp_file(project_name, filename):
    logger.info(f"--- Request received for temp file: Project={project_name}, File={filename} ---")
    try:
        # 1. Sanitize Inputs
        project_name_safe = secure_filename(project_name)
        filename_safe = secure_filename(filename)
        logger.debug(f"Sanitized inputs: Project={project_name_safe}, File={filename_safe}")
        if project_name != project_name_safe or filename != filename_safe:
            logger.warning("Potential unsafe characters detected in project name or filename.")

        # 2. Get Base Project Directory from Config
        if 'UPLOAD_FOLDER' not in current_app.config:
            logger.error("CRITICAL: UPLOAD_FOLDER not found in Flask app config!")
            return jsonify({"error": "Server configuration error [UPLOAD_FOLDER]"}), 500

        projects_base_dir = Path(current_app.config['UPLOAD_FOLDER'])
        logger.debug(f"Projects base directory from config: {projects_base_dir}")
        if not projects_base_dir.is_dir():
            logger.error(f"Projects base directory does not exist: {projects_base_dir}")
            return jsonify({"error": "Server configuration error [Base Dir Missing]"}), 500

        # 3. Construct Full Path to Expected File
        project_dir = projects_base_dir / project_name_safe
        base_temp_parser_dir = project_dir / 'temp' / 'parser'
        file_path = base_temp_parser_dir / filename_safe
        logger.debug(f"Expected full file path: {file_path}")

        # 4. Check Directory Existence
        if not project_dir.is_dir():
            logger.warning(f"Project directory check failed: {project_dir}")
            return jsonify({"error": "Project not found"}), 404

        if not base_temp_parser_dir.is_dir():
            logger.warning(f"Base directory for temp parser files check failed: {base_temp_parser_dir}")
            # Check file next

        # 5. Check File Existence and Serve
        logger.debug(f"Checking if file exists: {file_path.is_file()}")
        if file_path.is_file():
            logger.info(f"File exists. Attempting to serve using send_from_directory: Directory='{base_temp_parser_dir}', Filename='{filename_safe}'")
            try:
                response = send_from_directory(base_temp_parser_dir, filename_safe)
                logger.info(f"send_from_directory successful for {filename_safe}")
                return response
            except Exception as send_e:
                logger.error(f"Error during send_from_directory for {filename_safe}: {send_e}", exc_info=True)
                return jsonify({"error": "Error serving file after finding it"}), 500
        else:
            logger.warning(f"File not found at expected path: {file_path}")
            return jsonify({"error": "Temporary file not found"}), 404
    except Exception as e:
        logger.error(f"--- UNEXPECTED ERROR in get_temp_file: {e} ---", exc_info=True)
        return jsonify({"error": "Internal server error serving temp file"}), 500

@app.route('/projects/<project_name>/generated/<path:filename>')
def get_generated_file(project_name, filename):
    """
    Serve generated image files from the project's temp/generated/ directory.
    """
    try:
        project_dir = get_project_dir(project_name)
        if not project_dir.exists():
            logger.warning(f"Project directory not found: {project_dir}")
            return jsonify({"error": "Project not found"}), 404

        file_path = project_dir / 'generated' / secure_filename(filename)
        if not file_path.exists():
            logger.warning(f"Generated file not found: {file_path}")
            return jsonify({"error": "Generated file not found"}), 404

        logger.info(f"Serving generated file: {file_path}")
        return send_file(file_path)
    except Exception as e:
        logger.error(f"Error serving generated file: {e}", exc_info=True)
        return jsonify({"error": "Failed to serve generated file"}), 500

@app.route('/projects/<project_name>/results/<path:filename>')
def get_result_file(project_name, filename):
    """
    Serve result files (like the final video) for a project.
    """
    try:
        project_dir = get_project_dir(project_name)
        if not project_dir.exists():
             return jsonify({"error": "Project not found"}), 404

        # Sanitize filename - IMPORTANT for security
        safe_filename = secure_filename(filename)
        file_path = project_dir / 'results' / safe_filename

        if not file_path.is_file():
             logger.warning(f"Result file not found: {file_path}")
             return jsonify({"error": "Result file not found"}), 404

        # Determine mimetype (optional but good practice)
        # mimetype = mimetypes.guess_type(file_path)[0]
        logger.debug(f"Serving result file: {file_path}")
        # Use as_attachment=True if you want download instead of display
        return send_file(file_path)
    except ValueError as e:
         # From get_project_dir
         return jsonify({"error": str(e)}), 400
    except Exception as e:
         logger.error(f"Error serving result file '{filename}' for project '{project_name}': {e}", exc_info=True)
         return jsonify({"error": "Failed to serve file"}), 500

# Update style routes to use manager from app config
@app.route('/styles')
def list_styles():
    """
    List available styles
    """
    style_manager = current_app.config['style_manager']
    styles = style_manager.list_styles()
    return jsonify(styles)

@app.route('/styles/create', methods=['POST'])
def create_style():
    """
    Create a new style
    """
    style_manager = current_app.config['style_manager']
    data = request.json
    style_name = data.get('name')
    style_data = data.get('config')
    
    if not style_name or not style_data:
        return jsonify({'error': 'Style name and config required'}), 400
    
    success = style_manager.create_style(style_name, style_data)
    if success:
        return jsonify({'success': True, 'message': f'Style {style_name} created'})
    else:
        return jsonify({'error': 'Failed to create style'}), 500

@app.route('/styles/train', methods=['POST'])
async def train_style(): # Make async if training is async
    """
    Train a new style (placeholder - needs async task handling like generate)
    """
    style_manager = current_app.config['style_manager']
    data = request.json
    style_name = data.get('name')
    images_dir = data.get('images_dir') # Needs proper handling of uploaded images/paths
    base_style = data.get('base_style')
    steps = data.get('steps', 1000)

    if not style_name or not images_dir:
        return jsonify({'error': 'Style name and images directory required'}), 400

    # TODO: Implement proper async task handling for training
    # This is just a placeholder for the synchronous call
    logger.warning("Style training route is currently synchronous and uses simulation.")
    success = style_manager.train_style(style_name, images_dir, base_style, steps)

    if success:
        return jsonify({'success': True, 'message': f'Style training started/completed for {style_name}'})
    else:
        return jsonify({'error': 'Failed to start/complete style training'}), 500

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """
    Get or update the main application configuration
    """
    config_path = current_app.config.get('main_config_path') # Need to store this path
    if not config_path:
        return jsonify({"error": "Configuration path not set"}), 500
    
    if request.method == 'POST':
        try:
            new_config_data = request.json
            save_config(new_config_data, config_path)
            # Update running config in app? Requires restart or careful update.
            current_app.config['config'] = new_config_data
            logger.info(f"Configuration saved to {config_path}")
            return jsonify({'success': True, 'message': 'Configuration updated'})
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return jsonify({'error': 'Failed to save configuration'}), 500
    else:
        # GET request
        config = current_app.config['config']
        return jsonify(config)


# Modified start_web_app to accept managers
def start_web_app(app_config, api_manager, model_manager, cache_manager, security_manager, host='127.0.0.1', port=5000, debug=False):
    """
    Start the Flask web application with initialized managers.
    
    Args:
        app_config (dict): Loaded application configuration.
        api_manager (APIManager): Initialized API manager.
        model_manager (ModelManager): Initialized Model manager.
        cache_manager (CacheManager): Initialized Cache manager.
        security_manager (SecurityManager): Initialized Security manager.
        host (str): Host to bind to.
        port (int): Port to listen on.
        debug (bool): Enable Flask debug mode.
    """
    global app

    # Store managers and config in Flask app context
    app.config['config'] = app_config
    app.config['api_manager'] = api_manager
    app.config['model_manager'] = model_manager
    app.config['cache_manager'] = cache_manager
    app.config['security_manager'] = security_manager
    app.config['style_manager'] = StyleManager(app_config, model_manager, cache_manager) # Init StyleManager here
    # Store path to main config if needed later (e.g., for saving)
    app.config['main_config_path'] = app_config.get('loaded_from_path', 'config/default.yaml') # Assume load_config adds this

    # Create base directories if they don't exist
    app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
    app.config['RESULT_FOLDER'].mkdir(parents=True, exist_ok=True)
    app.config['PROJECTS_BASE_DIR'].mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting Flask web server on http://{host}:{port}")
    # Use waitress or gunicorn for production instead of Flask dev server
    app.run(host=host, port=port, debug=debug)

# Note: Need to adjust startup.py to call this modified start_web_app

@app.route('/projects/<project_name>/preview_scene', methods=['POST'])
async def preview_scene(project_name):
    """ Generate a preview for a single selected scene. """
    global background_tasks

    try:
        project_dir = get_project_dir(project_name)
        if not project_dir.exists():
            return jsonify({"error": "Project not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Get data from request
    data = request.json
    task_id = data.get('task_id')
    scene_index = data.get('scene_index')
    style_name = data.get('style')
    use_cloud = data.get('use_cloud', False)

    # --- Input Validation ---
    if task_id not in background_tasks:
        return jsonify({"error": "Task ID not found or task data unavailable"}), 404

    task_info = background_tasks[task_id]

    if not isinstance(scene_index, int) or scene_index < 0 or scene_index >= len(task_info.get('scenes', [])):
        return jsonify({"error": f"Invalid scene index: {scene_index}"}), 400

    scene_data = task_info['scenes'][scene_index]
    original_image_path = scene_data.get('image')
    text = scene_data.get('text')

    if not original_image_path or not Path(original_image_path).exists():
        logger.error(f"Original image path not found or invalid for scene {scene_index} in task {task_id}: {original_image_path}")
        return jsonify({"error": f"Original image for scene {scene_index+1} not found"}), 400

    if not style_name:
        return jsonify({"error": "Style name is required for preview"}), 400

    logger.info(f"Received preview request for Project: {project_name}, Task: {task_id}, Scene Index: {scene_index}, Style: {style_name}")

    # --- Get Managers and Config --- 
    config = current_app.config['config']
    api_manager = current_app.config['api_manager']
    model_manager = current_app.config['model_manager']
    cache_manager = current_app.config['cache_manager']
    security_manager = current_app.config['security_manager']
    style_manager = current_app.config['style_manager']

    # Create project-specific config for this preview run
    # Ensures temp files go to the right project temp dir
    project_preview_config = config.copy()
    project_preview_config["temp_dir"] = project_dir / 'temp'
    project_preview_config["use_cloud"] = use_cloud # Reflect user choice for preview
    # Output path for generator isn't strictly needed here as generate returns the path,
    # but set temp_dir correctly is important.

    # Ensure temp dir exists
    os.makedirs(project_preview_config["temp_dir"] / "generated", exist_ok=True)

    try:
        # --- Instantiate Generator --- 
        # Pass the specific config for this preview
        generator = ImageGenerator(project_preview_config, style_manager, model_manager, api_manager, cache_manager, security_manager)

        # --- Generate Single Image --- 
        logger.info(f"Starting single scene generation for preview (Scene Index: {scene_index})...")
        # generate method handles caching internally
        generated_image_path = await generator.generate(
            original_image_path,
            text,
            style_name,
            scene_index=scene_index # Pass index for consistent naming/caching
        )

        if generated_image_path:
            logger.info(f"Preview image generated successfully: {generated_image_path}")
            # Return the path relative to the project's root or a structure the frontend understands
            # The generate method saves within temp/generated. Let's return the full path for now
            # and rely on get_result_file to serve it correctly.
            # Frontend JS currently constructs URL assuming file is directly in results/generated,
            # needs adjustment or this route needs to return a relative path.
            # Let's return the full path and fix the serving route if needed.
            return jsonify({
                "success": True,
                "generated_image_path": str(generated_image_path)
            })
        else:
            logger.error(f"Preview generation failed for scene index {scene_index}.")
            return jsonify({"success": False, "error": "Preview image generation failed"}), 500

    except Exception as e:
        logger.error(f"Error during preview generation for scene {scene_index}: {e}", exc_info=True)
        return jsonify({"success": False, "error": f"An internal error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    # This allows running the UI directly for development,
    # but managers won't be properly initialized without startup.py
    print("WARNING: Running ui/app.py directly.")
    print("Managers (API, Model, Cache, Security) will NOT be initialized.")
    print("Functionality will be limited. Run via startup.py --web for full features.")

    # Minimal config for basic operation if run directly
    dev_config = {
        "styles_dir": "styles",
        "local_models_path": "models",
        "temp_dir": "temp",
        "output_path": "output/output.mp4",
        "cache_enabled": False, # Disable cache if run directly
        "comfyui": {"host": "127.0.0.1", "port": 8188},
        # Add other minimal required config keys
    }
    # Create dummy managers if run directly
    class DummyManager: pass
    dummy_api_manager = DummyManager()
    dummy_model_manager = ModelManager(dev_config) # ModelManager might work partially
    dummy_cache_manager = CacheManager({"cache_enabled": False})
    dummy_security_manager = DummyManager()

    # Store dummy/minimal config and managers
    app.config['config'] = dev_config
    app.config['api_manager'] = dummy_api_manager
    app.config['model_manager'] = dummy_model_manager
    app.config['cache_manager'] = dummy_cache_manager
    app.config['security_manager'] = dummy_security_manager
    app.config['style_manager'] = StyleManager(dev_config, dummy_model_manager, dummy_cache_manager)

    # Create base directories
    app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
    app.config['RESULT_FOLDER'].mkdir(parents=True, exist_ok=True)
    app.config['PROJECTS_BASE_DIR'].mkdir(parents=True, exist_ok=True)

    app.run(debug=True)