# Journal de Bord - Projet Madsea

## 07/05/2025 - Structure du projet et configuration

### Structure des dossiers
- Clarification importante sur la structure du frontend:
  - Le frontend principal est désormais situé dans le dossier `frontend/` sous le nom `index.html` (ex-DeepSite migré).
  - Le dossier `front madsea` n’existe plus ou ne contient plus aucune version active du frontend.
  - Toute la documentation, les guides et les workflows doivent pointer vers `frontend/index.html` comme unique interface utilisateur.
  - Le dossier `frontend/` ne contient plus de version React/Vite active, mais la version HTML/React simple (DeepSite migré).

### Services actifs
- Backend Flask : Disponible sur http://localhost:5000
  - Fournit les API d'extraction et de gestion des projets
  - Routes principales : `/test`, `/extract`, endpoints du projet
- Frontend DeepSite (HTML/JS simple) : actif et fonctionnel dans `front madsea/`

### Prochaines étapes
- Tests d'extraction PDF → ComfyUI → Nomenclature standardisée
- Vérification du respect de la convention : `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}`
- Documentation de l'intégration ComfyUI avec les modèles et LoRA