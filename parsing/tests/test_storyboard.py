import unittest
from pathlib import Path
import tempfile
import os
from PIL import Image
import numpy as np

from ..parser import StoryboardParser

class TestStoryboardParser(unittest.TestCase):
    def setUp(self):
        self.config = {
            "temp_dir": "temp",
            "ocr_language": "fra"  # Français
        }
        self.parser = StoryboardParser(self.config)
        
        # Créer une image de test
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_image = self.test_dir / "test_scene.png"
        
        # Créer une image simple avec du texte
        img = Image.new('RGB', (800, 600), color='white')
        img.save(str(self.test_image))
        
    def tearDown(self):
        # Nettoyer les fichiers temporaires
        if self.test_dir.exists():
            for file in self.test_dir.glob("*"):
                file.unlink()
            self.test_dir.rmdir()
            
    def test_parse_image_directory(self):
        """Test le parsing d'un dossier d'images"""
        scenes = self.parser._parse_image_directory(self.test_dir)
        self.assertIsInstance(scenes, list)
        self.assertEqual(len(scenes), 1)
        self.assertTrue("image" in scenes[0])
        self.assertTrue("text" in scenes[0])
        
    def test_text_cleaning(self):
        """Test le nettoyage du texte"""
        dirty_text = "Test\n\nMultiple\n\n\nLines  \t  Spaces"
        clean_text = self.parser._clean_text(dirty_text)
        self.assertEqual(clean_text, "Test Multiple Lines Spaces")

if __name__ == '__main__':
    unittest.main() 