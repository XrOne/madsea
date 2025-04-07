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
from pathlib import Path
from abc import ABC, abstractmethod
from PIL import Image
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Main image generator class that orchestrates the generation process"""

    def __init__(self, config, style_manager):
        """
        Initialize the image generator
        
        Args:
            config (dict): Configuration dictionary
            style_manager (StyleManager): Style manager instance
        """
        self.config = config
        self.style_manager = style_manager
        self.output_dir = Path(config.get("temp_dir", "temp")) / "generated"
        self.resolution = config.get("resolution", [1024, 768])
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize the appropriate generator based on config
        if config.get("use_cloud", False):
            logger.info("Using cloud-based image generation")
            self.generator = CloudGenerator(config)
        else:
            logger.info("Using local image generation")
            self.generator = LocalGenerator(config)
    
    def generate(self, image_path, text, style_name=None):
        """
        Generate an image based on the storyboard scene
        
        Args:
            image_path (str): Path to the reference image
            text (str): Text description of the scene
            style_name (str, optional): Name of the style to apply
            
        Returns:
            str: Path to the generated image
        """
        # Use specified style or default from config
        style_name = style_name or self.config.get("style", "default")
        
        # Get style parameters from style manager
        style_params = self.style_manager.get_style(style_name)
        
        # Prepare the reference image for ControlNet
        processed_image = self._prepare_reference_image(image_path)
        
        # Enhance the prompt with style-specific text
        enhanced_prompt = self._enhance_prompt(text, style_params)
        
        # Generate the image
        output_path = self.generator.generate_image(
            processed_image,
            enhanced_prompt,
            style_params,
            self.output_dir / f"{Path(image_path).stem}_generated.png"
        )
        
        logger.info(f"Generated image saved to: {output_path}")
        return str(output_path)
    
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
            
            # Save processed image
            processed_path = Path(image_path).parent / f"{Path(image_path).stem}_processed.png"
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
    
    def __init__(self, config):
        """
        Initialize the generator
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.resolution = config.get("resolution", [1024, 768])
    
    @abstractmethod
    def generate_image(self, reference_image, prompt, style_params, output_path):
        """
        Generate an image based on the reference image and prompt
        
        Args:
            reference_image (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            output_path (Path): Path to save the generated image
            
        Returns:
            str: Path to the generated image
        """
        pass


