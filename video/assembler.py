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
import hashlib

# Import managers
from utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class VideoAssembler:
    """Assembles generated images into a video sequence"""

    def __init__(self, config, cache_manager: CacheManager = None):
        """
        Initialize the video assembler
        
        Args:
            config (dict): Configuration dictionary
            cache_manager (CacheManager, optional): Cache manager instance.
        """
        self.config = config
        self.cache_manager = cache_manager
        self.temp_dir = Path(config.get("temp_dir", "temp")) / "video"
        self.output_path_config = Path(config.get("output_path", "output/output.mp4"))
        self.output_dir = self.output_path_config.parent
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
        Create a video from the generated images. Uses cache if available.
        
        Args:
            image_paths (list): List of paths to generated images
            scenes (list, optional): List of scene data with text descriptions
            
        Returns:
            str: Path to the output video
        """
        if not image_paths:
            logger.error("No image paths provided for video assembly.")
            return None
        
        # --- Cache Check ---
        cache_key = None
        final_output_path = self.output_path_config # Use path from config
        
        if self.cache_manager:
            try:
                # Create a key based on image hashes and config parameters
                image_hashes = [self._get_file_hash(p) for p in image_paths if Path(p).exists()]
                scene_texts_hash = hashlib.sha256(json.dumps(scenes, sort_keys=True).encode()).hexdigest() if scenes else "no_scenes"
                
                cache_key = self.cache_manager.generate_key(
                    "assembled_video",
                    image_hashes,
                    scene_texts_hash,
                    self.scene_duration,
                    self.transition_duration,
                    self.fps,
                    tuple(self.resolution), # Needs to be hashable
                    self.use_animation,
                    # Add other relevant config options that affect output
                )
                cached_video_path = self.cache_manager.get(cache_key)
                if cached_video_path and Path(cached_video_path).exists():
                    logger.info(f"Cache hit for video assembly. Using cached video: {cached_video_path}")
                    # Ensure the final output path matches the cached one or copy it
                    if str(Path(cached_video_path).resolve()) != str(final_output_path.resolve()):
                        logger.info(f"Copying cached video to final destination: {final_output_path}")
                        shutil.copy2(cached_video_path, final_output_path)
                    return str(final_output_path)
            except Exception as e:
                logger.warning(f"Error checking or reading video assembly cache: {e}")
        # --- End Cache Check ---
        
        logger.info("Assembling video (cache miss or disabled)...")
        try:
            # Clear previous temp files
            self._clear_temp_files()
            os.makedirs(self.temp_dir, exist_ok=True) # Ensure temp dir exists
            
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
            # Assemble to a temporary path first before potentially caching
            temp_video_output = self.temp_dir / f"temp_{final_output_path.stem}.mp4"
            assembled_video_path = self._assemble_video(frame_paths, temp_video_output)
            if not assembled_video_path:
                raise ValueError("Video assembly using ffmpeg failed.")
            
            # Add text overlays if scenes data is provided
            if scenes:
                # This might modify the video file, so do it before caching/moving
                final_video_path_step = self._add_text_overlays(assembled_video_path, scenes)
                if not final_video_path_step:
                    logger.warning("Failed to add text overlays, returning video without text.")
                    final_video_path_step = assembled_video_path # Use the non-overlayed video
            else:
                final_video_path_step = assembled_video_path
            
            # Move final video to target location
            shutil.move(final_video_path_step, final_output_path)
            logger.info(f"Video successfully assembled and moved to: {final_output_path}")
            
            # --- Cache Store ---
            if self.cache_manager and cache_key:
                try:
                    # Cache the path to the final video file
                    self.cache_manager.set(cache_key, str(final_output_path))
                    logger.info(f"Cached assembled video path for key: {cache_key}")
                except Exception as e:
                    logger.warning(f"Error writing assembled video path to cache: {e}")
            # --- End Cache Store ---
            
            return str(final_output_path)
        except Exception as e:
            logger.error(f"Error creating video: {e}", exc_info=True)
            return self._create_fallback_video(image_paths)
        finally:
            # Clean up temp frame files regardless of success/failure/cache
            self._clear_temp_files()
    
    def _get_file_hash(self, file_path):
        """Calculates SHA256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            logger.warning(f"File not found for hashing: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            return None
    
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
    
    def _assemble_video(self, frame_paths, output_video_path):
        """
        Assemble frames into a video using ffmpeg
        
        Args:
            frame_paths (list): List of paths to generated frames
            output_video_path (Path): Path to save the output video
            
        Returns:
            str or None: Path to the output video or None on failure
        """
        list_file_path = None # Define outside try to ensure it's available in finally
        if not frame_paths:
            logger.error("No frames provided for video assembly")
            return None
        
        logger.info(f"Assembling {len(frame_paths)} frames into video: {output_video_path}")
        
        try:
            # Create a temporary file listing the frames for ffmpeg
            list_file_path = self.temp_dir / "framelist.txt"
            with open(list_file_path, "w") as f:
                for frame_path in frame_paths:
                    # Ensure paths are formatted correctly for ffmpeg
                    # Use forward slashes, escape special characters if needed
                    formatted_path = str(frame_path.resolve()).replace("\\", "/") # Corrected double backslash
                    f.write(f"file '{formatted_path}'\n")
                    # Assuming duration based on FPS
                    f.write(f"duration {1.0/self.fps:.6f}\n")
            
            # Add the last frame again to ensure the list is properly terminated
            # Check if frame_paths is not empty before accessing the last element
            if frame_paths:
                last_frame_path = str(frame_paths[-1].resolve()).replace("\\", "/") # Corrected double backslash
                with open(list_file_path, "a") as f:
                    f.write(f"file '{last_frame_path}'\n")
            
            # Construct ffmpeg command
            # Using concat demuxer for precise frame control
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if exists
                "-f", "concat",
                "-safe", "0", # Allow absolute paths in list file
                "-i", str(list_file_path),
                "-vf", f"fps={self.fps},scale={self.resolution[0]}:{self.resolution[1]}:flags=lanczos",
                "-c:v", "libx264", # Video codec
                "-preset", "medium", # Encoding speed vs compression
                "-crf", "23", # Constant Rate Factor (lower value = better quality, larger file)
                "-pix_fmt", "yuv420p", # Pixel format for compatibility
                str(output_video_path)
            ]
            
            logger.debug(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
            
            result = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True # Raise exception on non-zero exit code
            )
            logger.info(f"ffmpeg finished successfully. Output: {output_video_path}")
            logger.debug(f"ffmpeg stdout:\n{result.stdout}")
            logger.debug(f"ffmpeg stderr:\n{result.stderr}")
            return str(output_video_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg command failed with exit code {e.returncode}")
            logger.error(f"ffmpeg stderr:\n{e.stderr}")
            return None
        except FileNotFoundError:
            logger.error("ffmpeg command not found. Ensure ffmpeg is installed and in PATH.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during ffmpeg execution: {e}")
            return None
        finally:
            # Clean up the temporary list file used by ffmpeg concat
            # Check if list_file_path was defined and exists
            if list_file_path and list_file_path.exists():
                 try:
                     os.remove(list_file_path)
                 except OSError:
                      # Ignore error if file doesn't exist or cannot be removed
                     pass
    
    def _add_text_overlays(self, video_path, scenes):
        """
        Add text overlays to the video
        
        Args:
            video_path (str): Path to the input video
            scenes (list): List of scene data with text descriptions
            
        Returns:
            str: Path to the output video with text overlays
        """
        subtitle_path = None # Initialize subtitle_path
        try:
            # Create output path
            input_path = Path(video_path)
            output_path = input_path.parent / f"{input_path.stem}_with_text{input_path.suffix}"
            
            # Create subtitle file
            subtitle_path = self.temp_dir / "subtitles.srt"
            self._create_subtitle_file(subtitle_path, scenes)
            
            # Prepare subtitle path for ffmpeg filter (escape special chars)
            subtitle_path_str_escaped = str(subtitle_path).replace(':', '\\:').replace('\\', '/') # Corrected double backslash
            ffmpeg_vf_filter = f"subtitles={subtitle_path_str_escaped}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&Hffffff&'"

            # Add subtitles using ffmpeg
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-i", str(input_path),  # Input video
                "-vf", ffmpeg_vf_filter, # Use the pre-formatted filter string
                "-c:a", "copy",  # Copy audio stream if present
                str(output_path)  # Output path
            ]
            
            logger.info(f"Running ffmpeg for subtitles: {' '.join(cmd)}")
            
            # Run ffmpeg
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            logger.info(f"Subtitles added successfully. Output: {output_path}")
            logger.debug(f"ffmpeg stdout:\n{result.stdout}")
            logger.debug(f"ffmpeg stderr:\n{result.stderr}")
            
            # Return the path to the new video with overlays
            return str(output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg subtitles command failed with exit code {e.returncode}")
            logger.error(f"ffmpeg stderr:\n{e.stderr}")
            return None # Return None on failure
        except FileNotFoundError:
            logger.error("ffmpeg command not found. Ensure ffmpeg is installed and in PATH.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during subtitle overlay: {e}")
            return None
        finally:
            # Clean up subtitle file
            # Check if subtitle_path was defined and exists
            if subtitle_path and subtitle_path.exists():
                try:
                    os.remove(subtitle_path)
                except OSError:
                     # Ignore error if file doesn't exist or cannot be removed
                    pass
    
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
            # Assemble a very simple slideshow as fallback
            fallback_path = self.output_dir / f"{self.output_path_config.stem}_fallback.mp4"
            logger.warning(f"Creating a simple fallback slideshow at: {fallback_path}")
            return self._create_simple_slideshow(image_paths, fallback_path)
        except Exception as e:
            logger.error(f"Error creating fallback video: {e}")
            return None
    
    def _create_simple_slideshow(self, image_paths, output_path):
        """
        Create a simple slideshow video using ffmpeg
        
        Args:
            image_paths (list): List of paths to images
            output_path (Path): Path to save the output video
            
        Returns:
            str or None: Path to the output video or None on failure
        """
        list_file_path = None # Define outside try to ensure it's available in finally
        if not image_paths:
            return None
        
        try:
            # Create input list file for ffmpeg (image per second)
            list_file_path = self.temp_dir / "fallback_framelist.txt"
            with open(list_file_path, "w") as f:
                for img_path in image_paths:
                    if Path(img_path).exists():
                        formatted_path = str(Path(img_path).resolve()).replace("\\", "/") # Corrected double backslash
                        f.write(f"file '{formatted_path}'\n")
                        f.write(f"duration 1.0\n") # Simple 1 second per image
            
            # Add last image again
            # Check if image_paths is not empty before accessing the last element
            if image_paths and Path(image_paths[-1]).exists():
                last_frame_path = str(Path(image_paths[-1]).resolve()).replace("\\", "/") # Corrected double backslash
                with open(list_file_path, "a") as f:
                    f.write(f"file '{last_frame_path}'\n")
            
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file_path),
                "-vf", f"fps={self.fps},scale={self.resolution[0]}:{self.resolution[1]}:flags=lanczos,format=yuv420p",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "28",
                str(output_path)
            ]
            
            logger.debug(f"Running ffmpeg for fallback slideshow: {' '.join(ffmpeg_cmd)}")
            
            result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            logger.info(f"Fallback slideshow created successfully: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Failed to create fallback slideshow: {e}")
            if isinstance(e, subprocess.CalledProcessError):
                logger.error(f"ffmpeg stderr: {e.stderr}")
            return None
        finally:
            # Ensure list_file_path exists before trying to remove
            # Check if list_file_path was defined and exists
            if list_file_path and list_file_path.exists():
                try:
                    os.remove(list_file_path)
                except OSError:
                     # Ignore error if file doesn't exist or cannot be removed
                    pass
    
    def _clear_temp_files(self):
        """Clear temporary files generated during assembly."""
        if self.temp_dir.exists():
            logger.debug(f"Clearing temporary video directory: {self.temp_dir}")
            for item in self.temp_dir.iterdir():
                try:
                    if item.is_file() or item.is_symlink():
                        os.remove(item)
                    elif item.is_dir():
                        shutil.rmtree(item)
                except OSError as e:
                    logger.warning(f"Could not remove temp item {item}: {e}")
            # Optionally remove the temp dir itself if empty, but often useful for debugging
            # try:
            #     self.temp_dir.rmdir()
            # except OSError:
            #     pass