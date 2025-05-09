# 001-architecture-projects-madsea.md

## Architecture gestion projets/épisodes/scènes — Madsea (v1)

### 1. Objectif business
Permettre la gestion simple et évolutive de multiples projets, épisodes et scènes dans Madsea : création, sélection, organisation, pour garantir un workflow fluide de l’import à la génération IA.

---

### 2. Workflow utilisateur
- Sidebar : onglet “Projects” (remplace “StoryFlow” par “Madsea” partout)
- Page Projects :
    - Liste des projets existants
    - Bouton “New Project”
    - Sélection d’un projet actif
- Formulaire création projet :
    - Nom du projet (ex : Déclics Saison 1)
    - Numéro d’épisode (ex : 01)
    - Nom d’épisode (ex : “Le laboratoire”)
- Sélection d’un projet/épisode = tout upload, extraction, correction, etc. sont rattachés à ce contexte

---

### 3. Structure de données locale (JSON)

```json
{
  "projects": [
    {
      "id": "proj_abc123",
      "name": "Déclics Saison 1",
      "episodes": [
        {
          "id": "ep_01",
          "number": 1,
          "name": "Le laboratoire",
          "scenes": [
            { "id": "scene_1", "name": "Ouverture", ... }
          ]
        }
      ]
    }
  ]
}
```

---

### 4. Stockage
- Fichier local `projects.json` dans le dossier Madsea
- CRUD simple, prêt à migrer vers Firebase/Supabase plus tard

---

### 5. Compatibilité future (cloud)
- Structure pensée pour être synchronisable (clé unique, champs extensibles)
- Ajout possible de tags, statut, owner, etc. sans casser la base

---

### 6. UX/UI
- Sidebar “Projects” (remplace StoryFlow → Madsea)
- Page gestion projets/épisodes
- Sélection projet/épisode = contexte courant pour toutes les opérations

---

### 7. Étapes suivantes
- Prototype UI Projects (front)
- Prototype backend CRUD local (Python/JSON)
- Intégration dans le workflow d’import et d’extraction

---

**Livrable à jour, prêt pour validation et implémentation.**
