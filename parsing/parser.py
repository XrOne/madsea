#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Storyboard Parser Module

This module extracts images and text from storyboard PDFs or image sets.
It supports:
- PDF parsing using PyMuPDF
- Image extraction and processing
- OCR for text embedded in images using Tesseract
"""

import os
import logging
import tempfile
from pathlib import Path
import re
import shutil
import hashlib # Added for cache key generation

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class StoryboardParser:
    """Parser for extracting scenes from storyboard PDFs or image sets"""

    def __init__(self, config, cache_manager=None):
        """
        Initialize the storyboard parser
        
        Args:
            config (dict): Configuration dictionary
            cache_manager (CacheManager, optional): Cache manager instance.
        """
        self.config = config
        self.cache_manager = cache_manager
        self.temp_dir = Path(config.get("temp_dir", "temp")) / "parser"
        self.ocr_language = config.get("ocr_language", "eng")
        
        # Create temp directory if it doesn't exist
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Check if tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            logger.warning(f"Tesseract OCR not available: {e}")
            logger.warning("Text extraction from images may not work properly")
    
    def parse(self, storyboard_path):
        """
        Parse storyboard and extract scenes. Uses cache if available.
        
        Args:
            storyboard_path (str): Path to storyboard PDF or directory of images
            
        Returns:
            list: List of scenes, each containing image path and text
        """
        storyboard_path = Path(storyboard_path)
        
        if not storyboard_path.exists():
            raise FileNotFoundError(f"Storyboard not found: {storyboard_path}")
        
        # --- Cache Check ---
        cache_key = None
        if self.cache_manager:
            try:
                 # Create a key based on path and modification time
                 file_mod_time = storyboard_path.stat().st_mtime if storyboard_path.is_file() else None
                 # For directories, might need a more robust way to check for changes (hash of contents?)
                 cache_key = self.cache_manager.generate_key(
                     "parser_results",
                     str(storyboard_path.resolve()), # Use absolute path
                     file_mod_time,
                     self.ocr_language # Include relevant config
                 )
                 cached_scenes = self.cache_manager.get(cache_key)
                 if cached_scenes:
                     # Validate that cached image paths still exist (or handle regeneration)
                     # For simplicity, we assume cache is valid if found for now
                     logger.info(f"Cache hit for parsing storyboard: {storyboard_path}")
                     # Ensure temp dir exists even if cached
                     os.makedirs(self.temp_dir, exist_ok=True)
                     return cached_scenes
            except Exception as e:
                 logger.warning(f"Error checking or reading parser cache: {e}")
        # --- End Cache Check ---

        logger.info(f"Parsing storyboard (cache miss or disabled): {storyboard_path}")
        # Clear previous temp files *only if not using cache* (or manage temp files better)
        self._clear_temp_files() # Consider if temp files should be named based on cache key
        os.makedirs(self.temp_dir, exist_ok=True) # Ensure temp dir exists after clearing
        
        # Process based on input type
        if storyboard_path.is_file() and storyboard_path.suffix.lower() == ".pdf":
            logger.info(f"Parsing PDF storyboard: {storyboard_path}")
            scenes = self._parse_pdf(storyboard_path)
        elif storyboard_path.is_dir():
            logger.info(f"Parsing image directory: {storyboard_path}")
            scenes = self._parse_image_directory(storyboard_path)
        else:
            raise ValueError(f"Unsupported storyboard format: {storyboard_path}")
        
        logger.info(f"Extracted {len(scenes)} scenes from storyboard")

        # --- Cache Store ---
        if self.cache_manager and cache_key:
             try:
                 self.cache_manager.set(cache_key, scenes)
                 logger.info(f"Parsing results cached for key: {cache_key}")
             except Exception as e:
                 logger.warning(f"Error writing parser results to cache: {e}")
        # --- End Cache Store ---

        return scenes
    
    def _parse_pdf(self, pdf_path):
        """
        Parse PDF and extract scenes
        
        Args:
            pdf_path (Path): Path to PDF file
            
        Returns:
            list: List of scenes
        """
        scenes = []
        
        # First try with PyMuPDF for image and text extraction
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                # Extract images
                image_path = self._extract_page_image(page, page_num)
                
                # Extract text
                text = page.get_text()
                
                # If no text found, try OCR
                if not text.strip():
                    text = self._extract_text_with_ocr(image_path)
                
                scenes.append({
                    "image": str(image_path),
                    "text": text.strip(),
                    "page": page_num + 1
                })
            
            doc.close()
        except Exception as e:
            logger.error(f"Error parsing PDF with PyMuPDF: {e}")
            logger.info("Falling back to pdfplumber for extraction")
            
            # Fallback to pdfplumber
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        # Extract page as image
                        img = page.to_image(resolution=300)
                        image_path = self.temp_dir / f"scene_{page_num:04d}.png"
                        img.save(str(image_path))
                        
                        # Extract text
                        text = page.extract_text() or ""
                        
                        # If no text found, try OCR
                        if not text.strip():
                            text = self._extract_text_with_ocr(image_path)
                        
                        scenes.append({
                            "image": str(image_path),
                            "text": text.strip(),
                            "page": page_num + 1
                        })
            except Exception as e2:
                logger.error(f"Error parsing PDF with pdfplumber: {e2}")
                raise
        
        return scenes
    
    def _extract_page_image(self, page, page_num):
        """
        Extract image from PDF page
        Uses a unique name within the parser's temp directory.
        
        Args:
            page (fitz.Page): PDF page
            page_num (int): Page number
            
        Returns:
            Path: Path to extracted image
        """
        # Use a more specific temp path if multiple parsers run concurrently
        # For now, simple sequential naming within the instance's temp dir
        image_filename = f"pdf_page_{page_num:04d}.png"
        image_path = self.temp_dir / image_filename
        try:
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72)) # Higher DPI
            pix.save(str(image_path))
            logger.debug(f"Extracted image for page {page_num} to {image_path}")
            return image_path
        except Exception as e:
            logger.error(f"Failed to extract image for page {page_num}: {e}")
            return None # Return None if extraction fails
    
    def _parse_image_directory(self, dir_path):
        """
        Parse directory of images
        
        Args:
            dir_path (Path): Path to directory containing images
            
        Returns:
            list: List of scenes
        """
        scenes = []
        
        # Get all image files
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"]
        image_files = [f for f in sorted(dir_path.iterdir()) 
                      if f.is_file() and f.suffix.lower() in image_extensions]
        
        for i, img_path in enumerate(image_files):
            # Copy image to temp directory with a unique name
            temp_img_filename = f"dir_img_{i:04d}{img_path.suffix}"
            temp_img_path = self.temp_dir / temp_img_filename
            try:
                shutil.copy2(img_path, temp_img_path)
            except Exception as e:
                logger.error(f"Failed to copy image {img_path} to temp dir: {e}")
                continue # Skip this image
            
            # Extract text with OCR
            text = self._extract_text_with_ocr(temp_img_path)
            
            scenes.append({
                "image": str(temp_img_path),
                "text": text.strip(),
                "page": i + 1
            })
        
        return scenes
    
    def _extract_text_with_ocr(self, image_path):
        """
        Extract text from image using OCR
        
        Args:
            image_path (Path): Path to image
            
        Returns:
            str: Extracted text
        """
        try:
            # Open image with PIL
            image = Image.open(image_path)
            
            # Preprocess image for better OCR results
            # Convert to grayscale and apply thresholding
            img_cv = cv2.imread(str(image_path))
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            
            # Find text regions (contours)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size to find text regions
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 50 and h > 10:  # Minimum size for text regions
                    text_regions.append((x, y, w, h))
            
            # If no text regions found, process the whole image
            if not text_regions:
                text = pytesseract.image_to_string(image, lang=self.ocr_language)
            else:
                # Process each text region
                texts = []
                for x, y, w, h in text_regions:
                    roi = img_cv[y:y+h, x:x+w]
                    text = pytesseract.image_to_string(roi, lang=self.ocr_language)
                    texts.append(text)
                text = "\n".join(texts)
            
            # Clean up text
            text = self._clean_text(text)
            return text
        except Exception as e:
            logger.error(f"Error extracting text with OCR: {e}")
            return ""
    
    def _clean_text(self, text):
        """
        Clean up extracted text
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR errors
        text = text.replace('|', 'I')
        
        # Remove non-printable characters
        text = ''.join(c for c in text if c.isprintable() or c in '\n\t')
        
        return text.strip()
    
    def _clear_temp_files(self):
        """Removes files created by this parser instance in its temp subdir."""
        if self.temp_dir.exists():
            logger.debug(f"Clearing temp parser directory: {self.temp_dir}")
            try:
                # Remove the specific parser temp dir, not the root temp dir
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                logger.warning(f"Could not clear temp directory {self.temp_dir}: {e}")
        # Recreate the directory after clearing
        # os.makedirs(self.temp_dir, exist_ok=True) # Recreated in parse() if needed