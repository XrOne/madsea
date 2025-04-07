# Guide d'Installation de Madsea

Ce guide vous aidera à installer et configurer Madsea, une plateforme de transformation de storyboards en vidéos stylisées par IA, spécialement conçue pour les artistes et créateurs.

## Prérequis

- Un ordinateur Windows 10 ou 11 (64 bits)
- Au moins 8 Go de RAM (16 Go recommandés)
- Au moins 10 Go d'espace disque libre
- Une connexion Internet
- Droits d'administrateur sur votre ordinateur

## Installation automatique (recommandée)

1. **Téléchargez** le package Madsea
2. **Décompressez** l'archive dans un dossier de votre choix
3. **Exécutez** le fichier `install_windows.bat` en tant qu'administrateur :
   - Faites un clic droit sur le fichier
   - Sélectionnez "Exécuter en tant qu'administrateur"
4. **Patientez** pendant l'installation (cela peut prendre plusieurs minutes)
5. Une fois l'installation terminée, un raccourci "Madsea" sera créé sur votre bureau

## Démarrage de Madsea

1. **Double-cliquez** sur le raccourci "Madsea" sur votre bureau
2. Deux fenêtres de commande s'ouvriront :
   - ComfyUI (moteur de génération d'images)
   - Madsea (interface principale)
3. **Ouvrez** votre navigateur web à l'adresse : http://127.0.0.1:5000
4. L'interface de Madsea est maintenant prête à être utilisée

## Configuration des modèles externes (optionnel)

Pour utiliser le style "Déclic Ombre Chinoise", vous devez configurer les modèles externes :

1. **Ouvrez** une invite de commande dans le dossier d'installation de Madsea
2. **Exécutez** la commande : `python startup.py --install-models`
3. **Suivez** les instructions pour configurer :
   - Qwen 2.1 (sera installé automatiquement via Ollama)
   - Google Gemini Studio (nécessite une clé API)
   - WAN 2.1 (nécessite une clé API)

## Utilisation de base

1. **Accédez** à l'interface web de Madsea (http://127.0.0.1:5000)
2. **Importez** votre storyboard (PDF ou images)
3. **Sélectionnez** un style visuel
4. **Lancez** la génération
5. **Visualisez** et **exportez** la vidéo générée

## Dépannage

### ComfyUI ne démarre pas

- Vérifiez que Python est correctement installé
- Assurez-vous que les dépendances sont installées : `python -m pip install -r ComfyUI/requirements.txt`

### Madsea ne se connecte pas à ComfyUI

- Vérifiez que ComfyUI est bien démarré (fenêtre de commande active)
- Assurez-vous que le port 8188 est disponible

### Problèmes avec les modèles externes

- Pour Qwen 2.1 : vérifiez qu'Ollama est correctement installé
- Pour Google Gemini et WAN 2.1 : vérifiez vos clés API

## Obtenir de l'aide

Si vous rencontrez des problèmes lors de l'installation ou de l'utilisation de Madsea :

1. Consultez le fichier `DOCUMENTATION.md` pour des informations détaillées
2. Vérifiez les logs d'installation dans le dossier `logs`
3. Contactez l'équipe de support technique

---

© 2023-2024 Projet Madsea (Storyboard-to-Video AI)