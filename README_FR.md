# Madsea - Plateforme Storyboard-to-Video AI

## Présentation

Madsea est une plateforme avancée qui transforme des storyboards statiques en vidéos animées stylisées grâce à l'intelligence artificielle. Elle utilise Stable Diffusion, ControlNet et LoRA pour générer des images de haute qualité à partir de croquis, puis les assemble en séquences vidéo fluides.

## Fonctionnalités principales

- **Extraction de storyboards** : Support des formats PDF et images
- **Génération d'images IA** : Utilisation de Stable Diffusion avec ControlNet
- **Styles visuels** : Plusieurs styles prédéfinis, dont le style exclusif "Déclic Ombre Chinoise"
- **Assemblage vidéo** : Transitions fluides et effets d'animation
- **Interface web** : Interface utilisateur intuitive basée sur ComfyUI/SwarmUI
- **Intégration de modèles externes** : Support pour Qwen 2.1, Google Gemini Studio et WAN 2.1

## Installation rapide

1. Clonez le dépôt
2. Installez les dépendances : `pip install -r requirements.txt`
3. Vérifiez les dépendances système : `python startup.py --check-dependencies`
4. Configurez les modèles externes (optionnel) : `python startup.py --install-models`
5. Démarrez l'interface web : `python startup.py --web`

## Style Déclic Ombre Chinoise

Le style "Déclic Ombre Chinoise" est un style visuel exclusif qui crée des silhouettes intégrales avec rim light et lumière cinématographique réaliste. Il se caractérise par :

- Silhouettes noires pures avec définition précise des contours
- Rim light doré intense pour séparer les sujets de l'arrière-plan
- Rayons de lumière volumétriques et brume atmosphérique
- Contraste dramatique entre lumière et ombre
- Esthétique film noir avec ombres profondes
- Ratio cinématographique 16:9

## Script de démarrage global

Le script `startup.py` est le point d'entrée principal pour initialiser et configurer tous les composants de la plateforme.

```bash
# Démarrer l'interface web
python startup.py --web

# Installer les modèles externes
python startup.py --install-models

# Vérifier les dépendances
python startup.py --check-dependencies

# Mode verbeux pour le débogage
python startup.py --verbose
```

## Structure du projet

```
Madsea/
├── config/               # Fichiers de configuration
├── parsing/              # Extraction de storyboards
├── generation/           # Génération d'images
├── styles/               # Gestion des styles visuels
├── video/                # Assemblage vidéo
├── ui/                   # Interface utilisateur web
├── utils/                # Utilitaires communs
├── workflows/            # Templates de workflows ComfyUI
├── main.py               # Point d'entrée principal
├── startup.py            # Script de démarrage global
├── DOCUMENTATION.md      # Documentation complète
└── requirements.txt      # Dépendances Python
```

## Documentation

Consultez le fichier `DOCUMENTATION.md` pour une documentation complète du projet, incluant :
- Architecture détaillée
- Description des modules
- Configuration des modèles externes
- Guide de dépannage

## Prérequis système

- Python 3.8 ou supérieur
- CUDA compatible avec PyTorch (pour la génération locale)
- Tesseract OCR (pour l'extraction de texte)
- FFmpeg (pour l'assemblage vidéo)
- ComfyUI (pour l'interface web et la génération d'images)
- Ollama (optionnel, pour Qwen 2.1)

## Licence

© 2023-2024 Projet Madsea (Storyboard-to-Video AI)