# TODO - Projet Madsea

## Dernière mise à jour : 2025-05-10

## 🔴 Priorités Immédiates (à compléter dans la semaine)

1. **Finalisation Module OCR Portable**
   - [x] Mise en place du gestionnaire OCR modulaire
   - [x] Intégration du mode portable pour distribution
   - [x] Documentation du module OCR
   - [ ] Tests de validation sur différentes configurations Windows

2. **Vérification Complète du Pipeline d'Extraction**
   - [x] Création des scripts de vérification d'intégrité
   - [ ] Tests systématiques sur différents types de storyboards
   - [ ] Optimisation des performances d'extraction sur fichiers volumineux

3. **Documentation Utilisateur**
   - [x] Guides d'utilisation des scripts
   - [ ] Guide complet du workflow utilisateur (extraction → génération)
   - [ ] Tutoriel vidéo des fonctionnalités clés

## 🟠 Tâches en Cours (à compléter ce mois)

1. **Amélioration UI/UX**
   - [ ] Refonte UI/UX de `frontend/index.html` pour :
     - [ ] Affichage côte à côte images extraites / IA (historique, itérations)
     - [ ] Bouton relance génération IA
     - [ ] Suppression de plans
     - [ ] Historique visible
     - [ ] Auto-save
     - [ ] Export projet

2. **Optimisation ComfyUI**
   - [ ] Finalisation des workflows ControlNet pour respect composition
   - [ ] Intégration complète des styles paramétrables
   - [ ] Mode batch processing pour génération par lots
   - [ ] Gestion des erreurs et fallbacks

3. **Respect Strict Nomenclature**
   - [x] Validation du format `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}`
   - [ ] Tests unitaires pour vérifier la nomenclature
   - [ ] Outils de correction automatique des noms de fichiers

## 🟢 Améliorations Futures

1. **Module ComfyUI Avancé**
   - [ ] Support pour styles additionnels (silhouette, labo, etc.)
   - [ ] Intégration de nouveaux modèles IA
   - [ ] Interface d'entraînement LoRA simplifiée
   - [ ] Prévisualisations rapides des styles

2. **Outils Collaboratifs**
   - [ ] Système de commentaires sur les plans
   - [ ] Partage de projets entre organisations
   - [ ] Historique des versions avec diff visuel
   - [ ] Notifications d'avancement

3. **Déploiement et Distribution**
   - [ ] Packaging en application autonome
   - [ ] Déploiement cloud optionnel
   - [ ] Support multi-plateformes (Windows, macOS)
   - [ ] Mise à jour automatique

## Notes & Rappels

- **Nomenclature standardisée** : Tous les fichiers doivent respecter le format `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}` (ex: `E202_SQ0010-0010_AI-concept_v0001.png`)
- **Structure de base** :
  - Backend Python/FastAPI avec services modulaires
  - Intégration ComfyUI pour génération d'images
  - Frontend simple pour créatifs
- **Priorités techniques** :
  - Extraction PDF multi-pages avec OCR fiable ✅
  - Interface simple pour utilisateurs créatifs
  - Styles paramétrables (silhouette, labo, etc.)
- **Organisation des fichiers** :
  - Documentation dans `doc/` et `doc/gestion/`
  - Sources dans `backend/` et `frontend/`
  - Configuration dans `config/`

---

Pour ajouter une tâche à cette liste ou signaler une tâche terminée, veuillez mettre à jour ce fichier et indiquer la date de modification.