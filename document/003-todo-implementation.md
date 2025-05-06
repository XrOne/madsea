instale avec mcp 
# 003-todo-implementation.md (Mise à jour MCP)

## Suivi des tâches d’implémentation Madsea

Ce document centralise et priorise les tâches, avec une structure claire pour le suivi manuel et la collaboration avec l’agent MCP/Windsurf.

---

### 1. Audit & Stabilisation

- [x] **Audit backend**
  - [x] Réviser `app.py` et endpoints extraction
  - [ ] Vérifier et documenter toutes les dépendances (PyMuPDF, Tesseract, etc.)
  - [ ] Documenter architecture et flux réels (schéma à intégrer dans docs/MCP/diagrams/)

- [x] **Audit frontend**
  - [x] Vérifier UploadStoryboard, SceneDisplay, SceneGrid
  - [x] Identifier intégration backend
  - [ ] Lister besoins API non couverts

- [ ] **Vérification dépendances**
  - [ ] Lister bibliothèques extraction/OCR
  - [ ] Vérifier versions/compatibilités
  - [x] Fichier requirements.txt à jour ? (à revérifier)

---

### 2. Extraction Adaptative (Backend)

- [x] **Refactoring extraction**
  - [x] Modulariser extraction (fonctions autonomes, blueprints)
  - [ ] Gestion d’erreurs/logging détaillés
  - [ ] Commentaires/docstrings Google format
  - [ ] Implémenter extraction réelle (simple/OCR)
  - [ ] Extraction asynchrone (Celery/RQ) [optionnel]

- [ ] **OCR avancé**
  - [ ] Optimiser Tesseract ou autre OCR
  - [ ] Filtres prétraitement images
  - [ ] Structuration texte (type plan, dialogues, etc.)

- [ ] **2.5 Intégration Frontend `ProjectView.jsx`**
  - [ ] Passer le `projectId` et `episodeId` actifs au composant `UploadStoryboard`.
  - [ ] Implémenter le handler `onUploadSuccess` pour recevoir les scènes extraites.
  - [ ] Mettre à jour l'affichage des scènes dans `ProjectView` après une extraction réussie.

### 3. Autosauvegardes et Continuité

- [ ] **3.1 Vérification de l'implémentation existante (Backend)**
  - [ ] Tester les endpoints d'autosauvegarde (`/project/<id>/autosave`, `/project/<id>/autosaves`, `/project/<id>/restore/<version>`).
  - [ ] Vérifier la génération et restauration de versions.
  - [ ] Tester la limite FIFO (10 versions max).

- [x] **3.2 Intégration avec le workflow d'extraction (Frontend/Backend)**
  - [x] Déclencher une autosauvegarde après extraction réussie depuis `UploadStoryboard.jsx`.
  - [ ] Sauvegarder les métadonnées d'extraction pertinentes dans l'autosave.
  - [ ] Assurer la restauration complète du contexte après une restauration d'autosave.

- [ ] **3.3 UI Timeline (Frontend)**
  - [ ] Créer/Valider l'implémentation du composant `TimelineVersions`.
  - [ ] Afficher les versions avec détails (date, action, commentaire).
  - [ ] Ajouter des vignettes/previews aux versions sauvegardées.
  - [ ] Permettre la comparaison visuelle entre versions (optionnel).
  - [ ] Améliorer les notifications de sauvegarde/restauration.

### 4. Génération et Styles

- [ ] **4.1 Audit des fonctionnalités de style**
{{ ... }}
- [ ] **4.2 Génération d'images**
    - [ ] Intégrer dans l’UX frontend et backend la possibilité de saisir et stocker une clé API OpenAI (champ sécurisé, validation, feedback utilisateur)
    - [ ] Permettre la génération d’images via OpenAI (GPT-4 Vision, DALL·E, GPT-Image-1) en cloud, avec sélection du moteur (OpenAI, Midjourney, etc.)
    - [ ] Ajouter une gestion d’erreur claire si la clé n’est pas valide ou si le quota est dépassé
    - [ ] Prévoir une interface pour saisir une clé API Midjourney (ou relai Discord/Bridge)
    - [ ] Documenter la procédure pour ajouter une clé API et choisir le moteur dans l’UI
    - [ ] Permettre la sélection du moteur IA (OpenAI, Midjourney, SwarmUI, ComfyUI local) pour chaque génération
    - [ ] Assurer la compatibilité avec les flux locaux (SwarmUI, ComfyUI) et cloud (OpenAI, Midjourney)
    - [ ] Gérer la priorisation locale/cloud (fallback si absence de clé ou quota)

- [ ] **4.3 Intégration styles personnalisés**
{{ ... }}

### 5. Intégration Globale et Finalisation

- [ ] **5.1 Tests bout en bout**
  - [ ] Tester le flux complet : Upload (simple + OCR) -> Affichage Scènes -> Autosave -> Restauration.
  - [ ] Vérifier la gestion des erreurs à chaque étape (frontend et backend).
  - [ ] Valider l'interface utilisateur complète sur différents navigateurs/résolutions.

- [ ] **5.2 Documentation utilisateur**
{{ ... }}
- [ ] **5.3 Optimisations finales**
{{ ... }}

### Prochaines étapes prioritaires

1.  **IMMÉDIAT** : Finaliser l'intégration de `ProjectView.jsx` (tâche 2.5) pour afficher les scènes après upload.
2.  **COURT TERME** : Implémenter la logique d'extraction réelle (simple et OCR) dans le backend (tâche 2.1).
3.  **MOYEN TERME** : Tester et valider le système d'autosauvegarde de bout en bout (tâches 3.1, 3.2, 5.1).
4.  **MOYEN TERME** : Développer l'UI Timeline pour la gestion des versions (tâche 3.3).
5.  **LONG TERME** : Amélioration de l'OCR, génération d'images, styles personnalisés.

## Notes et dépendances

- L'audit doit précéder toute modification pour éviter les régressions
- Chaque tâche complétée doit être documentée dans `log-projet.md`
- Les modifications doivent respecter l'architecture définie dans `001-architecture-extraction-adaptative.md`
- Privilégier les améliorations incrémentales aux réécritures complètes
- **IMPORTANT :** Toujours valider les changements avec Charly avant de les appliquer.

### 6. Nomenclature & Placeholders

- [ ] **Nomenclature & Placeholders `extraction_api.py` (upload_storyboard_v3)**
  - [ ] Modifier `extraction_api.py` pour sauvegarder les images brutes (`extracted-raw`) avec la nomenclature `E{Ep}_P{Page}-I{Img}_extracted-raw_v0001.ext`.
  - [ ] Modifier `extraction_api.py` pour générer des images PNG blanches comme placeholders `AI-concept`.
  - [ ] Assurer que les placeholders `AI-concept` suivent la nomenclature `E{Ep}_SQ0010-{PlanIncr10}_AI-concept_v0001.ext`.
  - [ ] Documenter la stratégie dans `log-projet.md` et `rules.md`.