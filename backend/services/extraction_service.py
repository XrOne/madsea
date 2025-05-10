import fitz  # PyMuPDF
import io
import os
from pathlib import Path
from PIL import Image, ImageEnhance
import pytesseract
import logging
from dataclasses import dataclass

# Configuration du logger
logger = logging.getLogger("extraction")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@dataclass
class ExtractedPanel:
    """Panel extrait avec sa nomenclature et ses métadonnées"""
    image_path: str
    page_num: int
    panel_num: int
    text: str = None
    sequence: int = None
    shot: int = None

class PDFExtractor:
    def __init__(self, tesseract_path=None):
        """
        Initialise l'extracteur PDF avec Tesseract pour l'OCR
        
        Args:
            tesseract_path: Chemin vers l'exécutable Tesseract OCR (optionnel)
        """
        # Détection automatique de Tesseract
        self.tesseract_path = tesseract_path
        if not self.tesseract_path:
            # Chemins communs pour Tesseract
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'/usr/bin/tesseract',
                r'/usr/local/bin/tesseract'
            ]
            
            # Trouver le premier chemin valide
            for path in possible_paths:
                if os.path.isfile(path):
                    self.tesseract_path = path
                    break
        
        # Configuration de Tesseract
        if self.tesseract_path:
            logger.info(f"Utilisation de Tesseract OCR: {self.tesseract_path}")
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        else:
            logger.warning("Tesseract OCR non trouvé. L'OCR ne sera pas disponible.")

    def extract(self, pdf_path: str, output_dir: str, episode: str = "202", version: int = 1) -> list:
        """
        Extrait les panels avec la nomenclature stricte Madsea
        
        Args:
            pdf_path: Chemin vers le fichier PDF (normalisé avec Path)
            output_dir: Répertoire de sortie pour les images extraites
            episode: Numéro d'épisode pour la nomenclature (ex: "666")
            version: Version pour la nomenclature (ex: 1)
            
        Returns:
            Liste d'objets ExtractedPanel avec chemins et métadonnées
            
        Format de nomenclature Madsea : E{episode}_SQ{seq}-{plan}_{task}_v{version}.png
        """
        # Conversion et validation des chemins
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        
        logger.info(f"Ouverture du PDF: {pdf_path}")
        logger.info(f"Sortie vers: {output_dir}")
        
        # Assurer que le dossier de sortie existe
        os.makedirs(output_dir, exist_ok=True)
        
        panels = []
        try:
            # Ouverture du document avec gestion d'erreur
            doc = fitz.open(str(pdf_path))
            num_pages = len(doc)
            logger.info(f"PDF ouvert avec succès: {num_pages} pages")
            
            for page_num in range(num_pages):
                logger.info(f"Traitement de la page {page_num+1}/{num_pages}")
                
                # Chargement et rendu de la page
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                img = Image.open(io.BytesIO(pix.tobytes()))
                
                # Génération du nom de fichier selon nomenclature Madsea
                sequence = page_num + 1
                shot = 1  # Par défaut, chaque page est un plan
                
                # Nomenclature stricte Madsea
                filename = f"E{episode}_SQ{sequence:04d}-{shot:04d}_storyboard_v{version:04d}.png"
                output_path = output_dir / filename
                
                # Sauvegarde avec vérification
                img.save(str(output_path), "PNG")
                logger.info(f"Image extraite: {filename}")
                
                # OCR (si Tesseract est disponible)
                text = None
                try:
                    if self.tesseract_path:
                        text = pytesseract.image_to_string(img, lang='fra+eng')
                        logger.debug(f"Texte extrait pour {filename}: {len(text)} caractères")
                except Exception as e:
                    logger.warning(f"Erreur OCR pour {filename}: {e}")
                
                # Ajout du panel à la liste des résultats
                panels.append(ExtractedPanel(
                    image_path=str(output_path),
                    page_num=page_num+1,
                    panel_num=shot,
                    text=text,
                    sequence=sequence,
                    shot=shot
                ))
            
            # Fermeture du document
            doc.close()
            logger.info(f"Extraction terminée: {len(panels)} panels extraits")
            
        except Exception as e:
            logger.error(f"Erreur pendant l'extraction: {e}", exc_info=True)
            raise
            
        return panels
