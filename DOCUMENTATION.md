# Documentation du Projet Madsea (Storyboard-to-Video AI)

## Table des matières

1. [Introduction](#introduction)
2. [Architecture du projet](#architecture-du-projet)
3. [Modules principaux](#modules-principaux)
   - [Parsing](#module-parsing)
   - [Generation](#module-generation)
   - [Styles](#module-styles)
   - [Video](#module-video)
   - [UI](#module-ui)
4. [Style Déclic Ombre Chinoise](#style-déclic-ombre-chinoise)
5. [Script de démarrage global](#script-de-démarrage-global)
6. [Modèles externes](#modèles-externes)
7. [Workflow d'utilisation](#workflow-dutilisation)
8. [Dépannage](#dépannage)

## Introduction

La plateforme Madsea (Storyboard-to-Video AI) est un outil avancé qui permet de transformer des storyboards statiques en vidéos animées stylisées. Elle utilise des technologies d'intelligence artificielle comme Stable Diffusion, ControlNet et LoRA pour générer des images de haute qualité à partir de croquis de storyboard, puis les assemble en séquences vidéo fluides.

Cette plateforme est particulièrement utile pour les créateurs de contenu, réalisateurs, animateurs et concepteurs qui souhaitent prévisualiser rapidement leurs idées ou créer des animations stylisées à partir de storyboards simples.

## Architecture du projet

Le projet Madsea suit une architecture modulaire MCP (Model-Controller-Presenter) qui sépare clairement les différentes responsabilités :

```
Madsea/
├── config/               # Fichiers de configuration
├── parsing/              # Module d'extraction de storyboards
├── generation/           # Module de génération d'images
├── styles/               # Module de gestion des styles visuels
├── video/                # Module d'assemblage vidéo
├── ui/                   # Interface utilisateur web
├── utils/                # Utilitaires communs
├── workflows/            # Templates de workflows ComfyUI
├── main.py               # Point d'entrée principal
├── startup.py            # Script de démarrage global
└── requirements.txt      # Dépendances Python
```

Les modules communiquent entre eux via des interfaces bien définies, ce qui permet une grande flexibilité et extensibilité.

## Modules principaux

### Module Parsing

Le module de parsing est responsable de l'extraction des scènes à partir de storyboards au format PDF ou d'ensembles d'images.

**Fonctionnalités principales :**
- Extraction d'images à partir de fichiers PDF (via PyMuPDF)
- Traitement et normalisation des images
- OCR pour extraire le texte intégré dans les images (via Tesseract)
- Détection et segmentation des scènes

**Classes principales :**
- `StoryboardParser` : Classe principale pour l'extraction des scènes

### Module Generation

Le module de génération est responsable de la création d'images à partir des scènes extraites du storyboard, en utilisant des modèles d'IA.

**Fonctionnalités principales :**
- Génération d'images via Stable Diffusion et ControlNet
- Application de styles visuels via LoRA
- Support pour la génération locale (via ComfyUI) et cloud (via APIs externes)
- Optimisation des prompts pour différents styles

**Classes principales :**
- `ImageGenerator` : Orchestrateur principal du processus de génération
- Générateurs spécifiques pour différentes méthodes (local, cloud, etc.)

### Module Styles

Le module de styles gère les différents styles visuels qui peuvent être appliqués aux images générées.

**Fonctionnalités principales :**
- Gestion des styles prédéfinis et personnalisés
- Configuration des paramètres de génération pour chaque style
- Support pour les modèles LoRA spécifiques aux styles

**Classes principales :**
- `StyleManager` : Gestion des styles disponibles

### Module Video

Le module vidéo est responsable de l'assemblage des images générées en séquences vidéo fluides.

**Fonctionnalités principales :**
- Création de transitions entre les scènes (cross-fade, etc.)
- Support pour les effets d'animation (via AnimateDiff)
- Export vidéo avec résolution et framerate configurables

**Classes principales :**
- `VideoAssembler` : Assemblage des images en vidéo

### Module UI

Le module UI fournit une interface web pour interagir avec la plateforme.

**Fonctionnalités principales :**
- Interface web basée sur Flask
- Intégration avec ComfyUI (SwarmUI)
- Upload de storyboards et sélection de styles
- Suivi de la progression et prévisualisation des résultats

**Composants principaux :**
- `app.py` : Application Flask principale
- `comfyui_integration.py` : Intégration avec ComfyUI

## Style Déclic Ombre Chinoise

Le style "Déclic Ombre Chinoise" est un style visuel spécial qui crée des silhouettes intégrales avec rim light et lumière cinématographique réaliste.

**Caractéristiques du style :**
- Silhouettes noires pures avec définition précise des contours
- Rim light doré intense pour séparer les sujets de l'arrière-plan
- Rayons de lumière volumétriques et brume atmosphérique
- Contraste dramatique entre lumière et ombre
- Esthétique film noir avec ombres profondes
- Ratio cinématographique 16:9

**Paramètres optimaux :**
- Modèle de base : Stable Diffusion 1.5
- CFG Scale : 10.0
- Steps : 45
- Sampler : Euler Ancestral

**Intégration avec modèles externes :**
- Google Gemini Studio : Enrichissement des prompts et génération de variations
- Qwen 2.1 : Génération de texte pour des prompts précis de silhouettes
- WAN 2.1 : Génération d'images pour le style chinois

## Script de démarrage global

Le script `startup.py` est le point d'entrée principal pour initialiser et configurer tous les composants de la plateforme.

**Fonctionnalités :**
- Initialisation de tous les modules (parsing, generation, styles, video)
- Vérification des dépendances requises
- Installation et configuration des modèles externes
- Démarrage de l'interface web

**Options de ligne de commande :**
- `--config, -c` : Chemin vers le fichier de configuration
- `--web, -w` : Démarrer l'interface web
- `--install-models, -i` : Installer et configurer les modèles externes
- `--check-dependencies, -d` : Vérifier les dépendances requises
- `--verbose, -v` : Afficher les logs détaillés

**Exemple d'utilisation :**
```bash
# Démarrer l'interface web avec la configuration par défaut
python startup.py --web

# Installer et configurer les modèles externes
python startup.py --install-models

# Vérifier les dépendances requises
python startup.py --check-dependencies

# Utiliser une configuration personnalisée et activer les logs détaillés
python startup.py --config my_config.yaml --verbose
```

## Modèles externes

La plateforme peut utiliser plusieurs modèles externes pour améliorer la génération d'images et de texte.

### Qwen 2.1

Qwen 2.1 est un modèle de génération de texte développé par Alibaba, utilisé pour créer des prompts précis pour les silhouettes.

**Configuration :**
- Installation via Ollama : `ollama pull qwen2:1.5b`
- Endpoint local : `http://localhost:11434/api/generate`

### Google Gemini Studio

Gemini Studio est un modèle multimodal de Google, utilisé pour l'enrichissement des prompts et la génération de variations.

**Configuration :**
- Nécessite une clé API Google AI Studio
- Endpoint : `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`

### WAN 2.1

WAN 2.1 est un modèle de génération d'images développé par Tencent, spécialisé dans le style chinois.

**Configuration :**
- Nécessite une clé API Tencent
- Endpoint : `https://api.tencent.com/wan/v1/images/generations`

## Workflow d'utilisation

1. **Préparation du storyboard**
   - Créer un storyboard au format PDF ou un ensemble d'images
   - S'assurer que les scènes sont clairement définies

2. **Configuration du style**
   - Sélectionner un style prédéfini ou créer un style personnalisé
   - Ajuster les paramètres selon les besoins

3. **Génération des images**
   - Uploader le storyboard via l'interface web
   - Lancer le processus de génération
   - Suivre la progression en temps réel

4. **Assemblage vidéo**
   - Configurer les paramètres vidéo (durée des scènes, transitions, etc.)
   - Lancer l'assemblage vidéo
   - Télécharger le résultat final

## Dépannage

### Problèmes courants

1. **Erreur d'OCR**
   - Vérifier que Tesseract OCR est correctement installé
   - Essayer d'améliorer la qualité des images du storyboard

2. **Erreur de génération d'images**
   - Vérifier que ComfyUI est en cours d'exécution
   - Vérifier que les modèles nécessaires sont installés
   - Ajuster les paramètres de génération

3. **Erreur d'assemblage vidéo**
   - Vérifier que FFmpeg est correctement installé
   - Vérifier que les images générées sont disponibles

4. **Modèles externes non accessibles**
   - Vérifier les clés API et leur validité
   - Vérifier la connexion réseau
   - Pour Qwen, vérifier qu'Ollama est en cours d'exécution

### Logs

Les logs détaillés sont disponibles dans le fichier `madsea.log`. Activez le mode verbose avec l'option `--verbose` pour obtenir plus d'informations de débogage.

---

© 2023-2024 Projet Madsea (Storyboard-to-Video AI)