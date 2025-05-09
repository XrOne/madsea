# 002-specs-api-generate-ai.md

## Résumé exécutif
Définition de l’API centrale permettant au frontend Madsea de piloter la génération IA des plans, en mode automatique (Puppeteer/ComfyUI) ou manuel, avec gestion stricte de la nomenclature et retour d’état détaillé.

---

## 1. Endpoint principal

### `POST /api/generate_ai_concept`

#### **Payload JSON attendu**
```json
{
  "project_id": "madsea-2025-ep202",
  "episode": "E202",
  "season": "S02",
  "sequences": [
    {
      "sequence_id": "SQ0010",
      "plans": ["0010", "0020", "0030"]
    },
    ...
  ],
  "style": "ombres_chinoises", // ou "labo"
  "workflow_json": "OmbresChinoises.json",
  "params": {
    "steps": 30,
    "cfg": 7.5,
    "lora_strength": 0.9
  },
  "mode": "auto" // ou "manuel"
}
```

#### **Explications**
- `project_id` : identifiant unique du projet Madsea
- `episode`, `season` : pour la nomenclature
- `sequences` : liste des séquences à traiter, avec plans à générer
- `style` : style IA à appliquer (Ombres Chinoises, Labo, etc.)
- `workflow_json` : nom du workflow ComfyUI à utiliser
- `params` : paramètres IA personnalisés
- `mode` : "auto" (automation Puppeteer) ou "manuel" (upload manuel)

---

### **Réponse JSON**
```json
{
  "status": "started",
  "batch_id": "abc123",
  "logs": [],
  "progress": 0,
  "results": []
}
```
- `status` : état du batch (started, running, done, error)
- `batch_id` : identifiant du batch de génération
- `logs` : messages d’avancement ou d’erreur
- `progress` : % d’avancement
- `results` : liste des fichiers générés (avec chemins et nomenclature)

---

## 2. Endpoints complémentaires

- `GET /api/generate_ai_concept/status?batch_id=...` : suivi temps réel de la progression
- `POST /api/generate_ai_concept/retry` : relancer un plan en erreur
- `POST /api/generate_ai_concept/cancel` : annuler le batch en cours

---

## 3. Points de validation
- Respect strict de la nomenclature pour chaque fichier généré
- Logs détaillés pour chaque plan (succès/échec)
- Possibilité de relancer individuellement un plan
- Retour d’état en temps réel pour feedback frontend

---

**Validation ? Questions ? Je passe au prototype Puppeteer ComfyUI ?**
