import sys
import os
from pathlib import Path
from backend.services.extraction_service import PDFExtractor

def ensure_dir(directory):
    """Crée le répertoire si nécessaire"""
    os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: uv run scripts/test_extraction.py <pdf_path> <output_dir> [episode] [version]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    episode = sys.argv[3] if len(sys.argv) > 3 else "202"
    version = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    
    # Création automatique du dossier de sortie
    ensure_dir(output_dir)
    
    print(f"Démarrage de l'extraction du PDF: {pdf_path}")
    print(f"Dossier de sortie: {output_dir}")
    print(f"Nomenclature: E{episode}_SQxxxx-xxxx_storyboard_v{version:04d}.png")
    
    extractor = PDFExtractor()
    results = extractor.extract(pdf_path, output_dir, episode, version)
    
    print(f"\n{len(results)} panels extraits avec succès:")
    for panel in results:
        print(f"- {panel.image_path}")