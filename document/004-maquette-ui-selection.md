# 004-maquette-ui-selection.md

## Résumé exécutif
Maquette fonctionnelle de l’interface de sélection et configuration IA pour Madsea : workflow guidé, grille visuelle, sélection des plans, configuration du style et feedback temps réel.

---

## 1. Grille de sélection des plans

- Affichage en grille de toutes les images extraites du storyboard (miniatures)
- Pour chaque image :
  - Case à cocher « À générer »
  - Affichage du numéro de séquence, plan, état (à faire, généré, erreur…)
  - Aperçu du style sélectionné (Ombres Chinoises, Labo…)
  - Bouton « Prévisualiser » (ouvre un panneau latéral)

---

## 2. Panneau de configuration IA (sidebar ou modal)

- **Choix du style** (radio : Ombres Chinoises / Labo)
- **Sélection du workflow JSON** (dropdown)
- **Sliders pour les paramètres IA** (steps, CFG, LoRA strength…)
- **Toggle mode auto/manuel** (switch)
- **Bouton Générer IA** (lance la génération sur tous les plans sélectionnés)

---

## 3. Feedback & logs

- Barre de progression pour la génération batch
- Affichage des logs détaillés (succès/erreur par plan)
- Affichage des images générées à côté de la source
- Bouton « Relancer » sur chaque plan en cas d’erreur

---

## 4. Workflow utilisateur (schéma)

```mermaid
graph LR
    A[Import PDF / Nouveau projet] --> B[Extraction images/textes]
    B --> C[Grille de sélection visuelle]
    C --> D[Panneau config IA]
    D --> E[Génération IA (auto/manuel)]
    E --> F[Feedback & logs]
    F --> G[Validation / Export]
```

---

## 5. Points UX importants
- Sélection en masse possible (multi-sélection, drag)
- Feedback immédiat sur l’état de chaque plan
- Possibilité de changer le style ou workflow à la volée
- Interface adaptée aux créatifs non techniques

---

**Validation ? Questions ? Je passe au plan de tests locaux ?**
