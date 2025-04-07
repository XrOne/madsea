#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Storyboard-to-Video AI Platform
Main entry point for the application
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsing.parser import StoryboardParser
from generation.generator import ImageGenerator
from styles.manager import StyleManager
from video.assembler import VideoAssembler
from utils.config import load_config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("storyboard_to_video.log"),
    ],
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert storyboard to stylized animated video"
    )
    parser.add_argument(
        "--storyboard", "-s", type=str, help="Path to storyboard PDF or image directory"
    )
    parser.add_argument(
        "--style", "-t", type=str, default="default", help="Style to apply to generated images"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="output.mp4", help="Output video file path"
    )
    parser.add_argument(
        "--config", "-c", type=str, default="config/default.yaml", help="Configuration file"
    )
    parser.add_argument(
        "--use-cloud",
        action="store_true",
        help="Use cloud resources for generation",
    )
    parser.add_argument(
        "--web", "-w", action="store_true", help="Start web interface"
    )
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Start web interface if requested
    if args.web:
        from ui.app import start_web_app
        start_web_app()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.storyboard:
        config["storyboard_path"] = args.storyboard
    if args.style:
        config["style"] = args.style
    if args.output:
        config["output_path"] = args.output
    if args.use_cloud:
        config["use_cloud"] = True
    
    # Check if required parameters are provided
    if "storyboard_path" not in config:
        logger.error("No storyboard path provided. Use --storyboard or specify in config.")
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(os.path.abspath(config["output_path"]))
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    parser = StoryboardParser(config)
    style_manager = StyleManager(config)
    generator = ImageGenerator(config, style_manager)
    assembler = VideoAssembler(config)
    
    # Process storyboard
    logger.info(f"Parsing storyboard: {config['storyboard_path']}")
    scenes = parser.parse(config["storyboard_path"])
    
    # Generate images for each scene
    logger.info(f"Generating images with style: {config['style']}")
    generated_images = []
    for i, scene in enumerate(scenes):
        logger.info(f"Processing scene {i+1}/{len(scenes)}")
        image = generator.generate(scene["image"], scene["text"])
        generated_images.append(image)
    
    # Assemble video
    logger.info(f"Assembling video: {config['output_path']}")
    video_path = assembler.create_video(generated_images, scenes)
    
    logger.info(f"Video created successfully: {video_path}")
    return video_path


if __name__ == "__main__":
    main()