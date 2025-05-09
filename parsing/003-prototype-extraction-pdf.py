#!/usr/bin/env python3
"""
003-prototype-extraction-pdf.py

Prototype d’extraction adaptative d’images, textes, dialogues et découpages techniques depuis un PDF storyboard Madsea.
- Extraction images (PyMuPDF)
- Extraction textes (PyMuPDF, OCR fallback)
- Matching images/textes par page ou heuristique
- Application d’un profil de mapping (JSON/config)
- Log d’incertitude si structure inconnue
- Résultat structuré prêt pour injection dans le front/backend

Usage :
    python parsing/003-prototype-extraction-pdf.py <chemin_pdf> [--profil profil.json]

"""
import sys
import os
import fitz  # PyMuPDF
import json
import re
import datetime
from typing import List, Dict, Optional

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# --- Profil de mapping par défaut (modifiable)
DEFAULT_PROFILE = {
    "plan_id_key": ["Plan", "Scene", "Séquence"],
    "dialogue_key": ["Dialogue"],
    "decoupage_key": ["Découpage", "Technique"],
    "texte_key": ["Description", "Texte", "Note"]
}


def extract_images_and_texts(pdf_path: str, profile: Optional[Dict] = None, output_dir: str = None) -> List[Dict]:
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(pdf_path), "images")
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    results = []
    for page_num, page in enumerate(doc):
        images = page.get_images(full=True)
        # Extraction du texte de la page (pour association heuristique)
        text = page.get_text()
        # Pour chaque image trouvée sur la page, créer une entrée plan
        for img_idx, img_info in enumerate(images):
            xref = img_info[0]
            img = doc.extract_image(xref)
            img_bytes = img["image"]
            img_ext = img["ext"]
            img_filename = f"page{page_num+1}_img{img_idx+1}.{img_ext}"
            img_path = os.path.join(output_dir, img_filename)
            with open(img_path, "wb") as f:
                f.write(img_bytes)
            # Chemin relatif pour le JSON
            image_rel = os.path.relpath(img_path, start=os.path.dirname(pdf_path))
            # Associer le texte de la page à ce plan (ordre simple, à raffiner si besoin)
            results.append({
                "page": page_num + 1,
                "image_path": image_rel,
                "raw_text": text
            })
            
    # Fallback OCR si besoin (pour des pages sans texte mais avec images)
    for i, result in enumerate(results):
        if not result["raw_text"].strip() and OCR_AVAILABLE:
            try:
                # Récupérer l'image directement du chemin
                img_path = result["image_path"]
                abs_path = os.path.join(os.path.dirname(pdf_path), img_path)
                from PIL import Image
                img = Image.open(abs_path)
                text = pytesseract.image_to_string(img, lang='fra')
                result["raw_text"] = text
                print(f"[OCR] Texte extrait pour l'image {img_path}")
            except Exception as e:
                print(f"[OCR] Erreur extraction OCR : {e}")
                pass
        # Matching heuristique (profil)
        mapping = extract_structured_fields(result["raw_text"], profile or DEFAULT_PROFILE)
        result.update(mapping)
    return results


