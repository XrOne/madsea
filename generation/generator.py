#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Image Generation Module

This module handles the generation of images from storyboard scenes using
Stable Diffusion, ControlNet, and custom styles via LoRA.

It supports both local generation (via ComfyUI) and cloud-based generation
through external APIs like OpenAI or Midjourney.
"""

import os
import json
import logging
import time
import base64
import requests
import asyncio
from pathlib import Path
from abc import ABC, abstractmethod
from PIL import Image
import numpy as np
import cv2
import hashlib
import random
import uuid
import aiohttp

# Import managers (assuming they are accessible via sys.path)
from utils.api_manager import APIManager
from utils.model_manager import ModelManager
from utils.cache_manager import CacheManager
from utils.security import SecurityManager

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Main image generator class that orchestrates the generation process"""

    def __init__(self, config, style_manager, model_manager: ModelManager, api_manager: APIManager, cache_manager: CacheManager, security_manager: SecurityManager):
        """
        Initialize the image generator
        
        Args:
            config (dict): Configuration dictionary
            style_manager (StyleManager): Style manager instance
            model_manager (ModelManager): Model manager instance
            api_manager (APIManager): API manager instance
            cache_manager (CacheManager): Cache manager instance
            security_manager (SecurityManager): Security manager instance
        """
        self.config = config
        self.style_manager = style_manager
        self.model_manager = model_manager
        self.api_manager = api_manager
        self.cache_manager = cache_manager
        self.security_manager = security_manager
        self.output_dir = Path(config.get("temp_dir", "temp")) / "generated"
        self.resolution = config.get("resolution", [1024, 768])
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize the appropriate generator based on config
        if config.get("use_cloud", False):
            logger.info("Using cloud-based image generation")
            self.generator = CloudGenerator(config, api_manager, security_manager, cache_manager)
        else:
            logger.info("Using local image generation")
            self.generator = LocalGenerator(config, api_manager, model_manager, cache_manager)
    
    async def generate(self, image_path, text, style_name=None, scene_index=0):
        """
        Generate an image based on the storyboard scene. Uses cache.
        
        Args:
            image_path (str): Path to the reference image (original from parser).
            text (str): Text description of the scene.
            style_name (str, optional): Name of the style to apply.
            scene_index (int): Index of the scene for naming output.
            
        Returns:
            str or None: Path to the generated image, or None on failure.
        """
        # Use specified style or default from config
        style_name = style_name or self.config.get("style", "default")
        
        # Get style parameters from style manager
        style_params = self.style_manager.get_style(style_name)
        if not style_params:
            logger.error(f"Style '{style_name}' not found.")
            return None
        
        # --- Cache Check ---
        cache_key = None
        final_output_path = self.output_dir / f"scene_{scene_index:04d}_generated.png"
        
        # Disable cache for debugging? Add a flag?
        use_cache = False # FORCE CACHE DISABLED FOR DEBUGGING

        if self.cache_manager and use_cache:
            try:
                # Create a robust cache key
                ref_img_hash = self._get_file_hash(image_path) if Path(image_path).exists() else None
                cache_key = self.cache_manager.generate_key(
                    "generated_image",
                    ref_img_hash, # Use hash of reference image
                    text,
                    style_name,
                    style_params, # Include style details
                    self.resolution,
                    self.config.get("use_cloud", False),
                    # Potentially add model IDs used if deterministic
                )
                cached_result_path = self.cache_manager.get(cache_key)
                if cached_result_path and Path(cached_result_path).exists():
                    logger.info(f"Cache hit for scene {scene_index} ({style_name}). Using: {cached_result_path}")
                    # Ensure the target output path exists by copying/linking?
                    # For simplicity, assume cached path is usable directly or copy it
                    if str(Path(cached_result_path).resolve()) != str(final_output_path.resolve()):
                         shutil.copy2(cached_result_path, final_output_path)
                    return str(final_output_path)
            except Exception as e:
                logger.warning(f"Error checking image generation cache: {e}")
        # --- End Cache Check ---
        
        logger.info(f"Generating image for scene {scene_index} ({style_name}) - Cache miss or disabled.")
        
        # Prepare the reference image for ControlNet
        processed_image_path = self._prepare_reference_image(image_path)
        if not processed_image_path:
             logger.error(f"Failed to prepare reference image for scene {scene_index}: {image_path}")
             return None
        
        # Enhance the prompt with style-specific text
        enhanced_prompt = self._enhance_prompt(text, style_params)
        
        # Generate the image using the specific generator (now async)
        generated_image_path = await self.generator.generate_image(
            processed_image_path,
            enhanced_prompt,
            style_params,
            final_output_path # Pass the final desired output path
        )
        
        if generated_image_path:
            logger.info(f"Generated image for scene {scene_index} saved to: {generated_image_path}")
            # --- Cache Store ---
            if self.cache_manager and cache_key:
                try:
                    # Cache the path to the *final* generated image
                    self.cache_manager.set(cache_key, str(generated_image_path))
                    logger.info(f"Cached generated image path for key: {cache_key}")
                except Exception as e:
                    logger.warning(f"Error writing image generation result to cache: {e}")
            # --- End Cache Store ---
            return str(generated_image_path)
        else:
            logger.error(f"Image generation failed for scene {scene_index}.")
            return None
    
    def _get_file_hash(self, file_path):
         """ Calculates SHA256 hash of a file. """
         hasher = hashlib.sha256()
         with open(file_path, 'rb') as f:
             while chunk := f.read(8192):
                 hasher.update(chunk)
         return hasher.hexdigest()
    
    def _prepare_reference_image(self, image_path):
        """
        Prepare the reference image for ControlNet
        
        Args:
            image_path (str): Path to the reference image
            
        Returns:
            str: Path to the processed image
        """
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Resize to target resolution
            img = cv2.resize(img, (self.resolution[0], self.resolution[1]))
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection (for scribble ControlNet)
            edges = cv2.Canny(gray, 100, 200)
            
            # Create white background
            background = np.ones_like(img) * 255
            
            # Draw edges on white background
            background[edges != 0] = 0
            
            # Save processed image to a subfolder within the generator output dir?
            processed_path = self.output_dir / f"{Path(image_path).stem}_processed.png"
            cv2.imwrite(str(processed_path), background)
            
            return str(processed_path)
        except Exception as e:
            logger.error(f"Error processing reference image: {e}")
            # Return original image if processing fails
            return image_path
    
    def _enhance_prompt(self, text, style_params):
        """
        Enhance the prompt with style-specific text
        
        Args:
            text (str): Original text description
            style_params (dict): Style parameters
            
        Returns:
            str: Enhanced prompt
        """
        # Get style-specific prompt prefix and suffix
        prefix = style_params.get("prompt_prefix", "")
        suffix = style_params.get("prompt_suffix", "")
        
        # Clean up the text
        text = text.strip()
        
        # Combine prefix, text, and suffix
        enhanced_prompt = f"{prefix} {text} {suffix}".strip()
        
        return enhanced_prompt


