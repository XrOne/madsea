# backend/services/extraction_service.py
import fitz  # PyMuPDF
import io
from PIL import Image

def extract_images_from_pdf(pdf_path, output_folder):
    """
    Extrait toutes les images d'un fichier PDF et les sauvegarde dans le dossier spécifié.
    Retourne une liste de chemins vers les images extraites.
    """
    doc = fitz.open(pdf_path)
    extracted_images_paths = []
    image_count = 0

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Convertir en PIL Image pour sauvegarder en PNG
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Générer un nom de fichier simple pour l'image extraite
            # Une nomenclature plus complexe sera appliquée plus tard
            output_image_filename = f"extracted_page{page_num+1}_img{image_count+1}.png"
            output_image_path = f"{output_folder}/{output_image_filename}"
            
            pil_image.save(output_image_path, "PNG")
            extracted_images_paths.append(output_image_path)
            image_count += 1
            print(f"Image extraite : {output_image_path}")

    doc.close()
    return extracted_images_paths

if __name__ == '__main__':
    # Pour des tests directs
    # Assurez-vous d'avoir un PDF de test et un dossier de sortie
    test_pdf_path = "i:/Madsea/tests/test_files/sample_storyboard.pdf"  # À adapter
    test_output_folder = "i:/Madsea/outputs/test_extraction_output"
    
    import os
    if not os.path.exists(test_output_folder):
        os.makedirs(test_output_folder)
    
    if os.path.exists(test_pdf_path):
        extracted = extract_images_from_pdf(test_pdf_path, test_output_folder)
        print(f"{len(extracted)} images extraites de {test_pdf_path}")
    else:
        print(f"Fichier PDF de test non trouvé : {test_pdf_path}")
