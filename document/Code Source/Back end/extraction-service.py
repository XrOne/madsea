import os
import re
import fitz  # PyMuPDF
import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import Dict, List, Tuple, Optional, Any

class StoryboardExtractor:
    """
    Service d'extraction de storyboard pour Madsea
    Supporte l'extraction d'images et de texte à partir de PDF et d'images
    """
    
    def __init__(self, output_dir: str, ocr_enabled: bool = True):
        """
        Initialise le service d'extraction
        
        Args:
            output_dir: Répertoire de sortie pour les images extraites
            ocr_enabled: Activer la reconnaissance de texte (OCR)
        """
        self.output_dir = output_dir
        self.ocr_enabled = ocr_enabled
        
        # Configuration OCR
        if ocr_enabled:
            # Vérifier la présence de tesseract
            try:
                pytesseract.get_tesseract_version()
            except:
                print("AVERTISSEMENT: Tesseract OCR n'est pas installé ou inaccessible.")
                self.ocr_enabled = False
    
    def extract_from_pdf(self, pdf_path: str, project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait les images et textes d'un fichier PDF de storyboard
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            project_info: Informations sur le projet pour la nomenclature
                {
                    'project_code': 'E202',  # Code du projet/épisode
                    'starting_sequence': 1,  # Numéro de séquence de départ
                    'starting_plan': 1       # Numéro de plan de départ
                }
                
        Returns:
            Liste de dictionnaires contenant les informations de chaque scène extraite
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Le fichier PDF {pdf_path} n'existe pas")
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Ouvrir le PDF
        pdf_document = fitz.open(pdf_path)
        scenes = []
        
        # Extraire les paramètres de nomenclature
        project_code = project_info.get('project_code', 'E000')
        sequence_num = project_info.get('starting_sequence', 1)
        plan_num = project_info.get('starting_plan', 1)
        
        # Parcourir chaque page du PDF
        for page_idx, page in enumerate(pdf_document):
            print(f"Traitement de la page {page_idx + 1}/{len(pdf_document)}...")
            
            # Obtenir les images de la page
            image_list = self._extract_images_from_page(page)
            
            # Si aucune image n'est trouvée, essayer de traiter la page entière comme une image
            if not image_list:
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img_np = np.array(img)
                
                # Détecter les cases de storyboard dans l'image de la page
                boxes = self._detect_storyboard_frames(img_np)
                
                # Pour chaque case détectée
                for box_idx, box in enumerate(boxes):
                    x, y, w, h = box
                    frame_img = img_np[y:y+h, x:x+w]
                    
                    # Générer un nom de fichier basé sur la nomenclature
                    output_filename = f"{project_code}_SQ{sequence_num:04d}-{plan_num:04d}_Concept_v0001.jpg"
                    output_path = os.path.join(self.output_dir, output_filename)
                    
                    # Sauvegarder l'image
                    Image.fromarray(frame_img).save(output_path)
                    
                    # Extraire le texte si OCR est activé
                    scene_info = {
                        'id': f"scene_{page_idx}_{box_idx}",
                        'image_path': output_path,
                        'page': page_idx + 1,
                        'sequence_number': sequence_num,
                        'plan_number': plan_num,
                        'title': f"Scène {sequence_num}-{plan_num}"
                    }
                    
                    if self.ocr_enabled:
                        # Extraire le texte autour de la case
                        text_info = self._extract_text_info(img_np, box)
                        scene_info.update(text_info)
                    
                    scenes.append(scene_info)
                    plan_num += 1
            else:
                # Traiter chaque image trouvée dans la page
                for img_idx, img_info in enumerate(image_list):
                    img_data, img_bbox = img_info
                    
                    # Convertir l'image en tableau numpy
                    img = Image.open(io.BytesIO(img_data))
                    img_np = np.array(img)
                    
                    # Générer un nom de fichier basé sur la nomenclature
                    output_filename = f"{project_code}_SQ{sequence_num:04d}-{plan_num:04d}_Concept_v0001.jpg"
                    output_path = os.path.join(self.output_dir, output_filename)
                    
                    # Sauvegarder l'image
                    Image.fromarray(img_np).save(output_path)
                    
                    # Extraire le texte si OCR est activé
                    scene_info = {
                        'id': f"scene_{page_idx}_{img_idx}",
                        'image_path': output_path,
                        'page': page_idx + 1,
                        'sequence_number': sequence_num,
                        'plan_number': plan_num,
                        'title': f"Scène {sequence_num}-{plan_num}"
                    }
                    
                    if self.ocr_enabled:
                        # Extraire le texte à partir de la page du PDF autour de l'image
                        bbox = fitz.Rect(img_bbox)
                        text_blocks = page.get_text("blocks", clip=bbox.inflate(50))  # Élargir la zone de recherche
                        
                        text_info = self._process_text_blocks(text_blocks)
                        scene_info.update(text_info)
                    
                    scenes.append(scene_info)
                    plan_num += 1
            
            # À la fin de chaque page, incrémenter éventuellement la séquence
            # Cette logique peut être adaptée selon la structure du storyboard
            if (page_idx + 1) % 2 == 0:  # Par exemple, nouvelle séquence toutes les 2 pages
                sequence_num += 1
                plan_num = 1
        
        # Fermer le document PDF
        pdf_document.close()
        
        return scenes
    
    def extract_from_images(self, image_paths: List[str], project_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait les informations à partir d'une série d'images de storyboard
        
        Args:
            image_paths: Liste des chemins vers les images
            project_info: Informations sur le projet pour la nomenclature
                
        Returns:
            Liste de dictionnaires contenant les informations de chaque scène extraite
        """
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Extraire les paramètres de nomenclature
        project_code = project_info.get('project_code', 'E000')
        sequence_num = project_info.get('starting_sequence', 1)
        plan_num = project_info.get('starting_plan', 1)
        
        scenes = []
        
        # Traiter chaque image
        for img_idx, img_path in enumerate(image_paths):
            if not os.path.exists(img_path):
                print(f"AVERTISSEMENT: L'image {img_path} n'existe pas, ignorée.")
                continue
            
            print(f"Traitement de l'image {img_idx + 1}/{len(image_paths)}...")
            
            # Charger l'image
            img = cv2.imread(img_path)
            if img is None:
                print(f"AVERTISSEMENT: Impossible de lire l'image {img_path}, ignorée.")
                continue
            
            # Convertir en RGB pour traitement
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Détecter les cases de storyboard dans l'image
            boxes = self._detect_storyboard_frames(img_rgb)
            
            # Si aucune case n'est détectée, traiter l'image entière comme une case
            if not boxes:
                boxes = [(0, 0, img.shape[1], img.shape[0])]
            
            # Pour chaque case détectée
            for box_idx, box in enumerate(boxes):
                x, y, w, h = box
                frame_img = img_rgb[y:y+h, x:x+w]
                
                # Générer un nom de fichier basé sur la nomenclature
                output_filename = f"{project_code}_SQ{sequence_num:04d}-{plan_num:04d}_Concept_v0001.jpg"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Sauvegarder l'image
                Image.fromarray(frame_img).save(output_path)
                
                # Extraire le texte si OCR est activé
                scene_info = {
                    'id': f"scene_{img_idx}_{box_idx}",
                    'image_path': output_path,
                    'sequence_number': sequence_num,
                    'plan_number': plan_num,
                    'title': f"Scène {sequence_num}-{plan_num}"
                }
                
                if self.ocr_enabled:
                    text_info = self._extract_text_info(img_rgb, box)
                    scene_info.update(text_info)
                
                scenes.append(scene_info)
                plan_num += 1
            
            # Incrémenter éventuellement la séquence après chaque image
            # Cette logique peut être adaptée selon la structure du storyboard
            sequence_num += 1
            plan_num = 1
        
        return scenes
    
    def _extract_images_from_page(self, page) -> List[Tuple[bytes, Tuple[float, float, float, float]]]:
        """
        Extrait les images d'une page PDF
        
        Args:
            page: Objet page PyMuPDF
            
        Returns:
            Liste de tuples (données d'image, bbox)
        """
        image_list = []
        
        # Obtenir les images de la page
        images = page.get_images(full=True)
        
        for img_idx, img_info in enumerate(images):
            xref = img_info[0]
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Trouver la position de l'image sur la page
            for img_bbox in page.get_image_rects(xref):
                image_list.append((image_bytes, img_bbox))
        
        return image_list
    
    def _detect_storyboard_frames(self, image) -> List[Tuple[int, int, int, int]]:
        """
        Détecte les cases de storyboard dans une image
        
        Args:
            image: Image numpy RGB
            
        Returns:
            Liste de tuples (x, y, largeur, hauteur) pour chaque case détectée
        """
        # Convertir en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Appliquer un seuillage adaptatif
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Trouver les contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrer les contours pour ne garder que les rectangles qui pourraient être des cases
        boxes = []
        for contour in contours:
            # Calculer l'aire du contour
            area = cv2.contourArea(contour)
            
            # Ignorer les petits contours (bruit)
            if area < 10000:  # Valeur à ajuster selon les dimensions des images
                continue
            
            # Obtenir un rectangle englobant
            x, y, w, h = cv2.boundingRect(contour)
            
            # Vérifier le ratio hauteur/largeur (cases typiquement pas trop étroites)
            aspect_ratio = w / float(h)
            if 0.3 <= aspect_ratio <= 3.0:  # Valeurs à ajuster
                boxes.append((x, y, w, h))
        
        # Si plusieurs cases sont détectées, les trier de haut en bas, puis de gauche à droite
        if boxes:
            boxes.sort(key=lambda b: (b[1], b[0]))
        
        return boxes
    
    def _extract_text_info(self, image, box) -> Dict[str, str]:
        """
        Extrait le texte d'une image et le classifie
        
        Args:
            image: Image numpy
            box: Tuple (x, y, w, h) de la case
            
        Returns:
            Dictionnaire avec les champs textuels extraits
        """
        x, y, w, h = box
        
        # Définir une zone élargie pour chercher du texte autour de la case
        padding = 50
        img_height, img_width = image.shape[:2]
        
        # Coordonnées avec padding mais limitées aux dimensions de l'image
        text_x = max(0, x - padding)
        text_y = max(0, y - padding)
        text_w = min(img_width - text_x, w + 2 * padding)
        text_h = min(img_height - text_y, h + 2 * padding)
        
        # Extraire la région de texte
        text_region = image[text_y:text_y+text_h, text_x:text_x+text_w]
        
        # Utiliser OCR pour extraire le texte
        text = pytesseract.image_to_string(text_region, lang='fra')
        
        # Analyser le texte
        location, dialogue, indication, type_plan = self._analyze_text(text)
        
        return {
            'location': location,
            'dialogue': dialogue,
            'indication': indication,
            'type_plan': type_plan,
            'raw_text': text
        }
    
    def _process_text_blocks(self, text_blocks) -> Dict[str, str]:
        """
        Traite les blocs de texte extraits d'un PDF
        
        Args:
            text_blocks: Blocs de texte d'une page PDF
            
        Returns:
            Dictionnaire avec les champs textuels classifiés
        """
        all_text = "\n".join([block[4] for block in text_blocks])
        location, dialogue, indication, type_plan = self._analyze_text(all_text)
        
        return {
            'location': location,
            'dialogue': dialogue,
            'indication': indication,
            'type_plan': type_plan,
            'raw_text': all_text
        }
    
    def _analyze_text(self, text) -> Tuple[str, str, str, str]:
        """
        Analyse le texte pour identifier les différents éléments
        
        Args:
            text: Texte brut extrait
            
        Returns:
            Tuple (location, dialogue, indication, type_plan)
        """
        lines = text.strip().split("\n")
        location = ""
        dialogue = ""
        indication = ""
        type_plan = ""
        
        # Patterns pour détecter les différents éléments
        location_pattern = re.compile(r'(INT\.|EXT\.)\s*(.*?)(\-|$|\n)', re.IGNORECASE)
        dialogue_pattern = re.compile(r'([A-Z][A-ZÀ-Ü\s]+)\s*:\s*(.*)', re.IGNORECASE)
        plan_types = ['PL', 'PR', 'GP', 'TGP', 'PA', 'PE', 'PC', 'PD']
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Détecter le lieu (format typique: "INT. LABORATOIRE - JOUR")
            location_match = location_pattern.search(line)
            if location_match and not location:
                location = line
                continue
                
            # Détecter un dialogue (format typique: "PERSONNAGE: Texte du dialogue")
            dialogue_match = dialogue_pattern.search(line)
            if dialogue_match:
                if dialogue:
                    dialogue += "\n"
                dialogue += line
                continue
                
            # Détecter le type de plan
            for plan in plan_types:
                if plan in line.upper() and not type_plan:
                    type_plan = plan
                    break
                    
            # Si la ligne n'est ni un lieu ni un dialogue, c'est probablement une indication
            if not dialogue_match and not location_match:
                if indication:
                    indication += "\n"
                indication += line
        
        # Si aucun type de plan n'a été détecté, essayer de le déduire du contexte
        if not type_plan:
            text_lower = text.lower()
            if any(term in text_lower for term in ['gros plan', 'close-up', 'détail']):
                type_plan = 'GP'
            elif any(term in text_lower for term in ['plan large', 'wide shot']):
                type_plan = 'PL'
            elif any(term in text_lower for term in ['plan américain']):
                type_plan = 'PA'
            elif any(term in text_lower for term in ['plan rapproché']):
                type_plan = 'PR'
            else:
                type_plan = 'PL'  # Plan large par défaut
        
        return location, dialogue, indication, type_plan
        
    def auto_generate_prompt(self, scene_info: Dict[str, Any]) -> str:
        """
        Génère automatiquement un prompt pour l'IA à partir des informations de scène
        
        Args:
            scene_info: Informations de scène extraites
            
        Returns:
            Prompt textuel optimisé pour la génération d'image
        """
        # Extraire les éléments clés
        location = scene_info.get('location', '')
        dialogue = scene_info.get('dialogue', '')
        indication = scene_info.get('indication', '')
        
        # Construire le prompt en utilisant les éléments disponibles
        prompt_parts = []
        
        # Ajouter la description du lieu
        if location:
            # Nettoyer le texte (remplacer INT./EXT. par une description plus claire)
            location_clean = location.replace("INT.", "Intérieur").replace("EXT.", "Extérieur")
            prompt_parts.append(location_clean)
        
        # Ajouter les indications concernant la mise en scène
        if indication:
            # Extraire les éléments importants des indications (limiter la longueur)
            key_indications = ' '.join(indication.split()[:20])  # Limiter à environ 20 mots
            prompt_parts.append(key_indications)
        
        # Ajouter des indices d'ambiance basés sur le dialogue si disponible
        if dialogue:
            # Extraire l'émotion du dialogue
            if "?" in dialogue:
                prompt_parts.append("expression interrogative")
            elif "!" in dialogue:
                prompt_parts.append("expression intense, émotionnelle")
            else:
                prompt_parts.append("expression neutre")
        
        # Assembler le prompt final
        prompt = ", ".join(prompt_parts)
        
        # Ajouter des descripteurs de qualité standard
        prompt += ", éclairage cinématographique, rendu professionnel, haute qualité"
        
        return prompt