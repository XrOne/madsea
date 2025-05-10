# Guide d'Installation des Dépendances Madsea

## Contexte
Pour assurer le bon fonctionnement de Madsea, plusieurs dépendances sont nécessaires à différents niveaux :
- OCR avec Tesseract
- Librairies Python pour le backend
- Node.js pour le frontend

## 1. Installation de Tesseract OCR

### Option 1 : Installation automatique (recommandée)

```batch
i:\Madsea\scripts\install_tesseract.bat
```

Ce script guide l'installation complète de Tesseract avec les langues françaises et anglaises.

### Option 2 : Installation manuelle

1. Téléchargez Tesseract 5.x depuis : https://github.com/UB-Mannheim/tesseract/wiki
2. Installez-le dans : `C:\Program Files\Tesseract-OCR\`
3. Assurez-vous de sélectionner les langues `fra` et `eng`

## 2. Dépendances Python

### Installation automatique
```batch
i:\Madsea\scripts\install_python_deps.bat
```

Ce script installera toutes les dépendances nécessaires, notamment :
- Flask et Flask-CORS pour le serveur backend
- PyMuPDF pour l'extraction PDF
- pytesseract pour l'OCR
- OpenCV pour le traitement d'image
- comfy-mcp-server pour l'intégration ComfyUI

### Installation manuelle
```batch
cd /d I:\Madsea\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Vérification de l'Installation

```batch
i:\Madsea\scripts\check_integrity.bat
```

Ce script vérifie que toutes les dépendances sont correctement installées :
- ✓ Tesseract OCR disponible
- ✓ Librairies Python installées
- ✓ Dossiers requis existants

## 4. Problèmes Connus et Solutions

### Erreur : "tesseract is not installed or it's not in your PATH"
**Solution** :
- Vérifiez que Tesseract est installé à `C:\Program Files\Tesseract-OCR\`
- Exécutez `i:\Madsea\scripts\install_tesseract.bat`
- Redémarrez votre terminal/IDE

### Erreur : "No module named X"
**Solution** :
- Exécutez `i:\Madsea\scripts\install_python_deps.bat`
- Assurez-vous d'utiliser l'environnement virtuel : `.venv\Scripts\activate`

## 5. Mode Portable pour Distribution

Pour préparer une version distribuable avec toutes les dépendances :
```batch
i:\Madsea\scripts\portable_install.bat
```

Cette version contiendra Tesseract embarqué et pourra être déployée facilement sur d'autres machines.