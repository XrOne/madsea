# Journal de Bord - Projet Madsea

## 07/05/2025 - Structure du projet et configuration

### Structure des dossiers
- Clarification importante sur la structure du frontend:
  - Le frontend principal est situé dans le dossier `front madsea/` (avec un espace)
  - Il s'agit d'une implémentation HTML DeepSite qui est active et fonctionnelle avec les fichiers suivants:
    - `index.html` : Page principale
    - `preview_selection_restylage.html` et `preview_selection_restylage_auto.html` : Pages de prévisualisation
    - `validation_button.js` : Script JavaScript pour validation
  - Le dossier `frontend/` contient une implémentation React/Vite qui est actuellement désactivée
  - DeepSite est le service frontend actif, tandis que React/Vite est désactivé pour le moment

### Services actifs
- Backend Flask : Disponible sur http://localhost:5000
  - Fournit les API d'extraction et de gestion des projets
  - Routes principales : `/test`, `/extract`, endpoints du projet
- Frontend DeepSite (HTML/JS simple) : actif et fonctionnel dans `front madsea/`

### Prochaines étapes
- Tests d'extraction PDF → ComfyUI → Nomenclature standardisée
- Vérification du respect de la convention : `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}`
- Documentation de l'intégration ComfyUI avec les modèles et LoRA