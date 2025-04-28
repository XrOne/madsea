from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Chemin du fichier PDF à générer
pdf_path = 'test_ocr.pdf'

# Création du PDF
c = canvas.Canvas(pdf_path, pagesize=A4)
width, height = A4

# Ajout de texte à plusieurs endroits
c.setFont("Helvetica", 14)
c.drawString(100, height - 100, "Voici un exemple de texte pour test OCR")
c.setFont("Helvetica", 12)
c.drawString(100, height - 150, "Projet Madsea - Extraction de texte")
c.drawString(100, height - 180, "Test d'OCR avec PyTesseract")

# Créer une zone qui ressemble à un storyboard
c.rect(100, height - 400, 200, 150)
c.setFont("Helvetica", 8)
c.drawString(120, height - 280, "PLAN 1 - EXTÉRIEUR JOUR")
c.drawString(120, height - 300, "Travelling avant - personnage marche")

# Deuxième case de storyboard
c.rect(350, height - 400, 200, 150)
c.drawString(370, height - 280, "PLAN 2 - INTÉRIEUR NUIT")
c.drawString(370, height - 300, "Plan large - silhouette contre fenêtre")

# Sauvegarder le PDF
c.save()

print(f"PDF de test créé à {pdf_path}")
