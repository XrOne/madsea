# Guide des commandes Madsea

---

## Nomenclature des fichiers Madsea

Tous les fichiers générés et manipulés dans Madsea doivent respecter une nomenclature stricte pour garantir la traçabilité, l’automatisation et la cohérence des workflows.

**Format général :**
```
@episode@@sequence@-@shot@@task@_@version@@extension@
```

**Exemple IA (image générée) :**
```
E202_SQ0010-0010_AI-concept_v0001.jpg
```

### Détail des segments
- **E202** : Saison + épisode (exemple : E202 = Épisode 2, Saison 2)
- **SQ0010** : Identifiant de la séquence (numérotation à quatre chiffres, padding zéro)
- **0010** : Identifiant du plan (numérotation à quatre chiffres, padding zéro)
- **AI-concept / Animation / Layout** : Tâche concernée
    - `AI-concept` : image fixe générée par IA, à valider avant animation
    - `Animation` : plan animé (vidéo) après validation des images fixes
    - `Layout` : autre tâche de layout ou de composition
- **v0001** : Version, toujours préfixée par un « v » minuscule et quatre chiffres (ex : v0001, v0002)
- **.jpg / .png** : Extension du fichier

### Règles spécifiques IA
- Pour les tâches IA, seules deux valeurs sont autorisées pour le segment `@task@` :
    - `AI-concept` : image fixe, soumise à validation
    - `Animation` : plan animé (vidéo générée après validation)
- Exemple image fixe à valider :
    - `E202_SQ0010-0010_AI-concept_v0001.jpg`
- Exemple vidéo animée :
    - `E202_SQ0010-0010_Animation_v0001.mp4`

### Règles générales
- **Aucun espace** dans les noms de fichiers
- **Tous les segments sont obligatoires**
- **Respect strict de la casse et du nombre de chiffres**
- **Versionnement incrémental** : chaque nouvelle version d’un fichier doit incrémenter le numéro de version
- **La nomenclature s’applique à tous les assets générés (images, vidéos, exports, etc.)**

---


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