class BaseGenerator(ABC):
    """Abstract base class for image generators"""
    
    def __init__(self, config, api_manager: APIManager, cache_manager: CacheManager, **kwargs):
        """
        Initialize the base generator
        
        Args:
            config (dict): Configuration dictionary
            api_manager (APIManager): API manager instance
            cache_manager (CacheManager): Cache manager instance
            **kwargs: Additional managers (like model_manager, security_manager)
        """
        self.config = config
        self.api_manager = api_manager
        self.cache_manager = cache_manager
        self.resolution = config.get("resolution", [1024, 768])
        # Store other managers if passed
        self.model_manager = kwargs.get('model_manager')
        self.security_manager = kwargs.get('security_manager')
    
    @abstractmethod
    async def generate_image(self, reference_image_path, prompt, style_params, output_path):
        """
        Generate an image based on the reference image and prompt
        
        Args:
            reference_image_path (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            output_path (Path): Path to save the generated image
            
        Returns:
            str or None: Path to the generated image or None on failure
        """
        pass

    def _create_placeholder_image(self, output_path):
        """ Creates a simple placeholder image if generation fails. """
        try:
            img = Image.new('RGB', (self.resolution[0], self.resolution[1]), color = 'darkgrey')
            # TODO: Add text indicating failure?
            img.save(output_path)
            logger.warning(f"Generation failed, created placeholder image at: {output_path}")
            return str(output_path)
        except Exception as e:
             logger.error(f"Failed to create placeholder image: {e}")
             return None


