# Journal de bord – Projet Madsea

## Suivi des décisions, évolutions et validations

- **2025-04-24** : Structuration des règles d’intégration, documentation et extraction adaptative. Vision globale et fonctionnement synthétisés dans `/document/000-vision-fonctionnement-madsea.md`. Règles formalisées dans `/rules/RULES_MADSEA.md`.
- **2025-04-24** : Début de l’industrialisation extraction adaptative (schéma pipeline extraction, prototype extraction à venir).
- **2025-04-24 17:58** : Diagnostic : Extraction JSON bloquée car le script Python n'est pas appelé correctement par le backend (problème de chemin/cwd). Le PDF source n'est pas conservé dans `/outputs`.
- **2025-04-24 18:28** : Correction : Modification de `backend/app.py` pour utiliser des chemins absolus, définir le `cwd` à la racine du projet, et copier le PDF uploadé dans `/outputs` de manière persistante. Ajout de logs et validation simple du JSON dans `front madsea/index.html`.
- **2025-04-24 18:28** : Action : Test du workflow complet upload -> extraction -> JSON -> affichage dynamique éditable.
- **2025-04-24 18:40** : Diagnostic: Le frontend appelait l'ancien endpoint `/api/upload_storyboard` au lieu de `/api/extraction_storyboard`. L'URL des images dans le code fallback était incorrecte. Correction de `index.html` pour utiliser le bon endpoint et la bonne URL de base (`http://localhost:5000`) pour le fallback.
- **2025-04-24 18:42** : Diagnostic: Fonction `window.renderScenes` manquante dans le frontend, ce qui empêchait l'affichage des scènes après extraction.
- **2025-04-24 18:48** : Implémentation: Ajout de la fonction `window.renderScenes` complète dans l'interface frontend, avec gestion de la nomenclature production suivant le standard de pipeline E202_SQ0010-0010_Concept_v0001.jpg. Ajout des champs pour type de plan, statut de production, et intégration avec le système d'autosauvegarde.
- **2025-04-25 00:05** : Diagnostic : Images non accessibles et problème de références techniques. Les images extraites sont bien générées mais non accessibles via le serveur (URL incorrectes). Les références techniques polluent la voix off.
- **2025-04-25 00:12** : Correction : Mise à jour de la fonction d'extraction pour filtrer les lignes techniques (Boards, Shots, Duration, etc.) avant la voix off. Correction du chemin des images (uploads/session-xxx/images) pour l'accessibilité web.
- **2025-04-25 00:22** : Refactorisation majeure : Modification du script d'extraction pour traiter chaque image du PDF comme plan distinct, même si plusieurs plans sont présents sur une page. Chaque image devient une entrée séparée dans le JSON avec sa nomenclature unique pipeline prod. Le texte de la page est associé à chaque image/plan.
- **2025-04-25 00:25** : Identification des prochaines étapes prioritaires : Intégration ComfyUI/SwarmUI pour génération locale, passerelle API services cloud (OpenAI, etc.), système d'autosauve FIFO, documentation exhaustive.

---

## Pipeline de Production - Nomenclature standardisée

La nomenclature suivante doit être strictement respectée pour tous les fichiers générés par Madsea:

```
@episode@@sequence@-@shot@@task@_@version@@extension@
```

**Exemples:**
- E202_SQ0010-0010_Layout_v0001.ma (3D)
- E202_SQ0010-0010_Concept_v0001.jpg (IA)

**Composants:**
- **E202**: Saison + épisode
- **SQ0010**: Identifiant de séquence (4 chiffres)
- **0010**: Identifiant de plan (4 chiffres)
- **Tâches IA disponibles:**
  - AI-Concept: Image fixe, génération qui doit être approuvée avant animation
  - Animation: Plan en mouvement
- **v0001**: Version (v minuscule obligatoire, 4 chiffres)

**Workflow de validation:**
1. Extraction du storyboard en scènes individuelles
2. Génération AI-Concept pour chaque scène
3. Validation par le réalisateur (notification status)
4. Génération Animation pour les plans validés
5. Export vers le pipeline 3D externe pour les plans complexes

---

## Plan d'implémentation - Architecture hybride local/cloud

### Autosauvegarde (priorité haute - conformité au cahier des charges)

- Mécanisme FIFO : 10 dernières versions par projet
- Structure : `/backups/<project_id>/autosave_YYYYMMDD_HHMMSS.json`
- Déclenchement : Toute modification critique (extraction, édition, génération, annotation)
- UX : Interface type Adobe Premiere pour restauration rapide

### Intégration ComfyUI & SwarmUI (priorité haute - fonctionnalité centrale)

**Phase 1 - Installation et configuration locale**
- ComfyUI : Génération locale d'images stylisées
  - Installation: `pip install comfyui`
  - Configuration: Modèles locaux Stable Diffusion 2.1, LoRA, ControlNet
  - Interface: WebAPI sur port 8188

**Phase 2 - Passerelle API services cloud**
- Intégration API OpenAI pour DALL-E 3
- Intégration API Midjourney (si besoin)
- Intégration API Runway ML (génération vidéo)

**Phase 3 - Interface de sélection de styles**
- Styles prédéfinis (silhouette cinématographique, laboratoire)
- Système d'entraînement styles personnalisés (LoRA)
- Prévisualisation et application par plan

### Génération vidéo & animations

- AnimateDiff pour animation locale simple
- WAN 2.1 pour séquence vidéo haute qualité
- Export vers pipeline 3D externe (Maya, Blender)

> Ce journal doit être mis à jour à chaque évolution majeure, décision clé, ou validation utilisateur.
