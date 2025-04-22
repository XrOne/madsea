# Plan détaillé des modifications à apporter au front-end Madsea (pipeline Déclics)

## Objectif
Aligner l’interface utilisateur avec la vision “production SwarmUI modifié” : gestion avancée des styles (Ombres chinoises réalistes/Labo), paramétrage technique, feedback utilisateur, intégration de la todo-list MCP.

---

## 1. Accueil / Création de projet
- Ajouter un écran ou une section pour la création d’un nouveau projet.
- Permettre la sélection du style principal dès la création (Ombres chinoises réalistes / Labo scientifique).
- Afficher les presets styles disponibles (LoRA, ControlNet, prompts), possibilité de dupliquer/éditer.

## 2. Paramétrage technique avancé
- Ajouter des sliders/options pour :
    - Lumière (intensité, direction, ambiance : golden hour…)
    - Caméra (angle, profondeur de champ, perspective)
    - Profondeur (activation ControlNet depth, scribble)
- Grouper ces paramètres dans une section dédiée, accessible lors de la création ou édition d’une scène.

## 3. Gestion des styles et presets
- Section dédiée à l’upload, l’activation, le training et l’édition de LoRA.
- Possibilité d’appliquer un preset à tout le projet ou à une scène spécifique.
- Feedback visuel sur le respect du style (preview silhouette, alerte visage détecté).

## 4. Génération et post-process
- Intégrer l’application automatique du negative prompt et des presets techniques (CFG, steps, sampling, ratio).
- Ajouter des options de post-process (grain film, cohérence couleur).

## 5. Intégration de la todo-list MCP
- Afficher la liste des tâches (todo-list) du projet, avec boutons pour lancer/valider chaque étape.
- Suivi d’avancement visuel (progress bar, checklist).

## 6. Guidage utilisateur
- Ajouter des bulles d’aide, explications, workflow étape par étape pour chaque action clé.

## 7. Respect du code front existant
- Adapter tous les ajouts/modifications à la structure HTML/CSS/JS déjà en place (pas de refonte totale, rester fidèle à la maquette fournie).
- Prévoir des commentaires pour chaque modification afin de faciliter la maintenance.

---

## Sécurité et robustesse
- Vérifier la compatibilité avec les modules Cursor et Gemini 2.5.
- Ajouter des messages d’erreur clairs et des fallback si une intégration IA échoue.
- Documenter toute limitation ou bug connu lors de l’intégration.

---

**Ce plan doit servir de feuille de route pour toutes les évolutions du front Madsea.**
