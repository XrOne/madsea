#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Style Management Module

This module handles the management of visual styles for the Storyboard-to-Video AI Platform.
It supports:
- Loading pre-trained styles (LoRA models)
- Training new styles on custom images
- Applying styles to the generation pipeline
"""

import os
import json
import logging
import shutil
from pathlib import Path
import subprocess
import time
import yaml

logger = logging.getLogger(__name__)


class StyleManager:
    """Manager for visual styles using LoRA models"""

    def __init__(self, config):
        """
        Initialize the style manager
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.styles_dir = Path(config.get("styles_dir", "styles"))
        self.models_dir = Path(config.get("local_models_path", "models"))
        self.lora_dir = self.models_dir / "lora"
        
        # Create directories if they don't exist
        os.makedirs(self.styles_dir, exist_ok=True)
        os.makedirs(self.lora_dir, exist_ok=True)
        
        # Load available styles
        self.styles = self._load_styles()
        
        # Add default style if no styles are available
        if not self.styles:
            self._create_default_style()
    
    def _load_styles(self):
        """
        Load available styles from the styles directory
        
        Returns:
            dict: Dictionary of available styles
        """
        styles = {}
        
        # Check for style definition files
        for style_file in self.styles_dir.glob("*.json"):
            try:
                with open(style_file, 'r') as f:
                    style_data = json.load(f)
                
                style_name = style_file.stem
                styles[style_name] = style_data
                logger.info(f"Loaded style: {style_name}")
            except Exception as e:
                logger.error(f"Error loading style {style_file}: {e}")
        
        # Also check for YAML style files
        for style_file in self.styles_dir.glob("*.yaml"):
            try:
                with open(style_file, 'r') as f:
                    style_data = yaml.safe_load(f)
                
                style_name = style_file.stem
                styles[style_name] = style_data
                logger.info(f"Loaded style: {style_name}")
            except Exception as e:
                logger.error(f"Error loading style {style_file}: {e}")
        
        return styles
    
    def _create_default_style(self):
        """
        Create a default style if no styles are available
        """
        default_style = {
            "name": "default",
            "description": "Default style using base Stable Diffusion",
            "prompt_prefix": "high quality, detailed, cinematic",
            "prompt_suffix": "4k, detailed",
            "negative_prompt": "low quality, blurry, distorted, deformed",
            "workflow_template": "default_controlnet.json",
            "lora_name": "",
            "lora_strength": 0.8,
            "cfg_scale": 7.5,
            "steps": 20,
            "sampler": "euler_ancestral"
        }
        
        # Save default style
        self.styles["default"] = default_style
        self._save_style("default", default_style)
        logger.info("Created default style")
        
        # Create a cinematic style as well
        cinematic_style = {
            "name": "cinematic",
            "description": "Cinematic style with dramatic lighting",
            "prompt_prefix": "cinematic, dramatic lighting, film grain, movie scene",
            "prompt_suffix": "8k, detailed, professional photography",
            "negative_prompt": "low quality, blurry, distorted, deformed, cartoon, anime",
            "workflow_template": "default_controlnet.json",
            "lora_name": "",
            "lora_strength": 0.8,
            "cfg_scale": 8.0,
            "steps": 25,
            "sampler": "euler_ancestral"
        }
        
        # Save cinematic style
        self.styles["cinematic"] = cinematic_style
        self._save_style("cinematic", cinematic_style)
        logger.info("Created cinematic style")
        
        # Create a declic style (silhouette style)
        declic_style = {
            "name": "declic",
            "description": "Declic cinematic silhouette style",
            "prompt_prefix": "silhouette style, high contrast, minimalist, black and white",
            "prompt_suffix": "dramatic, stark, elegant, simple",
            "negative_prompt": "color, detailed, complex, busy, noisy",
            "workflow_template": "default_controlnet.json",
            "lora_name": "",
            "lora_strength": 0.8,
            "cfg_scale": 7.0,
            "steps": 20,
            "sampler": "euler_ancestral"
        }
        
        # Save declic style
        self.styles["declic"] = declic_style
        self._save_style("declic", declic_style)
        logger.info("Created declic style")
    
    def _save_style(self, style_name, style_data):
        """
        Save style data to file
        
        Args:
            style_name (str): Name of the style
            style_data (dict): Style data
        """
        try:
            style_path = self.styles_dir / f"{style_name}.json"
            with open(style_path, 'w') as f:
                json.dump(style_data, f, indent=2)
            logger.info(f"Saved style to {style_path}")
        except Exception as e:
            logger.error(f"Error saving style {style_name}: {e}")
    
    def get_style(self, style_name):
        """
        Get style parameters by name
        
        Args:
            style_name (str): Name of the style
            
        Returns:
            dict: Style parameters
        """
        if style_name in self.styles:
            return self.styles[style_name]
        else:
            logger.warning(f"Style '{style_name}' not found, using default")
            return self.styles.get("default", {})
    
    def list_styles(self):
        """
        List all available styles
        
        Returns:
            list: List of style names and descriptions
        """
        return [
            {"name": name, "description": data.get("description", "")} 
            for name, data in self.styles.items()
        ]
    
    def create_style(self, style_name, style_data):
        """
        Create a new style
        
        Args:
            style_name (str): Name of the new style
            style_data (dict): Style parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate style data
            required_fields = ["description", "prompt_prefix", "prompt_suffix"]
            for field in required_fields:
                if field not in style_data:
                    logger.error(f"Missing required field '{field}' in style data")
                    return False
            
            # Add style name to data
            style_data["name"] = style_name
            
            # Save style
            self.styles[style_name] = style_data
            self._save_style(style_name, style_data)
            
            logger.info(f"Created new style: {style_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating style {style_name}: {e}")
            return False
    
    def delete_style(self, style_name):
        """
        Delete a style
        
        Args:
            style_name (str): Name of the style to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if style_name not in self.styles:
                logger.warning(f"Style '{style_name}' not found")
                return False
            
            # Don't delete default style
            if style_name == "default":
                logger.warning("Cannot delete default style")
                return False
            
            # Remove from memory
            del self.styles[style_name]
            
            # Remove file
            style_path = self.styles_dir / f"{style_name}.json"
            if style_path.exists():
                os.remove(style_path)
            
            # Also check for YAML file
            yaml_path = self.styles_dir / f"{style_name}.yaml"
            if yaml_path.exists():
                os.remove(yaml_path)
            
            logger.info(f"Deleted style: {style_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting style {style_name}: {e}")
            return False
    
    def train_style(self, style_name, training_images_dir, base_style=None, num_steps=1000):
        """
        Train a new style using LoRA
        
        Args:
            style_name (str): Name of the new style
            training_images_dir (str): Directory containing training images
            base_style (str, optional): Base style to start from
            num_steps (int, optional): Number of training steps
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            training_images_dir = Path(training_images_dir)
            if not training_images_dir.exists() or not training_images_dir.is_dir():
                logger.error(f"Training images directory not found: {training_images_dir}")
                return False
            
            # Get base style parameters
            base_params = {}
            if base_style and base_style in self.styles:
                base_params = self.styles[base_style].copy()
            elif "default" in self.styles:
                base_params = self.styles["default"].copy()
            
            # Create output directory for the LoRA model
            lora_output_dir = self.lora_dir / style_name
            os.makedirs(lora_output_dir, exist_ok=True)
            
            # In a real implementation, this would call a script to train the LoRA model
            # For this example, we'll simulate the training process
            logger.info(f"Training LoRA for style '{style_name}' using images from {training_images_dir}")
            logger.info(f"This would normally take a long time. Simulating training process...")
            
            # Simulate training process
            self._simulate_training(style_name, lora_output_dir, num_steps)
            
            # Create style data
            style_data = base_params.copy()
            style_data.update({
                "name": style_name,
                "description": f"Custom style trained on {training_images_dir.name}",
                "lora_name": str(lora_output_dir / f"{style_name}.safetensors"),
                "lora_strength": 0.8,
                "trained": True,
                "training_images": str(training_images_dir),
                "training_steps": num_steps,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Save style
            self.styles[style_name] = style_data
            self._save_style(style_name, style_data)
            
            logger.info(f"Trained new style: {style_name}")
            return True
        except Exception as e:
            logger.error(f"Error training style {style_name}: {e}")
            return False
    
    def _simulate_training(self, style_name, output_dir, num_steps):
        """
        Simulate the training process
        
        Args:
            style_name (str): Name of the style
            output_dir (Path): Output directory for the model
            num_steps (int): Number of training steps
        """
        # In a real implementation, this would call a script to train the LoRA model
        # For example, using kohya-ss/sd-scripts or similar
        
        # Create a dummy safetensors file to simulate the trained model
        dummy_model_path = output_dir / f"{style_name}.safetensors"
        with open(dummy_model_path, 'w') as f:
            f.write("This is a placeholder for a trained LoRA model.")
        
        # Create a training log
        log_path = output_dir / "training_log.txt"
        with open(log_path, 'w') as f:
            f.write(f"Training log for style '{style_name}'\n")
            f.write(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Number of steps: {num_steps}\n")
            f.write(f"Finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Simulate training time
        for i in range(5):
            logger.info(f"Training progress: {i+1}/5")
            time.sleep(0.5)  # Simulate training time
        
        logger.info(f"Training completed for style '{style_name}'")
    
    def import_style(self, style_path):
        """
        Import a style from a file
        
        Args:
            style_path (str): Path to the style file (JSON or YAML)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            style_path = Path(style_path)
            if not style_path.exists():
                logger.error(f"Style file not found: {style_path}")
                return False
            
            # Load style data
            ext = style_path.suffix.lower()
            with open(style_path, 'r') as f:
                if ext == ".json":
                    style_data = json.load(f)
                elif ext in [".yaml", ".yml"]:
                    style_data = yaml.safe_load(f)
                else:
                    logger.error(f"Unsupported style file format: {ext}")
                    return False
            
            # Get style name
            style_name = style_data.get("name", style_path.stem)
            
            # Copy any associated LoRA model
            lora_path = style_data.get("lora_name", "")
            if lora_path and os.path.exists(lora_path):
                lora_filename = os.path.basename(lora_path)
                target_lora_path = self.lora_dir / lora_filename
                shutil.copy2(lora_path, target_lora_path)
                style_data["lora_name"] = str(target_lora_path)
            
            # Save style
            self.styles[style_name] = style_data
            self._save_style(style_name, style_data)
            
            logger.info(f"Imported style: {style_name}")
            return True
        except Exception as e:
            logger.error(f"Error importing style from {style_path}: {e}")
            return False
    
    def export_style(self, style_name, output_path):
        """
        Export a style to a file
        
        Args:
            style_name (str): Name of the style to export
            output_path (str): Path to save the style file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if style_name not in self.styles:
                logger.error(f"Style '{style_name}' not found")
                return False
            
            output_path = Path(output_path)
            os.makedirs(output_path.parent, exist_ok=True)
            
            # Get style data
            style_data = self.styles[style_name].copy()
            
            # Save style data
            ext = output_path.suffix.lower()
            with open(output_path, 'w') as f:
                if ext == ".json":
                    json.dump(style_data, f, indent=2)
                elif ext in [".yaml", ".yml"]:
                    yaml.dump(style_data, f, default_flow_style=False)
                else:
                    logger.error(f"Unsupported output format: {ext}")
                    return False
            
            logger.info(f"Exported style '{style_name}' to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting style {style_name}: {e}")
            return False