class LocalGenerator(BaseGenerator):
    """Local image generator using ComfyUI"""
    
    def __init__(self, config):
        """
        Initialize the local generator
        
        Args:
            config (dict): Configuration dictionary
        """
        super().__init__(config)
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
    
    def generate_image(self, reference_image, prompt, style_params, output_path):
        """
        Generate an image using ComfyUI
        
        Args:
            reference_image (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            output_path (Path): Path to save the generated image
            
        Returns:
            str: Path to the generated image
        """
        try:
            # Load the appropriate workflow template
            workflow = self._load_workflow_template(style_params)
            
            # Update workflow with parameters
            workflow = self._update_workflow_params(workflow, reference_image, prompt, style_params)
            
            # Submit workflow to ComfyUI
            result = self._submit_workflow(workflow)
            
            # Wait for and download the result
            image_path = self._get_workflow_result(result, output_path)
            
            return image_path
        except Exception as e:
            logger.error(f"Error generating image with ComfyUI: {e}")
            # Return a placeholder image
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
    
    def _update_workflow_params(self, workflow, reference_image, prompt, style_params):
        """
        Update workflow with parameters
        
        Args:
            workflow (dict): Workflow template
            reference_image (str): Path to the processed reference image
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
                node["inputs"]["image"] = reference_image
            
            # Update LoRA if specified in style parameters
            if node.get("class_type") == "LoraLoader" and "lora_name" in style_params:
                node["inputs"]["lora_name"] = style_params["lora_name"]
                node["inputs"]["strength"] = style_params.get("lora_strength", 0.8)
        
        return workflow
    
    def _submit_workflow(self, workflow):
        """
        Submit workflow to ComfyUI
        
        Args:
            workflow (dict): Workflow to submit
            
        Returns:
            dict: Result from ComfyUI
        """
        try:
            # Submit workflow
            response = requests.post(
                f"{self.api_url}/prompt",
                json={"prompt": workflow}
            )
            
            if response.status_code != 200:
                raise Exception(f"ComfyUI returned status code {response.status_code}: {response.text}")
            
            result = response.json()
            logger.info(f"Submitted workflow to ComfyUI, prompt ID: {result.get('prompt_id')}")
            
            return result
        except Exception as e:
            logger.error(f"Error submitting workflow to ComfyUI: {e}")
            raise
    
    def _get_workflow_result(self, result, output_path):
        """
        Wait for and download the result from ComfyUI
        
        Args:
            result (dict): Result from ComfyUI
            output_path (Path): Path to save the generated image
            
        Returns:
            str: Path to the generated image
        """
        prompt_id = result.get("prompt_id")
        if not prompt_id:
            raise ValueError("No prompt ID in ComfyUI response")
        
        # Wait for the workflow to complete
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            # Check if the workflow has completed
            try:
                response = requests.get(f"{self.api_url}/history/{prompt_id}")
                if response.status_code == 200:
                    history = response.json()
                    if prompt_id in history and "outputs" in history[prompt_id]:
                        # Find the image output node
                        for node_id, node_output in history[prompt_id]["outputs"].items():
                            if "images" in node_output:
                                # Get the first image
                                image_data = node_output["images"][0]
                                image_filename = image_data["filename"]
                                
                                # Download the image
                                image_url = f"http://{self.comfyui_host}:{self.comfyui_port}/view?filename={image_filename}"
                                image_response = requests.get(image_url)
                                
                                if image_response.status_code == 200:
                                    # Save the image
                                    with open(output_path, "wb") as f:
                                        f.write(image_response.content)
                                    
                                    logger.info(f"Downloaded generated image to {output_path}")
                                    return str(output_path)
                        
                        # If we get here, no image was found in the output
                        logger.warning("No image found in ComfyUI output")
                        break
            except Exception as e:
                logger.warning(f"Error checking ComfyUI history: {e}")
            
            # Wait before checking again
            time.sleep(2)
        
        logger.error("Timed out waiting for ComfyUI to generate image")
        return self._create_placeholder_image(output_path)
    
    def _create_placeholder_image(self, output_path):
        """
        Create a placeholder image when generation fails
        
        Args:
            output_path (Path): Path to save the placeholder image
            
        Returns:
            str: Path to the placeholder image
        """
        # Create a simple colored image with text
        img = np.ones((self.resolution[1], self.resolution[0], 3), dtype=np.uint8) * 200  # Light gray
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, "Image Generation Failed", (int(self.resolution[0]*0.1), int(self.resolution[1]*0.5)),
                   font, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Save image
        cv2.imwrite(str(output_path), img)
        
        return str(output_path)


class CloudGenerator(BaseGenerator):
    """Cloud-based image generator using external APIs"""
    
    def __init__(self, config):
        """
        Initialize the cloud generator
        
        Args:
            config (dict): Configuration dictionary
        """
        super().__init__(config)
        self.api_key = config.get("cloud_api_key", "")
        self.api_provider = config.get("cloud_api_provider", "openai").lower()
        
        if not self.api_key:
            logger.warning("No API key provided for cloud generation")
    
    def generate_image(self, reference_image, prompt, style_params, output_path):
        """
        Generate an image using a cloud API
        
        Args:
            reference_image (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            output_path (Path): Path to save the generated image
            
        Returns:
            str: Path to the generated image
        """
        try:
            # Choose the appropriate API based on provider
            if self.api_provider == "openai":
                image_data = self._generate_with_openai(reference_image, prompt, style_params)
            elif self.api_provider == "midjourney":
                image_data = self._generate_with_midjourney(reference_image, prompt, style_params)
            else:
                logger.error(f"Unsupported cloud API provider: {self.api_provider}")
                return self._create_placeholder_image(output_path)
            
            # Save the image
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            logger.info(f"Generated image saved to: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error generating image with cloud API: {e}")
            return self._create_placeholder_image(output_path)
    
    def _generate_with_openai(self, reference_image, prompt, style_params):
        """
        Generate an image using OpenAI's DALL-E API
        
        Args:
            reference_image (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            
        Returns:
            bytes: Image data
        """
        try:
            import openai
            
            # Set API key
            openai.api_key = self.api_key
            
            # Load reference image
            with open(reference_image, "rb") as f:
                reference_data = base64.b64encode(f.read()).decode("utf-8")
            
            # Call OpenAI API
            response = openai.Image.create_edit(
                image=reference_data,
                prompt=prompt,
                n=1,
                size=f"{self.resolution[0]}x{self.resolution[1]}"
            )
            
            # Get image URL
            image_url = response["data"][0]["url"]
            
            # Download image
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                raise Exception(f"Failed to download image from OpenAI: {image_response.status_code}")
            
            return image_response.content
        except Exception as e:
            logger.error(f"Error generating image with OpenAI: {e}")
            raise
    
    def _generate_with_midjourney(self, reference_image, prompt, style_params):
        """
        Generate an image using Midjourney API
        
        Args:
            reference_image (str): Path to the processed reference image
            prompt (str): Text prompt for generation
            style_params (dict): Style parameters
            
        Returns:
            bytes: Image data
        """
        # Note: This is a placeholder as Midjourney doesn't have an official API
        # In a real implementation, this would use a third-party Midjourney API service
        logger.warning("Midjourney API is not implemented")
        
        # Create a placeholder image
        img = np.ones((self.resolution[1], self.resolution[0], 3), dtype=np.uint8) * 200  # Light gray
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, "Midjourney API Not Implemented", (int(self.resolution[0]*0.1), int(self.resolution[1]*0.5)),
                   font, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Convert to bytes
        _, buffer = cv2.imencode(".png", img)
        return buffer.tobytes()
    
    def _create_placeholder_image(self, output_path):
        """
        Create a placeholder image when generation fails
        
        Args:
            output_path (Path): Path to save the placeholder image
            
        Returns:
            str: Path to the placeholder image
        """
        # Create a simple colored image with text
        img = np.ones((self.resolution[1], self.resolution[0], 3), dtype=np.uint8) * 200  # Light gray
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, "Cloud Generation Failed", (int(self.resolution[0]*0.1), int(self.resolution[1]*0.5)),
                   font, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Save image
        cv2.imwrite(str(output_path), img)
        
        return str(output_path)