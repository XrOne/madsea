# Vérification des endpoints API Madsea

## 1. Endpoints actuels

### Backend principal (app.py)
- ✅ `/test` [GET] - Test simple de l'API

### Projects API (projects_api.py)
- ✅ `/api/projects` [GET] - Liste tous les projets
- ✅ `/api/projects` [POST] - Crée un nouveau projet
- ✅ `/api/projects/<proj_id>` [GET] - Récupère les détails d'un projet
- ✅ `/api/projects/<proj_id>/episodes` [POST] - Ajoute un épisode à un projet

### Extraction API (extraction_api.py)
- ⚠️ `/api/upload_storyboard` (défini mais incomplet) - L'endpoint est enregistré mais la fonction n'a pas de décorateur valide
- ✅ `/api/upload_storyboard_v3` [POST] - Route à créer/ajouter - Version avancée de l'extraction PDF

### ComfyUI API (comfyui_api.py)
- ✅ `/api/comfyui/process_plans` [POST] - Traite les plans via ComfyUI

### Autosave API (004-backend-autosave.py)
- ✅ `/api/autosave/<project_id>` [POST] - Crée une sauvegarde automatique
- ✅ `/api/autosave/<project_id>` [GET] - Liste les sauvegardes automatiques
- ✅ `/api/autosave/<project_id>/<version_id>` [GET] - Restaure une sauvegarde
- ✅ `/api/autosave/<project_id>/<version_id>` [DELETE] - Supprime une sauvegarde

## 2. Problèmes identifiés

1. **extraction_api.py** : L'endpoint `/api/upload_storyboard` est mal défini. Sa fonction implémentée `upload_storyboard_v3()` devrait être décorée correctement.

2. **Cohérence des endpoints** : La structure des URLs est bonne mais certains endpoints mélangent les styles (v3, sans préfixe).

## 3. Corrections nécessaires

### Extraction API
```python
# Correction prioritaire
@extraction_bp.route('/upload_storyboard_v3', methods=['POST'])
def upload_storyboard_v3():
    # Implémentation existante...
```

## 4. Recommandations

1. **Documentation API** : Créer une documentation OpenAPI/Swagger pour centraliser tous les endpoints et faciliter l'intégration.

2. **Harmonisation des versions** : 
   - Standardiser les noms d'endpoints (éviter les suffixes _v3)
   - Utiliser des préfixes de version explicites (/api/v1/...)

3. **Tester tous les endpoints** avec Postman ou un script Python dédié pour s'assurer qu'ils répondent correctement.

4. **Bridge ComfyUI** : Vérifier que le bridge est correctement connecté à l'API et documenté pour les développeurs frontend.

## 5. Prochaines étapes

1. Appliquer les corrections sur `extraction_api.py`
2. Tester l'extraction PDF vers AI-concept via le bridge ComfyUI
3. Documenter les schémas de requête et réponse pour les développeurs frontend

Ces corrections permettront d'assurer que l'API backend est stable pour l'industrialisation des 70 plans, en garantissant que les différents composants (extraction, bridge, génération) communiquent correctement.
