import sys
import os
from pathlib import Path
import logging
from backend.services.extraction_service import PDFExtractor

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Extraction")

def ensure_dir(directory):
    """Crée le répertoire si nécessaire"""
    try:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Répertoire assuré: {directory}")
    except Exception as e:
        logger.error(f"Erreur lors de la création du répertoire {directory}: {e}")
        raise

def validate_pdf_path(pdf_path):
    """Valide et normalise le chemin du PDF avec gestion d'erreur améliorée"""
    # Conversion en Path pour gestion cross-platform
    path = Path(pdf_path)
    
    # Vérification que le fichier existe avec diagnostic amélioré
    if not path.exists():
        logger.error(f"ERREUR: Le fichier PDF n'existe pas: {pdf_path}")
        logger.error(f"Chemin absolu tenté: {path.absolute()}")
        logger.error(f"Chemin courant: {Path.cwd()}")
        
        # Essayons de trouver des PDF similaires dans le dossier parent
        try:
            parent_dir = path.parent
            if parent_dir.exists():
                pdf_files = list(parent_dir.glob("*.pdf"))
                if pdf_files:
                    pdf_names = "\n  - ".join([str(p.name) for p in pdf_files])
                    logger.warning(f"PDF trouvés dans {parent_dir}:\n  - {pdf_names}")
                    
                    # Si un seul PDF est trouvé, utilisons-le automatiquement
                    if len(pdf_files) == 1:
                        logger.info(f"Utilisation automatique du seul PDF trouvé: {pdf_files[0]}")
                        return str(pdf_files[0].absolute())
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de PDF alternatifs: {e}")
        
        raise FileNotFoundError(f"PDF non trouvé: {pdf_path}")
    
    # Retour du chemin absolu normalisé
    return str(path.absolute())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: uv run scripts/test_extraction.py <pdf_path> <output_dir> [episode] [version]")
        sys.exit(1)
    
    try:
        # Récupération et validation des arguments
        pdf_path = validate_pdf_path(sys.argv[1])
        output_dir = sys.argv[2]
        episode = sys.argv[3] if len(sys.argv) > 3 else "202"
        version = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        
        # Création automatique du dossier de sortie
        ensure_dir(output_dir)
        
        logger.info(f"Démarrage de l'extraction du PDF: {pdf_path}")
        logger.info(f"Dossier de sortie: {output_dir}")
        logger.info(f"Nomenclature: E{episode}_SQxxxx-xxxx_storyboard_v{version:04d}.png")
        
        # Extraction
        extractor = PDFExtractor()
        results = extractor.extract(pdf_path, output_dir, episode, version)
        
        # Affichage des résultats
        if results:
            logger.info(f"\n{len(results)} panels extraits avec succès:")
            for panel in results:
                print(f"✓ {panel.image_path}")
        else:
            logger.warning("Aucun panel extrait. Vérifiez le PDF source.")
            
    except Exception as e:
        logger.error(f"Erreur pendant l'extraction: {e}", exc_info=True)
        sys.exit(1)