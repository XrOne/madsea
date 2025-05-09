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

# Import managers
from utils.model_manager import ModelManager
from utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class StyleManager:
    """Manager for visual styles using LoRA models and workflows."""

    def __init__(self, config, model_manager: ModelManager, cache_manager: CacheManager):
        """
        Initialize the style manager
        
        Args:
            config (dict): Configuration dictionary
            model_manager (ModelManager): Model manager instance
            cache_manager (CacheManager): Cache manager instance
        """
        self.config = config
        self.model_manager = model_manager
        self.cache_manager = cache_manager
        self.styles_dir = Path(config.get("styles_dir", "styles"))
        
        # Create directories if they don't exist
        os.makedirs(self.styles_dir, exist_ok=True)
        
        # Load available styles
        self.styles = self._load_styles()
        
        # Add default style if no styles are available
        if not self.styles:
            self._create_default_style()
    
    def _load_styles(self):
        """
        Load available styles from the styles directory. Uses cache.
        
        Returns:
            dict: Dictionary of available styles
        """
        cache_key = None
        styles = {}
        
        if self.cache_manager:
            # Create a key based on the styles directory content/mtime?
            # Simple key based on directory path for now
            cache_key = self.cache_manager.generate_key("loaded_styles", str(self.styles_dir))
            cached_styles = self.cache_manager.get(cache_key)
            if cached_styles:
                logger.info("Loaded styles from cache.")
                return cached_styles

        logger.info("Loading styles from disk (cache miss or disabled)...")
        # Check for style definition files (JSON and YAML)
        for style_file in self.styles_dir.glob("*.json"):
            try:
                with open(style_file, 'r') as f:
                    style_data = json.load(f)
                
                style_name = style_file.stem
                # Validate LoRA model existence using ModelManager
                lora_name = style_data.get("lora_name")
                if lora_name:
                     lora_info = self.model_manager.get_model(lora_name, model_type="lora", source="local")
                     if not lora_info:
                         logger.warning(f"LoRA model '{lora_name}' specified in style '{style_name}' not found by ModelManager. Style might not work correctly.")
                     else:
                         # Optionally add LoRA path to style_data for convenience?
                         style_data['_lora_path'] = lora_info.get('path')

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
                # Validate LoRA model existence using ModelManager
                lora_name = style_data.get("lora_name")
                if lora_name:
                     lora_info = self.model_manager.get_model(lora_name, model_type="lora", source="local")
                     if not lora_info:
                         logger.warning(f"LoRA model '{lora_name}' specified in style '{style_name}' not found by ModelManager. Style might not work correctly.")
                     else:
                         # Optionally add LoRA path to style_data for convenience?
                         style_data['_lora_path'] = lora_info.get('path')

                styles[style_name] = style_data
                logger.info(f"Loaded style: {style_name}")
            except Exception as e:
                logger.error(f"Error loading style {style_file}: {e}")
        
        # Store loaded styles in cache
        if self.cache_manager and cache_key:
             self.cache_manager.set(cache_key, styles)

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
        
        # Create Déclic Ombre Chinoise style
        declic_ombre_chinoise_style = {
            "name": "declic_ombre_chinoise",
            "description": "Silhouettes intégrales avec rim light et lumière cinématographique réaliste",
            "prompt_prefix": "cinematic photograph, silhouetted figure, rim lighting, realistic directional lighting",
            "prompt_suffix": "detailed silhouette, no visible faces, cinematic shadows, realistic textures, 16:9 ratio",
            "negative_prompt": "low quality, blurry, distorted, deformed, cartoon, anime, visible face details, flat lighting",
            "workflow_template": "default_controlnet.json",
            "lora_name": "",
            "lora_strength": 0.85,
            "cfg_scale": 7.5,
            "steps": 30,
            "sampler": "euler_ancestral"
        }
        
        # Save Déclic Ombre Chinoise style
        self.styles["declic_ombre_chinoise"] = declic_ombre_chinoise_style
        self._save_style("declic_ombre_chinoise", declic_ombre_chinoise_style)
        logger.info("Created Déclic Ombre Chinoise style")
    
    def _save_style(self, style_name, style_data):
        """
        Save style data to file and invalidate style cache.
        
        Args:
            style_name (str): Name of the style
            style_data (dict): Style data
        """
        try:
            # Remove internal keys before saving
            style_data_to_save = {k: v for k, v in style_data.items() if not k.startswith('_')}

            style_path = self.styles_dir / f"{style_name}.json"
            with open(style_path, 'w') as f:
                json.dump(style_data_to_save, f, indent=2)
            logger.info(f"Saved style to {style_path}")

            # Invalidate cache
            if self.cache_manager:
                 cache_key = self.cache_manager.generate_key("loaded_styles", str(self.styles_dir))
                 # Simple deletion, or update cache? Deletion forces reload next time.
                 try:
                      cache_filepath = self.cache_manager._get_cache_filepath(cache_key)
                      if cache_filepath.exists():
                           os.remove(cache_filepath)
                           logger.info("Invalidated style cache due to save operation.")
                 except Exception as cache_e:
                      logger.warning(f"Failed to invalidate style cache file: {cache_e}")

        except Exception as e:
            logger.error(f"Error saving style {style_name}: {e}")
    
    def get_style(self, style_name):
        """
        Get style parameters by name. Reloads styles if not found (e.g., cache invalidated).
        
        Args:
            style_name (str): Name of the style
            
        Returns:
            dict: Style parameters or empty dict if not found.
        """
        if style_name not in self.styles:
            logger.warning(f"Style '{style_name}' not in memory, attempting reload...")
            self.styles = self._load_styles() # Reload all styles

        if style_name in self.styles:
            # Ensure LoRA path is up-to-date if needed (ModelManager check)
            style_data = self.styles[style_name]
            lora_name = style_data.get("lora_name")
            if lora_name and not style_data.get('_lora_path'): # Check if path needs refresh
                 lora_info = self.model_manager.get_model(lora_name, model_type="lora", source="local")
                 if lora_info:
                     style_data['_lora_path'] = lora_info.get('path')
                 else:
                     logger.warning(f"LoRA '{lora_name}' for style '{style_name}' not found during get_style.")
                     if '_lora_path' in style_data: del style_data['_lora_path'] # Clear stale path
            return style_data
        else:
            logger.warning(f"Style '{style_name}' not found even after reload, using default")
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
            
            # Validate LoRA model existence if specified
            lora_name = style_data.get("lora_name")
            if lora_name:
                 lora_info = self.model_manager.get_model(lora_name, model_type="lora", source="local")
                 if not lora_info:
                     logger.error(f"LoRA model '{lora_name}' specified for new style '{style_name}' not found.")
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
                logger.error("Cannot delete the default style.")
                return False
            
            # Remove from memory
            del self.styles[style_name]
            
            # Remove file
            style_path_json = self.styles_dir / f"{style_name}.json"
            style_path_yaml = self.styles_dir / f"{style_name}.yaml"
            deleted = False
            if style_path_json.exists():
                os.remove(style_path_json)
                deleted = True
            if style_path_yaml.exists():
                 os.remove(style_path_yaml)
                 deleted = True

            if deleted:
                logger.info(f"Deleted style file for: {style_name}")
            else:
                 logger.warning(f"Style file not found for {style_name} during deletion attempt.")

            # Invalidate cache
            if self.cache_manager:
                cache_key = self.cache_manager.generate_key("loaded_styles", str(self.styles_dir))
                try:
                    cache_filepath = self.cache_manager._get_cache_filepath(cache_key)
                    if cache_filepath.exists():
                        os.remove(cache_filepath)
                        logger.info("Invalidated style cache due to delete operation.")
                except Exception as cache_e:
                     logger.warning(f"Failed to invalidate style cache file: {cache_e}")

            # Note: This does NOT delete the associated LoRA model file
            # LoRA model deletion should be handled separately via ModelManager maybe

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
            
            base_style_name = base_style or "default"
            base_style_params = self.get_style(base_style_name)

            # Determine base SD model (needs ModelManager)
            # base_sd_model_id = base_style_params.get("stable_diffusion_model", self.config.get("models", {}).get("stable_diffusion"))
            # sd_model_info = self.model_manager.get_model(base_sd_model_id, ...)
            # if not sd_model_info: raise ValueError(f"Base SD model {base_sd_model_id} not found")
            # base_model_path = sd_model_info.get('path')
            base_model_path = "PLACEHOLDER_SD_MODEL_PATH" # Replace with ModelManager lookup
            logger.warning("Using placeholder for base SD model path in training.")

            # Define output directory for LoRA model (managed by ModelManager?)
            lora_output_dir = Path(self.model_manager.local_models_path) / "lora" / style_name
            os.makedirs(lora_output_dir, exist_ok=True)

            # --- Training Execution (Conceptual) ---
            # This part needs to call a training script/service.
            # Option 1: Call local script (e.g., Kohya_ss GUI scripts via subprocess)
            # Option 2: Use an integrated library (if available)
            # Option 3: Call a cloud training API via APIManager

            logger.info(f"Starting LoRA training simulation for style '{style_name}'...")
            logger.info(f" - Training images: {training_images_dir}")
            logger.info(f" - Base SD model: {base_model_path}")
            logger.info(f" - Output LoRA directory: {lora_output_dir}")
            logger.info(f" - Steps: {num_steps}")

            # Placeholder: Simulate training process
            training_success = self._simulate_training(style_name, lora_output_dir, num_steps)

            if training_success:
                logger.info(f"LoRA training simulation completed for style '{style_name}'.")
                # Find the generated LoRA file (e.g., .safetensors)
                lora_files = list(lora_output_dir.glob("*.safetensors"))
                if not lora_files:
                    logger.error("Training simulation finished, but no LoRA file found.")
                    return False

                generated_lora_path = lora_files[0] # Assume first one is the result
                lora_name_for_style = generated_lora_path.stem # Use filename stem as LoRA ID

                # Update or create the style definition
                new_style_data = {
                    "name": style_name,
                    "description": f"Custom style '{style_name}' trained from images",
                    "lora_name": lora_name_for_style, # Link to the trained LoRA
                    "lora_strength": 0.8, # Default strength
                    # Copy other relevant params from base style or set defaults
                    "prompt_prefix": base_style_params.get("prompt_prefix", ""),
                    "prompt_suffix": base_style_params.get("prompt_suffix", ""),
                    "negative_prompt": base_style_params.get("negative_prompt", ""),
                    "stable_diffusion_model": base_style_params.get("stable_diffusion_model"), # Keep base SD model reference
                    "workflow_template": base_style_params.get("workflow_template", "default_lora.json"), # Use a LoRA workflow
                    # ... other params like cfg, steps, sampler
                }

                self.create_style(style_name, new_style_data) # This will save and update cache

                # Refresh ModelManager registry? Or assume it picks up new files?
                self.model_manager._build_registry() # Force refresh registry

                logger.info(f"Style '{style_name}' created/updated with trained LoRA '{lora_name_for_style}'")
                return True
            else:
                logger.error(f"LoRA training failed for style '{style_name}'.")
                return False

        except Exception as e:
            logger.error(f"Error during style training for {style_name}: {e}", exc_info=True)
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