def extract_structured_fields(text: str, profile: Dict) -> Dict:
    """
    Recherche heuristique et extraction avancée des champs pour les plans de storyboard:
    - voix_off: Texte principal/dialogue du narrateur (généralement en gras dans le PDF)
    - indication_plan: EXT/INT suivi du lieu et du moment (ex: "EXT. Cinema - Today")
    - type_plan: Code du type de plan (PL, GP, PR, etc.)
    - description: Description des actions/visuels de la scène
    """
    result = {
        "voix_off": None,
        "indication_plan": None,
        "type_plan": None,
        "description": None,
        "scene_id": None
    }
    
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # Suppression des lignes techniques avant la voix off
    technical_patterns = [
        r"Boards?:", r"Shots?:", r"Duration:", r"Aspect Ratio:", r"DRAFT:", r"Page:", r"^E\d+", r"NANOTECH"]
    filtered_lines = []
    skipping = True
    for line in lines:
        if skipping and any(re.search(pat, line, re.IGNORECASE) for pat in technical_patterns):
            continue
        skipping = False
        filtered_lines.append(line)
    lines = filtered_lines
    
    # Phase 1: Extraction du numéro de scène/plan
    for i, line in enumerate(lines):
        # Recherche de patterns comme "1A", "23B", etc. (numéro de plan)
        if (len(line) <= 3 and any(c.isdigit() for c in line)) or re.match(r'^\d+[A-Z]$', line):
            result["scene_id"] = line
            break
    
    # Phase 2: Extraction indication plan (EXT/INT)
    for i, line in enumerate(lines):
        if line.startswith("EXT.") or line.startswith("INT."):
            result["indication_plan"] = line
            # Le type de plan est souvent juste après l'indication
            if i + 1 < len(lines) and len(lines[i+1]) <= 4:  # PL, PR, etc.
                result["type_plan"] = lines[i+1]
            break
    
    # Phase 3: Extraction voix off (1er paragraphe substantiel)
    voix_off_text = []
    description_text = []
    in_voix_off = True  # On commence par la voix off
    
    for line in lines:
        # Si on trouve indication plan ou type plan, on bascule en mode description
        if line == result["indication_plan"] or line == result["type_plan"]:
            in_voix_off = False
            continue
        
        # Si la ligne est vide ou très courte, on l'ignore
        if not line or len(line) < 3:
            continue
            
        # Stockage dans le bon champ
        if in_voix_off:
            voix_off_text.append(line)
        else:
            description_text.append(line)
    
    # Assemblage des textes
    if voix_off_text:
        result["voix_off"] = "\n".join(voix_off_text)
    if description_text:
        result["description"] = "\n".join(description_text)
    
    return result


def main():
    import argparse
    import re  # Ajout de re pour les expressions régulières
    parser = argparse.ArgumentParser(description="Extraction adaptative PDF storyboard Madsea")
    parser.add_argument("pdf", help="Chemin du PDF storyboard")
    parser.add_argument("--profil", help="Profil de mapping JSON", default=None)
    parser.add_argument("--output_dir", help="Dossier de sortie pour les images extraites", default="outputs")
    parser.add_argument("--episode_code", help="Code de l'épisode (ex: E202)", default="E202")
    parser.add_argument("--sequence_offset", help="Offset pour la numérotation des séquences", type=int, default=10)
    parser.add_argument("--shot_offset", help="Offset pour la numérotation des plans", type=int, default=10)
    args = parser.parse_args()
    profile = DEFAULT_PROFILE
    if args.profil and os.path.exists(args.profil):
        with open(args.profil, "r", encoding="utf-8") as f:
            profile = json.load(f)
    pdf_path = args.pdf
    output_dir = args.output_dir
    results = extract_images_and_texts(pdf_path, profile, output_dir)
    
    # Structure compatible front : chaque page = une scène avec champs structurés
    scenes = []
    for idx, page in enumerate(results):
        # Extraction structurée des champs à partir du texte brut
        fields = extract_structured_fields(page.get("raw_text", ""), profile)
        
        # Génération nomenclature selon pipeline prod
        sequence_num = args.sequence_offset + idx
        shot_num = args.shot_offset + idx
        sequence_str = f"SQ{str(sequence_num).zfill(4)}"
        shot_str = str(shot_num).zfill(4)
        
        # Construction de la scène structurée
        scene = {
            "image": page.get("image_path"),
            "scene_id": fields.get("scene_id") or f"Scene {page.get('page','')}",
            "title": f"{args.episode_code}_{sequence_str}-{shot_str}_Concept_v0001",
            "voix_off": fields.get("voix_off") or "",
            "indication_plan": fields.get("indication_plan") or "",
            "type_plan": fields.get("type_plan") or "",
            "description": fields.get("description") or "",
            # Champs supplémentaires pour nomenclature pipeline
            "episode": args.episode_code,
            "sequence": sequence_str,
            "shot": shot_str,
            "task": "Concept",
            "version": "v0001",
            "extension": ".jpg"
        }
        scenes.append(scene)
    # Ajout des métadonnées du projet
    out_json = {
        "scenes": scenes,
        "source_pdf": os.path.basename(pdf_path),
        "metadata": {
            "episode_code": args.episode_code,
            "sequence_offset": args.sequence_offset,
            "shot_offset": args.shot_offset,
            "extracted_at": datetime.datetime.now().isoformat(),
            "total_scenes": len(scenes)
        }
    }
    out_path = os.path.splitext(pdf_path)[0] + "_extraction.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_json, f, ensure_ascii=False, indent=2)
    print(f"[Extraction] JSON structuré écrit : {out_path} avec {len(scenes)} scènes")


if __name__ == "__main__":
    main()
