#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration utilities for the Storyboard-to-Video AI Platform
"""

import os
import yaml
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "storyboard_path": "",
    "output_path": "output/output.mp4",
    "style": "default",
    "use_cloud": False,
    "cloud_api_key": "",
    "local_models_path": "models",
    "temp_dir": "temp",
    "scene_duration": 3.0,  # seconds per scene
    "transition_duration": 1.0,  # seconds for transition
    "resolution": [1024, 768],  # width, height
    "fps": 24,
    "ocr_language": "eng",
    "comfyui": {
        "host": "127.0.0.1",
        "port": 8188,
        "workflow_dir": "workflows"
    },
    "models": {
        "stable_diffusion": "runwayml/stable-diffusion-v1-5",
        "controlnet": "lllyasviel/control_v11p_sd15_scribble",
        "lora": {}
    }
}


def load_config(config_path=None):
    """
    Load configuration from file or use default
    
    Args:
        config_path (str): Path to configuration file (YAML or JSON)
        
    Returns:
        dict: Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_path and os.path.exists(config_path):
        try:
            ext = os.path.splitext(config_path)[1].lower()
            with open(config_path, 'r') as f:
                if ext == '.yaml' or ext == '.yml':
                    loaded_config = yaml.safe_load(f)
                elif ext == '.json':
                    loaded_config = json.load(f)
                else:
                    logger.warning(f"Unsupported config file format: {ext}")
                    return config
                
            # Update config with loaded values
            config.update(loaded_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
    else:
        logger.info("Using default configuration")
    
    # Create necessary directories
    os.makedirs(os.path.dirname(config['output_path']), exist_ok=True)
    os.makedirs(config['temp_dir'], exist_ok=True)
    os.makedirs(config['local_models_path'], exist_ok=True)
    
    return config


def save_config(config, config_path):
    """
    Save configuration to file
    
    Args:
        config (dict): Configuration dictionary
        config_path (str): Path to save configuration file
    """
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        ext = os.path.splitext(config_path)[1].lower()
        with open(config_path, 'w') as f:
            if ext == '.yaml' or ext == '.yml':
                yaml.dump(config, f, default_flow_style=False)
            elif ext == '.json':
                json.dump(config, f, indent=2)
            else:
                logger.warning(f"Unsupported config file format: {ext}")
                return
                
        logger.info(f"Saved configuration to {config_path}")
    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {e}")