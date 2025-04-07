#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Video Assembler Module

This module handles the assembly of generated images into a video sequence.
It supports:
- Simple cross-fade transitions between scenes
- Optional animation effects using AnimateDiff
- Configurable scene durations and transitions
- Video export with customizable resolution and framerate
"""

import os
import logging
import tempfile
from pathlib import Path
import subprocess
import shutil
import json
import time
import numpy as np
import cv2
from PIL import Image

logger = logging.getLogger(__name__)


class VideoAssembler:
    """Assembles generated images into a video sequence"""

    def __init__(self, config):
        """
        Initialize the video assembler
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.temp_dir = Path(config.get("temp_dir", "temp")) / "video"
        self.output_dir = Path(os.path.dirname(config.get("output_path", "output/output.mp4")))
        self.scene_duration = config.get("scene_duration", 3.0)  # seconds
        self.transition_duration = config.get("transition_duration", 1.0)  # seconds
        self.fps = config.get("fps", 24)
        self.resolution = config.get("resolution", [1024, 768])  # width, height
        self.use_animation = config.get("use_animation", False)
        
        # Create directories
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Check if ffmpeg is available
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """
        Check if ffmpeg is available
        """
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info("ffmpeg is available")
            else:
                logger.warning("ffmpeg check returned non-zero exit code")
                logger.warning(result.stderr)
        except Exception as e:
            logger.warning(f"Could not check ffmpeg: {e}")
            logger.warning("Video assembly may not work properly without ffmpeg")
    
    def create_video(self, image_paths, scenes=None):
        """
        Create a video from the generated images
        
        Args:
            image_paths (list): List of paths to generated images
            scenes (list, optional): List of scene data with text descriptions
            
        Returns:
            str: Path to the output video
        """
        try:
            # Clear previous temp files
            self._clear_temp_files()
            
            # Prepare frames for each scene
            logger.info("Preparing frames for video assembly")
            frame_paths = []
            
            if self.use_animation and self._check_animation_model():
                # Use AnimateDiff for more advanced animation
                frame_paths = self._create_animated_frames(image_paths, scenes)
            else:
                # Use simple cross-fade transitions
                frame_paths = self._create_transition_frames(image_paths)
            
            # Assemble frames into video
            output_path = self._assemble_video(frame_paths)
            
            # Add text overlays if scenes data is provided
            if scenes and output_path:
                output_path = self._add_text_overlays(output_path, scenes)
            
            return output_path
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return self._create_fallback_video(image_paths)
    
    def _create_transition_frames(self, image_paths):
        """
        Create frames with cross-fade transitions between scenes
        
        Args:
            image_paths (list): List of paths to generated images
            
        Returns:
            list: List of paths to generated frames
        """
        frame_paths = []
        
        # Calculate number of frames per scene and transition
        scene_frames = int(self.scene_duration * self.fps)
        transition_frames = int(self.transition_duration * self.fps)
        
        # Process each image
        for i, image_path in enumerate(image_paths):
            try:
                # Load current image
                current_img = cv2.imread(image_path)
                if current_img is None:
                    logger.warning(f"Could not load image: {image_path}")
                    continue
                
                # Resize to target resolution
                current_img = cv2.resize(current_img, (self.resolution[0], self.resolution[1]))
                
                # Generate scene frames (static image)
                for j in range(scene_frames):
                    frame_path = self.temp_dir / f"frame_{len(frame_paths):06d}.png"
                    cv2.imwrite(str(frame_path), current_img)
                    frame_paths.append(frame_path)
                
                # Generate transition frames (cross-fade to next image)
                if i < len(image_paths) - 1:
                    # Load next image
                    next_img = cv2.imread(image_paths[i + 1])
                    if next_img is None:
                        logger.warning(f"Could not load next image: {image_paths[i + 1]}")
                        continue
                    
                    # Resize to target resolution
                    next_img = cv2.resize(next_img, (self.resolution[0], self.resolution[1]))
                    
                    # Create transition frames
                    for j in range(transition_frames):
                        # Calculate alpha for blending
                        alpha = j / transition_frames
                        
                        # Blend images
                        blended = cv2.addWeighted(current_img, 1 - alpha, next_img, alpha, 0)
                        
                        # Save frame
                        frame_path = self.temp_dir / f"frame_{len(frame_paths):06d}.png"
                        cv2.imwrite(str(frame_path), blended)
                        frame_paths.append(frame_path)
            except Exception as e:
                logger.error(f"Error processing image {image_path}: {e}")
        
        logger.info(f"Created {len(frame_paths)} frames with transitions")
        return frame_paths
    
    def _create_animated_frames(self, image_paths, scenes):
        """
        Create animated frames using AnimateDiff
        
        Args:
            image_paths (list): List of paths to generated images
            scenes (list): List of scene data with text descriptions
            
        Returns:
            list: List of paths to generated frames
        """
        logger.info("Using AnimateDiff for advanced animation")
        
        # In a real implementation, this would use AnimateDiff to generate
        # animated sequences for each scene and then combine them
        
        # For this example, we'll simulate the process with a simple animation
        frame_paths = []
        
        # Calculate frames per scene
        scene_frames = int(self.scene_duration * self.fps)
        transition_frames = int(self.transition_duration * self.fps)
        
        for i, image_path in enumerate(image_paths):
            try:
                # Load image
                img = cv2.imread(image_path)
                if img is None:
                    logger.warning(f"Could not load image: {image_path}")
                    continue
                
                # Resize to target resolution
                img = cv2.resize(img, (self.resolution[0], self.resolution[1]))
                
                # Create a simple animation (zoom and pan)
                for j in range(scene_frames):
                    # Calculate animation parameters
                    progress = j / scene_frames
                    
                    # Apply zoom effect (1.0 to 1.1)
                    zoom = 1.0 + (0.1 * progress)
                    
                    # Apply pan effect
                    pan_x = int(self.resolution[0] * 0.05 * progress)
                    pan_y = int(self.resolution[1] * 0.05 * progress)
                    
                    # Create transformation matrix
                    M = cv2.getRotationMatrix2D(
                        (self.resolution[0] // 2, self.resolution[1] // 2),
                        0,  # No rotation
                        zoom
                    )
                    
                    # Apply translation
                    M[0, 2] += pan_x - (self.resolution[0] * (zoom - 1)) / 2
                    M[1, 2] += pan_y - (self.resolution[1] * (zoom - 1)) / 2
                    
                    # Apply transformation
                    animated_frame = cv2.warpAffine(
                        img,
                        M,
                        (self.resolution[0], self.resolution[1]),
                        borderMode=cv2.BORDER_CONSTANT,
                        borderValue=(0, 0, 0)
                    )
                    
                    # Save frame
                    frame_path = self.temp_dir / f"frame_{len(frame_paths):06d}.png"
                    cv2.imwrite(str(frame_path), animated_frame)
                    frame_paths.append(frame_path)
                
                # Add transition frames if not the last image
                if i < len(image_paths) - 1:
                    # Load next image
                    next_img = cv2.imread(image_paths[i + 1])
                    if next_img is None:
                        logger.warning(f"Could not load next image: {image_paths[i + 1]}")
                        continue
                    
                    # Resize to target resolution
                    next_img = cv2.resize(next_img, (self.resolution[0], self.resolution[1]))
                    
                    # Create transition frames
                    for j in range(transition_frames):
                        # Calculate alpha for blending
                        alpha = j / transition_frames
                        
                        # Blend images
                        blended = cv2.addWeighted(img, 1 - alpha, next_img, alpha, 0)
                        
                        # Save frame
                        frame_path = self.temp_dir / f"frame_{len(frame_paths):06d}.png"
                        cv2.imwrite(str(frame_path), blended)
                        frame_paths.append(frame_path)
            except Exception as e:
                logger.error(f"Error creating animated frames for {image_path}: {e}")
        
        logger.info(f"Created {len(frame_paths)} animated frames")
        return frame_paths
    
    def _check_animation_model(self):
        """
        Check if AnimateDiff model is available
        
        Returns:
            bool: True if available, False otherwise
        """
        # In a real implementation, this would check if the AnimateDiff model is available
        # For this example, we'll assume it's not available
        logger.warning("AnimateDiff model not available, using simple transitions instead")
        return False
    
    def _assemble_video(self, frame_paths):
        """
        Assemble frames into a video using ffmpeg
        
        Args:
            frame_paths (list): List of paths to frames
            
        Returns:
            str: Path to the output video
        """
        if not frame_paths:
            logger.error("No frames to assemble")
            return None
        
        try:
            # Create output path
            output_path = Path(self.config.get("output_path", "output/output.mp4"))
            os.makedirs(output_path.parent, exist_ok=True)
            
            # Create frame list file for ffmpeg
            frame_list_path = self.temp_dir / "frames.txt"
            with open(frame_list_path, 'w') as f:
                for frame_path in frame_paths:
                    f.write(f"file '{frame_path}'\n")
            
            # Assemble video using ffmpeg
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-r", str(self.fps),  # Frame rate
                "-f", "concat",  # Concatenate frames
                "-safe", "0",  # Don't require safe filenames
                "-i", str(frame_list_path),  # Input file list
                "-c:v", "libx264",  # Codec
                "-pix_fmt", "yuv420p",  # Pixel format
                "-crf", "23",  # Quality (lower is better)
                "-preset", "medium",  # Encoding speed/quality tradeoff
                str(output_path)  # Output path
            ]
            
            logger.info(f"Assembling video with ffmpeg: {' '.join(cmd)}")
            
            # Run ffmpeg
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"ffmpeg error: {result.stderr}")
                return None
            
            logger.info(f"Video assembled successfully: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error assembling video: {e}")
            return None
    
    def _add_text_overlays(self, video_path, scenes):
        """
        Add text overlays to the video
        
        Args:
            video_path (str): Path to the input video
            scenes (list): List of scene data with text descriptions
            
        Returns:
            str: Path to the output video with text overlays
        """
        try:
            # Create output path
            input_path = Path(video_path)
            output_path = input_path.parent / f"{input_path.stem}_with_text{input_path.suffix}"
            
            # Create subtitle file
            subtitle_path = self.temp_dir / "subtitles.srt"
            self._create_subtitle_file(subtitle_path, scenes)
            
            # Add subtitles using ffmpeg
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-i", str(input_path),  # Input video
                "-vf", f"subtitles={subtitle_path}",  # Add subtitles
                "-c:a", "copy",  # Copy audio stream
                str(output_path)  # Output path
            ]
            
            logger.info(f"Adding text overlays with ffmpeg: {' '.join(cmd)}")
            
            # Run ffmpeg
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"ffmpeg error: {result.stderr}")
                return video_path
            
            logger.info(f"Text overlays added successfully: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error adding text overlays: {e}")
            return video_path
    
    def _create_subtitle_file(self, subtitle_path, scenes):
        """
        Create a subtitle file for the video
        
        Args:
            subtitle_path (Path): Path to save the subtitle file
            scenes (list): List of scene data with text descriptions
        """
        try:
            with open(subtitle_path, 'w') as f:
                # Calculate timings
                scene_duration_ms = int(self.scene_duration * 1000)
                transition_duration_ms = int(self.transition_duration * 1000)
                
                for i, scene in enumerate(scenes):
                    # Get scene text
                    text = scene.get("text", "").strip()
                    if not text:
                        continue
                    
                    # Calculate start and end times
                    start_time = i * (scene_duration_ms + transition_duration_ms)
                    end_time = start_time + scene_duration_ms
                    
                    # Format times as HH:MM:SS,mmm
                    start_formatted = self._format_time(start_time)
                    end_formatted = self._format_time(end_time)
                    
                    # Write subtitle entry
                    f.write(f"{i+1}\n")
                    f.write(f"{start_formatted} --> {end_formatted}\n")
                    f.write(f"{text}\n\n")
            
            logger.info(f"Created subtitle file: {subtitle_path}")
        except Exception as e:
            logger.error(f"Error creating subtitle file: {e}")
    
    def _format_time(self, time_ms):
        """
        Format time in milliseconds as HH:MM:SS,mmm
        
        Args:
            time_ms (int): Time in milliseconds
            
        Returns:
            str: Formatted time
        """
        seconds, milliseconds = divmod(time_ms, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def _create_fallback_video(self, image_paths):
        """
        Create a simple fallback video when advanced assembly fails
        
        Args:
            image_paths (list): List of paths to generated images
            
        Returns:
            str: Path to the output video
        """
        try:
            # Create output path
            output_path = Path(self.config.get("output_path", "output/output.mp4"))
            os.makedirs(output_path.parent, exist_ok=True)
            
            # Create a simple slideshow with ffmpeg
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-framerate", "1/3",  # 3 seconds per image
                "-pattern_type", "glob",  # Use glob pattern for input
                "-i", f"{os.path.dirname(image_paths[0])}/scene_*_generated.png",  # Input pattern
                "-vf", f"scale={self.resolution[0]}:{self.resolution[1]}",  # Scale to target resolution
                "-c:v", "libx264",  # Codec
                "-pix_fmt", "yuv420p",  # Pixel format
                "-r", "30",  # Output frame rate
                str(output_path)  # Output path
            ]
            
            logger.info(f"Creating fallback video with ffmpeg: {' '.join(cmd)}")
            
            # Run ffmpeg
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"ffmpeg error: {result.stderr}")
                
                # Try an even simpler approach
                return self._create_simple_slideshow(image_paths, output_path)
            
            logger.info(f"Fallback video created successfully: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error creating fallback video: {e}")
            return None
    
    def _create_simple_slideshow(self, image_paths, output_path):
        """
        Create a very simple slideshow using OpenCV
        
        Args:
            image_paths (list): List of paths to generated images
            output_path (Path): Path to save the output video
            
        Returns:
            str: Path to the output video
        """
        try:
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(
                str(output_path),
                fourcc,
                self.fps,
                (self.resolution[0], self.resolution[1])
            )
            
            # Add each image to the video for a few seconds
            for image_path in image_paths:
                # Load and resize image
                img = cv2.imread(image_path)
                if img is None:
                    logger.warning(f"Could not load image: {image_path}")
                    continue
                
                img = cv2.resize(img, (self.resolution[0], self.resolution[1]))
                
                # Add image to video for scene_duration seconds
                for _ in range(int(self.scene_duration * self.fps)):
                    video.write(img)
            
            # Release video writer
            video.release()
            
            logger.info(f"Simple slideshow created successfully: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error creating simple slideshow: {e}")
            return None
    
    def _clear_temp_files(self):
        """
        Clear temporary files from previous runs
        """
        # Remove and recreate temp directory
        if self.temp_dir.exists():
            for file in self.temp_dir.glob("*"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete temp file {file}: {e}")