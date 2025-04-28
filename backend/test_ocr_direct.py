"""
Test direct de l'extraction PDF (incluant OCR amélioré)
Ce script valide que la fonction extract_content_from_pdf fonctionne
correctement avec le prétraitement OpenCV intégré.
"""
import os
import sys
import shutil
import tempfile

# Ajout du répertoire parent au PYTHONPATH pour trouver extraction_api
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir) 

# S'assurer que backend est dans le path si ce script est exécuté directement
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from extraction_api import extract_content_from_pdf

# Chemin vers le fichier PDF de test
PDF_PATH = r"d:\madsea\pdf storyboard\E202_nanoTech 2024-04-09 11.25.08.pdf"

def run_test_extraction(pdf_path):
    print(f"Lancement du test d'extraction sur: {pdf_path}")
    print("-" * 70)

    if not os.path.exists(pdf_path):
        print(f"ERREUR: Le fichier PDF spécifié n'existe pas:")
        print(f"'{pdf_path}'")
        return

    # Créer un dossier de sortie temporaire
    temp_output_dir = tempfile.mkdtemp(prefix="madsea_test_ocr_")
    print(f"Dossier de sortie temporaire créé : {temp_output_dir}")

    try:
        # Appeler la fonction principale d'extraction
        extracted_data = extract_content_from_pdf(pdf_path, temp_output_dir)

        # Afficher les résultats
        print("\n--- RÉSULTATS DE L'EXTRACTION ---")
        if extracted_data:
            if 'texts' in extracted_data and extracted_data['texts']:
                print("\n** Texte extrait (Natif + OCR Prétraité): **")
                full_text = "\n".join(extracted_data['texts'])
                print(full_text)
                print(f"\n(Nombre total de caractères extraits: {len(full_text)})\n")
            else:
                print("Aucun texte n'a été extrait.")

            if 'images' in extracted_data and extracted_data['images']:
                print(f"** {len(extracted_data['images'])} images ont été extraites dans {temp_output_dir} **")
                # print("Liste des images extraites:")
                # for img_info in extracted_data['images']:
                #     print(f"  - {img_info['filename']} (Panel {img_info['panel_index']}) - {img_info['size']} bytes")
            else:
                print("Aucune image n'a été extraite.")
        else:
             print("La fonction d'extraction n'a retourné aucune donnée.")

    except Exception as e:
        print(f"\n--- ERREUR PENDANT L'EXTRACTION --- ")
        import traceback
        traceback.print_exc()
        print(f"Erreur: {e}")

    finally:
        # Nettoyer le dossier temporaire
        try:
            print(f"\nNettoyage du dossier temporaire : {temp_output_dir}")
            shutil.rmtree(temp_output_dir)
            print("Nettoyage terminé.")
        except Exception as cleanup_error:
            print(f"Erreur lors du nettoyage du dossier temporaire : {cleanup_error}")

    print("-" * 70)
    print("Test d'extraction terminé.")


if __name__ == "__main__":
    # Vérification Tesseract (peut être nécessaire selon la configuration)
    # try:
    #    tess_version = pytesseract.get_tesseract_version()
    #    print(f"Version de Tesseract détectée : {tess_version}")
    # except pytesseract.TesseractNotFoundError:
    #    print("ERREUR: Tesseract non trouvé. Assurez-vous qu'il est installé et dans le PATH,")
    #    print("ou configurez pytesseract.pytesseract.tesseract_cmd")
    #    # Optionnel: Définir le chemin manuellement si nécessaire
    #    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    #    sys.exit(1)
        
    run_test_extraction(PDF_PATH)
