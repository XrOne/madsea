# Guide des commandes Madsea

Ce guide présente les principales commandes et fonctionnalités disponibles dans Madsea pour transformer vos storyboards en séquences visuelles stylisées.

## 1. Commandes de gestion de projet

### Création de projet
```
Madsea> CreerProjet "Nom du projet" --type=serie --saison=2 --episode=2
```
Crée un nouveau projet avec un nom et des paramètres spécifiques.

Options:
- `--type`: `unitaire` ou `serie` (défaut: `unitaire`)
- `--saison`: Numéro de saison (pour les séries)
- `--episode`: Numéro d'épisode (pour les séries)
- `--titre`: Titre du projet ou de l'épisode

### Sélection de projet
```
Madsea> OuvrirProjet "Nom du projet"
```
Ouvre un projet existant pour le modifier.

### Création d'épisode
```
Madsea> CreerEpisode "Titre de l'épisode" --numero=3
```
Ajoute un nouvel épisode à un projet de série.

## 2. Importation et extraction

### Import de storyboard
```
Madsea> ImporterStoryboard "chemin/vers/storyboard.pdf" [options]
```
Importe un storyboard depuis un fichier PDF ou une archive d'images.

Options:
- `--decouper`: Découpe automatiquement le storyboard en cases
- `--sequence=N`: Définit le numéro de séquence de départ
- `--plan=N`: Définit le numéro de plan de départ

### Extraction manuelle
```
Madsea> ExtraireCase page=1 x=100 y=200 largeur=400 hauteur