class LocalGenerator(BaseGenerator):
    """Local image generator using ComfyUI"""
    
    def __init__(self, config, api_manager: APIManager, model_manager: ModelManager, cache_manager: CacheManager):
        """
        Initialize the local generator
        
        Args:
            config (dict): Configuration dictionary
            api_manager (APIManager): API manager instance
            model_manager (ModelManager): Model manager instance
            cache_manager (CacheManager): Cache manager instance
        """
        super().__init__(config, api_manager=api_manager, cache_manager=cache_manager, model_manager=model_manager)
        self.comfyui_host = config.get("comfyui", {}).get("host", "127.0.0.1")
        self.comfyui_port = config.get("comfyui", {}).get("port", 8188)
        self.workflow_dir = Path(config.get("comfyui", {}).get("workflow_dir", "workflows"))
        
        # Create workflow directory if it doesn't exist
        os.makedirs(self.workflow_dir, exist_ok=True)
        
        # Base URL for ComfyUI API
        self.api_url = f"http://{self.comfyui_host}:{self.comfyui_port}/api"
        
        # Check if ComfyUI is available
        self._check_comfyui_connection()
    
    def _check_comfyui_connection(self):
        """
        Check if ComfyUI is available
        """
        try:
            response = requests.get(f"http://{self.comfyui_host}:{self.comfyui_port}/")
            if response.status_code == 200:
                logger.info("ComfyUI is available")
            else:
                logger.warning(f"ComfyUI returned status code {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to ComfyUI: {e}")
            logger.warning("Make sure ComfyUI is running and accessible")
    
    async def generate_image(self, reference_image_path, prompt, style_params, output_path):
        """
        Generate an image using ComfyUI via API Manager.
        
        Args:
            reference_image_path (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            output_path (Path): Path to save the generated image
            
        Returns:
            str or None: Path to the generated image or None on failure
        """
        try:
            # Load the appropriate workflow template
            workflow = self._load_workflow_template(style_params)
            if not workflow:
                 logger.error("Failed to load or create a workflow.")
                 return self._create_placeholder_image(output_path)

            # Update workflow with parameters (needs ModelManager)
            workflow = self._update_workflow_params(workflow, reference_image_path, prompt, style_params)

            # Submit workflow to ComfyUI using APIManager
            logger.debug("Submitting workflow to ComfyUI...")
            result_data = await self._submit_workflow(workflow)
            if not result_data or 'prompt_id' not in result_data:
                logger.error(f"Failed to submit workflow to ComfyUI or invalid response: {result_data}")
                return self._create_placeholder_image(output_path)

            prompt_id = result_data['prompt_id']
            logger.info(f"Workflow submitted to ComfyUI. Prompt ID: {prompt_id}")

            # Wait for and download the result using APIManager
            image_data = await self._get_workflow_result(prompt_id)

            if image_data:
                 # Save the received image data
                 with open(output_path, "wb") as f:
                     f.write(image_data)
                 logger.info(f"Image successfully generated by ComfyUI and saved to: {output_path}")
                 return str(output_path)
            else:
                 logger.error(f"Failed to retrieve image result from ComfyUI for prompt ID: {prompt_id}")
                 return self._create_placeholder_image(output_path)

        except Exception as e:
            logger.error(f"Error during local image generation with ComfyUI: {e}", exc_info=True)
            return self._create_placeholder_image(output_path)
    
    def _load_workflow_template(self, style_params):
        """
        Load the appropriate workflow template based on style parameters
        
        Args:
            style_params (dict): Style parameters
            
        Returns:
            dict: Workflow template
        """
        # Get workflow template path from style parameters or use default
        template_name = style_params.get("workflow_template", "default_controlnet.json")
        template_path = self.workflow_dir / template_name
        
        # Check if template exists
        if not template_path.exists():
            # Use default template
            logger.warning(f"Workflow template {template_path} not found, using default")
            # Create a basic default workflow
            return self._create_default_workflow()
        
        # Load template
        with open(template_path, 'r') as f:
            workflow = json.load(f)
        
        return workflow
    
    def _create_default_workflow(self):
        """
        Create a default workflow for ControlNet + Stable Diffusion
        
        Returns:
            dict: Default workflow
        """
        # This is a simplified representation of a ComfyUI workflow
        # In a real implementation, this would be a complete ComfyUI workflow JSON
        workflow = {
            "3": {  # Checkpoint Loader
                "inputs": {
                    "ckpt_name": self.config.get("models", {}).get("stable_diffusion", "runwayml/stable-diffusion-v1-5")
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "4": {  # Prompt
                "inputs": {
                    "text": "",  # Will be filled later
                    "clip": ["3", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "5": {  # Negative Prompt
                "inputs": {
                    "text": "low quality, blurry, distorted, deformed",
                    "clip": ["3", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "6": {  # ControlNet Image Loader
                "inputs": {
                    "image": ""  # Will be filled later
                },
                "class_type": "LoadImage"
            },
            "7": {  # ControlNet
                "inputs": {
                    "image": ["6", 0],
                    "model": self.config.get("models", {}).get("controlnet", "lllyasviel/control_v11p_sd15_scribble"),
                    "strength": 0.8
                },
                "class_type": "ControlNetLoader"
            },
            "8": {  # Sampler
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
            "9": {  # Empty Latent
                "inputs": {
                    "width": self.resolution[0],
                    "height": self.resolution[1],
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "10": {  # Decoder
                "inputs": {
                    "samples": ["8", 0],
                    "vae": ["3", 2]
                },
                "class_type": "VAEDecode"
            },
            "11": {  # Save Image
                "inputs": {
                    "images": ["10", 0],
                    "filename_prefix": "generated",
                    "save_to": "output"
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow
    
    def _update_workflow_params(self, workflow, reference_image_path, prompt, style_params):
        """
        Update workflow with parameters
        
        Args:
            workflow (dict): Workflow template
            reference_image_path (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            
        Returns:
            dict: Updated workflow
        """
        # This is a simplified implementation
        # In a real implementation, this would update the specific nodes in the workflow
        
        # Find the prompt node and update it
        for node_id, node in workflow.items():
            if node.get("class_type") == "CLIPTextEncode" and "positive" in node_id.lower():
                node["inputs"]["text"] = prompt
            
            # Find the image loader node and update it
            if node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = reference_image_path
            
            # Update LoRA if specified in style parameters
            if node.get("class_type") == "LoraLoader" and "lora_name" in style_params:
                node["inputs"]["lora_name"] = style_params["lora_name"]
                node["inputs"]["strength"] = style_params.get("lora_strength", 0.8)
        
        return workflow
    
    async def _submit_workflow(self, workflow):
        """
        Submit workflow to ComfyUI using APIManager
        
        Args:
            workflow (dict): Workflow dictionary
            
        Returns:
            dict or None: Response from ComfyUI or None on failure
        """
        try:
            # Submit workflow
            response = await self.api_manager.call_api(
                "comfyui",
                method="POST",
                endpoint_suffix="/prompt",
                data={"prompt": workflow}
            )
            
            if response:
                 logger.debug(f"ComfyUI submission response: {response}")
                 return response
            else:
                 logger.error("Failed to submit workflow to ComfyUI.")
                 return None
        except Exception as e:
            logger.error(f"Error submitting workflow to ComfyUI: {e}")
            raise
    
    async def _get_workflow_result(self, prompt_id, poll_interval=1, timeout=120):
        """
        Wait for workflow completion and download the result using APIManager.
        
        Args:
            prompt_id (str): The ID of the submitted prompt.
            poll_interval (int): Seconds between polling attempts.
            timeout (int): Maximum seconds to wait for completion.
            
        Returns:
            bytes or None: The generated image data as bytes, or None on failure/timeout.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                logger.debug(f"Polling ComfyUI history for prompt_id: {prompt_id}")
                history_response = await self.api_manager.call_api(
                    "comfyui",
                    method="GET",
                    endpoint_suffix=f"/history/{prompt_id}"
                )

                if history_response and prompt_id in history_response:
                    prompt_history = history_response[prompt_id]
                    logger.debug(f"History received: Keys={list(prompt_history.keys())}")

                    # Check outputs - Structure depends on workflow's SaveImage node
                    if "outputs" in prompt_history:
                        outputs = prompt_history["outputs"]
                        # Find the output node (e.g., the SaveImage node ID)
                        # This requires knowing the output node ID from the workflow.
                        # Let's assume the SaveImage node was ID "11" as in the default workflow
                        output_node_id = "11" # Hardcoded for now, should be dynamic ideally

                        if output_node_id in outputs and outputs[output_node_id].get("images"):
                            image_info = outputs[output_node_id]["images"][0]
                            filename = image_info.get("filename")
                            subfolder = image_info.get("subfolder")
                            img_type = image_info.get("type") # output or temp?

                            if filename and img_type == 'output':
                                logger.info(f"Workflow {prompt_id} completed. Output image: {filename}")
                                # Download the image using /view endpoint
                                image_data = await self.api_manager.call_api(
                                    "comfyui",
                                    method="GET",
                                    endpoint_suffix="/view",
                                    params={"filename": filename, "subfolder": subfolder, "type": img_type}
                                    # APIManager needs to handle non-json response here (bytes)
                                )
                                if isinstance(image_data, bytes):
                                     logger.info(f"Successfully downloaded image {filename}")
                                     return image_data
                                else:
                                     logger.error(f"Failed to download image {filename} from ComfyUI /view endpoint. Response: {image_data}")
                                     return None
                            else:
                                 logger.debug(f"Output node {output_node_id} found, but image data not yet ready or not final output.")
                        else:
                             logger.debug(f"Output node {output_node_id} not found in outputs or no images generated yet.")
                    else:
                         logger.debug(f"Prompt {prompt_id} still executing or history format unexpected.")

                # Wait before polling again
                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error polling ComfyUI history: {e}")
                await asyncio.sleep(poll_interval * 2) # Longer wait on error

        logger.error(f"Timeout waiting for ComfyUI workflow {prompt_id} to complete after {timeout} seconds.")
        return None


class CloudGenerator(BaseGenerator):
    """Cloud-based image generator using external APIs"""
    
    def __init__(self, config, api_manager: APIManager, security_manager: SecurityManager, cache_manager: CacheManager):
        """
        Initialize the cloud generator
        
        Args:
            config (dict): Configuration dictionary
            api_manager (APIManager): API manager instance
            security_manager (SecurityManager): Security manager instance
            cache_manager (CacheManager): Cache manager instance
        """
        super().__init__(config, api_manager=api_manager, cache_manager=cache_manager, security_manager=security_manager)
        self.api_provider_config = config.get("cloud_providers", {}) # Store provider specific configs
        self.default_provider = config.get("default_cloud_provider", "openai") # Default if not specified by style

    async def generate_image(self, reference_image_path, prompt, style_params, output_path):
        """
        Generate an image using a cloud API via API Manager.
        
        Args:
            reference_image_path (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            output_path (Path): Path to save the generated image
            
        Returns:
            str or None: Path to the generated image or None on failure
        """
        provider = style_params.get("cloud_api_provider", self.default_provider).lower()
        logger.info(f"Generating image using cloud provider: {provider}")

        # Get API Key securely
        # Assumes API keys are stored in config under 'api_keys_encrypted' or 'api_keys'
        encrypted_key = self.config.get("api_keys_encrypted", {}).get(provider)
        decrypted_key = None
        if encrypted_key:
             decrypted_key = self.security_manager.decrypt_string(encrypted_key)
        if not decrypted_key:
             decrypted_key = self.config.get("api_keys", {}).get(provider)

        if not decrypted_key:
            logger.error(f"API key for cloud provider '{provider}' not found or couldn't be decrypted.")
            return self._create_placeholder_image(output_path)

        # Register API with manager (it might already be registered from startup)
        provider_conf = self.api_provider_config.get(provider, {})
        api_endpoint = provider_conf.get("endpoint") # Get endpoint from config
        if not api_endpoint:
             logger.warning(f"API endpoint for provider '{provider}' not found in config. Using default/guess.")
             # Add default endpoints for known providers if needed
             if provider == "openai": api_endpoint = "https://api.openai.com/v1"
             elif provider == "midjourney": api_endpoint = "PLACEHOLDER_MJ_API" # Requires actual API if available
             else: api_endpoint = ""

        self.api_manager.register_api(provider, api_key=decrypted_key, endpoint=api_endpoint)

        try:
            image_data = None
            # Choose the appropriate API call based on provider
            if provider == "openai":
                image_data = await self._generate_with_openai(reference_image_path, prompt, style_params)
            elif provider == "midjourney":
                image_data = await self._generate_with_midjourney(reference_image_path, prompt, style_params)
            # Add elif for other providers (DALL-E 3, Stability, etc.)
            else:
                logger.error(f"Unsupported cloud API provider specified: {provider}")
                return self._create_placeholder_image(output_path)
            
            if image_data and isinstance(image_data, bytes):
                # Save the image
                with open(output_path, "wb") as f:
                    f.write(image_data)
                logger.info(f"Cloud generated image saved to: {output_path}")
                return str(output_path)
            else:
                 logger.error(f"Cloud generation with {provider} failed or returned invalid data.")
                 return self._create_placeholder_image(output_path)
            
        except Exception as e:
            logger.error(f"Error generating image with cloud API '{provider}': {e}", exc_info=True)
            return self._create_placeholder_image(output_path)
    
    async def _generate_with_openai(self, reference_image_path, prompt, style_params):
        """
        Generate an image using OpenAI's DALL-E API (assuming DALL-E 2 Edit or DALL-E 3).
        
        Args:
            reference_image_path (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            
        Returns:
            bytes or None: Image data as bytes, or None on failure.
        """
        try:
            # DALL-E 3 preferred, uses different endpoint and structure
            # Check config or style_params for model version (e.g., dall-e-3)
            model = style_params.get("openai_model", "dall-e-2") # Default to DALL-E 2
            api_key = self.api_manager.api_keys.get("openai") # API key already registered

            if not api_key:
                 logger.error("OpenAI API key not available in APIManager.")
                 return None

            headers = {
                 "Authorization": f"Bearer {api_key}",
                 # Content-Type might be application/json or multipart/form-data depending on endpoint
            }

            if model == "dall-e-3":
                 logger.info("Using OpenAI DALL-E 3 API")
                 payload = {
                     "model": "dall-e-3",
                     "prompt": prompt, # DALL-E 3 typically uses just the prompt
                     "n": 1,
                     "size": f"{self.resolution[0]}x{self.resolution[1]}", # Check supported sizes
                     "response_format": "b64_json" # Get image data directly
                 }
                 endpoint_suffix = "/images/generations"
                 headers['Content-Type'] = 'application/json'
                 response = await self.api_manager.call_api("openai", method="POST", endpoint_suffix=endpoint_suffix, data=payload, headers=headers)

                 if response and response.get("data") and response["data"][0].get("b64_json"):
                     b64_data = response["data"][0]["b64_json"]
                     return base64.b64decode(b64_data)
                 else:
                      logger.error(f"OpenAI DALL-E 3 API call failed or returned unexpected data: {response}")
                      return None

            else: # Assume DALL-E 2 Image Edit endpoint
                 logger.info("Using OpenAI DALL-E 2 Image Edit API")
                 endpoint_suffix = "/images/edits"
                 # Requires multipart/form-data
                 # Need a way for APIManager or here to handle multipart uploads async
                 # TODO: Implement async multipart upload similar to comfyui upload

                 # Placeholder - This part needs rework for async multipart
                 logger.warning("DALL-E 2 async multipart upload not fully implemented yet.")
                 try:
                     import openai # Use official lib as fallback TEMPORARILY? NO - stick to APIManager
                     logger.error("Fallback to openai library is deprecated. Need async multipart in APIManager.")
                     # Fallback simulation (REMOVE THIS LATER)
                     # openai.api_key = api_key
                     # with open(reference_image_path, "rb") as image_file:
                     #     response = openai.Image.create_edit(
                     #         image=image_file,
                     #         prompt=prompt,
                     #         n=1,
                     #         size=f"{self.resolution[0]}x{self.resolution[1]}",
                     #         response_format="b64_json"
                     #     )
                     # return base64.b64decode(response['data'][0]['b64_json'])
                     return None # Return None until implemented
                 except Exception as fallback_e:
                      logger.error(f"Error during DALL-E 2 fallback attempt: {fallback_e}")
                      return None

        except Exception as e:
            logger.error(f"Error generating image with OpenAI: {e}", exc_info=True)
            return None
    
    async def _generate_with_midjourney(self, reference_image_path, prompt, style_params):
        """
        Generate an image using a Midjourney API (if available).
        Note: Midjourney does not have an official public API as of last check.
              This assumes a hypothetical or third-party API exists and is configured.
        
        Args:
            reference_image_path (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            
        Returns:
            bytes or None: Image data as bytes, or None on failure.
        """
        logger.warning("Midjourney API interaction is hypothetical or relies on unofficial APIs.")
        provider = "midjourney"
        api_key = self.api_manager.api_keys.get(provider)
        if not api_key:
            logger.error(f"API key for {provider} not found.")
            return None

        try:
            # Construct payload based on the assumed Midjourney API structure
            payload = {
                "prompt": prompt,
                # Add other MJ parameters from style_params: --ar, --style, --seed, image refs?
                "aspect_ratio": f"{self.resolution[0]}:{self.resolution[1]}",
                "image_weight": style_params.get("mj_iw", 0.5), # Example param
                "seed": style_params.get("seed"),
                 # Need to handle reference image upload/linking if API supports it
            }
            # Remove None values from payload
            payload = {k: v for k, v in payload.items() if v is not None}

            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            endpoint_suffix = "/imagine" # Hypothetical endpoint

            response = await self.api_manager.call_api(provider, method="POST", endpoint_suffix=endpoint_suffix, data=payload, headers=headers)

            if response and response.get("status") == "success" and response.get("image_url"):
                 # Assuming API returns a URL to the generated image
                 image_url = response["image_url"]
                 logger.info(f"Midjourney task submitted, image URL: {image_url}")
                 # Need to download the image from the URL
                 # Use requests or aiohttp via APIManager?
                 img_response = requests.get(image_url, timeout=60) # Simple sync download for now
                 img_response.raise_for_status()
                 return img_response.content
            else:
                 logger.error(f"Midjourney API call failed or returned unexpected data: {response}")
                 return None

        except Exception as e:
            logger.error(f"Error generating image with Midjourney API: {e}", exc_info=True)
            return None

    async def _get_image_data(self, filename, subfolder, image_type):
        """ Fetches the actual image bytes from the ComfyUI /view endpoint. """
        try:
            comfyui_url = self.api_manager.get_comfyui_url()
            params = {"filename": filename, "subfolder": subfolder, "type": image_type}
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{comfyui_url}/view", params=params) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error(f"Error fetching image from ComfyUI /view: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Exception fetching image data: {e}")
            return None

    async def _get_prompt_status(self, prompt_id):
        """ Gets the execution status of a specific prompt from ComfyUI /prompt endpoint. """    
        try:
            comfyui_url = self.api_manager.get_comfyui_url()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{comfyui_url}/prompt/{prompt_id}") as response:
                    if response.status == 200:
                        # The prompt endpoint itself doesn't give status, it gives the submitted prompt
                        # We need the history endpoint for status/outputs
                        # This function might be misnamed or redundant if we only use history
                        return await response.json() # Returns the original prompt
                    else:
                        # logger.error(f"Error getting prompt status {prompt_id}: {response.status}")
                        # It's normal to get 404 if the prompt doesn't exist / hasn't run?
                        return None # Or specific error status?
        except Exception as e:
            logger.error(f"Exception getting prompt status for {prompt_id}: {e}")
            return None

    async def _get_history(self, prompt_id):
        """ Fetches the execution history which contains outputs for a given prompt_id. """
        try:
            comfyui_url = self.api_manager.get_comfyui_url()
            async with aiohttp.ClientSession() as session:
                # Fetch history for the specific prompt ID
                async with session.get(f"{comfyui_url}/history/{prompt_id}") as response:
                    if response.status == 200:
                        history = await response.json()
                        # logger.debug(f"History for {prompt_id}: {json.dumps(history, indent=2)}")
                        return history
                    else:
                        logger.error(f"Error getting history for prompt {prompt_id}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Exception getting history for {prompt_id}: {e}")
            return None