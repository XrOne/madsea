import fitz  # PyMuPDF
import io
from pathlib import Path
from PIL import Image, ImageEnhance
import pytesseract
import logging
from dataclasses import dataclass

logger = logging.getLogger("extraction")

@dataclass
class ExtractedPanel:
    image_path: str
    page_num: int
    panel_num: int
    text: str = None

class PDFExtractor:
    def __init__(self, tesseract_path=None):
        self.tesseract_path = tesseract_path or r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

    def extract(self, pdf_path: str, output_dir: str, episode: str = "202", version: int = 1) -> list:
        """
        Extrait les panels avec la nomenclature stricte Madsea :
        Format: E{episode}_SQ{seq}-{plan}_{task}_v{version}.png
        """
        doc = fitz.open(pdf_path)
        panels = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            img = Image.open(io.BytesIO(pix.tobytes()))
            
            # Nomenclature stricte Madsea
            filename = f"E{episode}_SQ{page_num+1:04d}-0001_storyboard_v{version:04d}.png"
            output_path = str(Path(output_dir) / filename)
            img.save(output_path, "PNG")
            
            # OCR
            text = pytesseract.image_to_string(img, lang='fra+eng')
            
            panels.append(ExtractedPanel(
                image_path=output_path,
                page_num=page_num+1,
                panel_num=1,
                text=text
            ))
        
        doc.close()
        return panels
