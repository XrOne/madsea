# Guide du Script `portable_install.bat`

## Objectif
Préparer une version portable et distribuable de Madsea pour d'autres organisations, incluant Tesseract OCR embarqué.

## Fonctionnement Détaillé

1. **Préparation de l'environnement portable**
   - Crée une structure de dossiers dans `i:\Madsea\portable`
   - Configure le dossier OCR embarqué pour Tesseract

2. **Copie de Tesseract embarqué**
   - Détecte Tesseract sur le système actuel
   - Copie uniquement les fichiers essentiels (exécutable, DLLs)
   - Copie les données de langues (français, anglais)

3. **Configuration adaptative**
   - Crée un fichier `ocr_config.json` adapté pour le mode portable
   - Configure l'application pour chercher Tesseract en priorité dans le dossier embarqué

4. **Script de démarrage portable**
   - Crée `start_madsea_portable.bat` qui configure l'environnement
   - Ajoute Tesseract embarqué au PATH temporairement
   - Lance l'application standard avec la configuration portable

## Structure créée
```
i:\Madsea\portable\
├── ocr\                   # Tesseract embarqué
│   ├── tesseract.exe      # Exécutable principal
│   ├── *.dll              # Bibliothèques requises
│   └── tessdata\          # Données de langues
│       ├── fra.traineddata
│       └── eng.traineddata
├── config\
│   └── ocr_config.json    # Configuration pour mode embarqué
└── start_madsea_portable.bat  # Script de lancement portable
```

## Distribution à d'autres organisations

### Pour préparer la distribution :
```
i:\Madsea\scripts\portable_install.bat
```

### Pour l'organisation cliente :
1. Copier le dossier Madsea complet
2. Exécuter `portable\start_madsea_portable.bat`

## Avantages du mode portable
- Aucune installation de Tesseract requise sur la machine cliente
- Configuration automatique des chemins
- Expérience identique au système principal
- Maintenance simplifiée (mise à jour d'un seul dossier)

## Considérations techniques
- Taille approximative du package portable : ~40 MB (avec les données fra+eng)
- Compatible avec Windows 10/11
- L'organisation cible a besoin de Python 3.10+ et Node.js pour le développement