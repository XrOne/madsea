import fitz  # PyMuPDF
import os

# === CONFIGURATION ===
PDF_PATH = r'd:/madsea/pdf storyboard/E210_photoelectrique 2024-02-28 02.11.18.pdf'  # À adapter pour chaque épisode
OUTPUT_DIR = r'd:/madsea/pdf storyboard/extract'

# === EXTRACTION ===
os.makedirs(OUTPUT_DIR, exist_ok=True)
doc = fitz.open(PDF_PATH)
for page_number in range(len(doc)):
    page = doc.load_page(page_number)
    pix = page.get_pixmap(dpi=200)
    output_path = os.path.join(OUTPUT_DIR, f'page_{page_number+1}.png')
    pix.save(output_path)
    print(f'Page {page_number+1} extraite : {output_path}')
print('Extraction terminée !')
