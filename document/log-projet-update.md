# Journal de Bord - Projet Madsea

## 09/05/2025 - Industrialisation, automatisation et tests nomenclature

### Avancées majeures
- Création branche `test` sur GitHub pour sécuriser les commits ComfyUI
- Mise à jour du `.gitignore` pour exclure `ComfyUI/models/` tout en versionnant le reste de ComfyUI
- Installation et configuration de ComfyUI prêt pour l'intégration
- Tests de nomenclature réussis sur 79 plans de l'épisode E202 (16 séquences)
- Création d'un prototype Puppeteer pour automatiser ComfyUI (génération batch)
- Spécification complète de l'API `/api/generate_ai_concept` pour le frontend
- Maquette UI de sélection et configuration IA
- Plan de tests locaux validé

### Documentation produite
- `001-architecture-automatisation-madsea.md` : architecture globale front/back/puppeteer
- `002-specs-api-generate-ai.md` : API REST complète de génération IA
- `003-prototype-puppeteer-comfyui.js` : script d'automation ComfyUI
- `004-maquette-ui-selection.md` : frontend de sélection visuelle et config
- `005-plan-tests-local.md` : checklist de tests et validation

### Pipeline validé
- Extraction PDF storyboard → structure de fichiers avec nomenclature stricte
- Sélection visuelle et configuration IA (frontend)
- Génération auto (Puppeteer) ou manuelle (ComfyUI direct) 
- Feedback visuel et logs temps réel
- Structure finale respectant `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}`

### Prochaine étape
- Tests des générations ComfyUI sur batch local (3-5 plans)
- Déploiement sur cloud (RunPod) si besoin de GPU supplémentaire
- Intégration API avec le frontend DeepSite

## 09/05/2025 - Mise à jour de la structure frontend

### Structure des dossiers corrigée
- Clarification définitive sur la structure du frontend:
  - Le frontend principal est la version React/TailwindCSS dans `frontend/index.html` (DeepSite complètement migré)
  - Le dossier `front madsea` est maintenant obsolète et vide (toutes les fonctionnalités ont été migrées)
  - Toute la documentation et les workflows doivent pointer vers `frontend/index.html` comme unique interface utilisateur
  - Le nouveau frontend intègre l'interface complète avec le bridge ComfyUI

### Services actifs 
- Backend Flask : Disponible sur http://localhost:5000
  - Fournit les API d'extraction et de gestion des projets
  - Intègre le bridge pour communiquer avec ComfyUI
  - Routes principales : `/test`, `/extract`, endpoints du projet, `/api/generate_ai_concept`
- Frontend React/TailwindCSS : accessible via http://localhost:5000 ou directement via `frontend/index.html`
- ComfyUI : Accessible sur http://localhost:8188 mais généralement utilisé via le bridge

## 07/05/2025 - Structure du projet et configuration

### Structure des dossiers
- Clarification importante sur la structure du frontend:
  - Le frontend principal est désormais situé dans le dossier `frontend/` sous le nom `index.html` (ex-DeepSite migré).
  - Le dossier `front madsea` n'existe plus ou ne contient plus aucune version active du frontend.
  - Toute la documentation, les guides et les workflows doivent pointer vers `frontend/index.html` comme unique interface utilisateur.
  - Le dossier `frontend/` ne contient plus de version React/Vite active, mais la version HTML/React simple (DeepSite migré).
