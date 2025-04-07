# Madsea - Package d'Installation

## Présentation

Bienvenue dans le package d'installation de Madsea, une plateforme avancée qui transforme vos storyboards en vidéos animées stylisées grâce à l'intelligence artificielle. Ce package a été spécialement conçu pour les artistes et créateurs, sans nécessiter de connaissances techniques approfondies.

## Contenu du package

- **Scripts d'installation automatique** pour Windows
- **Interface utilisateur intuitive** basée sur ComfyUI/SwarmUI
- **Styles visuels prédéfinis**, dont le style exclusif "Déclic Ombre Chinoise"
- **Modèles d'IA** pour la génération d'images et de vidéos
- **Documentation complète** en français

## Installation rapide

1. **Exécutez** le fichier `install_windows.bat` en tant qu'administrateur
2. **Patientez** pendant l'installation des composants
3. **Lancez** Madsea via le raccourci créé sur votre bureau
4. **Accédez** à l'interface web à l'adresse http://127.0.0.1:5000

## Configuration des modèles externes (optionnel)

Pour utiliser le style "Déclic Ombre Chinoise", vous pouvez installer les modèles externes :

1. **Exécutez** le fichier `install_all_models.bat`
2. **Suivez** les instructions pour configurer les modèles externes

## Composants installés

Ce package installe automatiquement :

- **Python 3.10** (si non présent)
- **FFmpeg** pour le traitement vidéo
- **Tesseract OCR** pour l'extraction de texte
- **ComfyUI** pour la génération d'images
- **Ollama** pour le modèle Qwen 2.1
- **Toutes les dépendances Python** nécessaires

## Utilisation

Consultez le fichier `GUIDE_INSTALLATION.md` pour des instructions détaillées sur l'utilisation de Madsea.

## Dépannage

En cas de problème lors de l'installation :

1. Vérifiez les logs d'installation dans le dossier `logs`
2. Assurez-vous d'avoir exécuté les scripts en tant qu'administrateur
3. Vérifiez votre connexion Internet

## Configuration système requise

- Windows 10 ou 11 (64 bits)
- 8 Go de RAM minimum (16 Go recommandés)
- 10 Go d'espace disque libre
- Carte graphique compatible avec CUDA (recommandé mais non obligatoire)

---

© 2023-2024 Projet Madsea (Storyboard-to-Video AI)