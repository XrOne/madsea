# Guide du Script `check_integrity.bat`

## Objectif
Vérifier l'intégrité de l'installation Madsea et diagnostiquer les problèmes potentiels.

## Fonctionnement Détaillé

1. **Vérification de Tesseract OCR**
   - Vérifie si Tesseract est installé et disponible dans le PATH
   - Affiche la version de Tesseract si trouvée
   - Indique comment installer Tesseract si manquant

2. **Vérification des dépendances Python**
   - Teste l'environnement virtuel backend
   - Vérifie les packages critiques (PyMuPDF, pytesseract)
   - Confirme la communication avec Tesseract depuis Python

3. **Vérification des dossiers critiques**
   - Vérifie l'existence de `temp` pour les fichiers temporaires
   - Vérifie l'existence de `uploads` pour les uploads PDF
   - Vérifie l'existence de `outputs` pour les résultats générés
   - Vérifie l'existence de `projects` pour les données projet

## Résultats possibles

### Tout est OK
```
=== Vérification intégrité Madsea ===

[1/3] Vérification Tesseract...
Tesseract 5.5.0
[2/3] Vérification Python et dépendances...
PyMuPDF 1.25.5, Tesseract 5.5.0.20241111
[3/3] Vérification dossiers critiques...
temp: OK 
uploads: OK 
outputs: OK 
projects: OK 

=== Résumé ===
Exécutez 'start_madsea.bat' si tout est OK
```

### Problèmes détectés
```
=== Vérification intégrité Madsea ===

[1/3] Vérification Tesseract...
[ERREUR] Tesseract non installé
Solution: choco install tesseract
[2/3] Vérification Python et dépendances...
[ERREUR] Dépendances manquantes
[3/3] Vérification dossiers critiques...
[ALERTE] Dossier manquant: temp
[ALERTE] Dossier manquant: uploads
outputs: OK
projects: OK

=== Résumé ===
Exécutez 'start_madsea.bat' si tout est OK
```

## Résolution des problèmes

1. **Tesseract manquant**
   - Installer via `scripts\install_tesseract.bat`
   - Ou installer manuellement depuis github.com/UB-Mannheim/tesseract/wiki

2. **Dépendances Python manquantes**
   - Exécuter `cd /d I:\Madsea\backend && .venv\Scripts\pip install -r requirements.txt`

3. **Dossiers manquants**
   - Créer avec `mkdir "I:\Madsea\temp" "I:\Madsea\uploads"`

## Exécution
```
i:\Madsea\scripts\check_integrity.bat
```

## Bonnes Pratiques
- Exécuter ce script après installation ou mise à jour
- Vérifier avant chaque session de développement
- Résoudre les problèmes détectés avant de lancer l'application