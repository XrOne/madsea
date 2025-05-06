# log-projet.md

## Journal de bord Madsea – Suivi des décisions clés

### 2025-05-06
- **Décision Nomenclature Placeholders :**
  - Pour les tests d'extraction et afin de fournir au réalisateur une structure de fichiers conforme, l'endpoint `upload_storyboard_v3` dans `extraction_api.py` va être modifié.
  - **Fichiers `extracted-raw` :** Nommés `E{ID_Episode}_P{NumPage4digits}-I{IndexImagePage4digits}_extracted-raw_v0001.{ext}`. (Ex: `E202_P0001-I0001_extracted-raw_v0001.png`).
  - **Placeholders `AI-concept` :** Seront des images PNG blanches. Nommés `E{ID_Episode}_SQ0010-{PlanNum4digits}_AI-concept_v0001.{ext}`.
    - `SQ0010` est la séquence par défaut pour ces placeholders initiaux.
    - `{PlanNum4digits}` s'incrémente de 10 pour chaque image extraite du PDF (0010, 0020, ...).
    - (Ex: `E202_SQ0010-0010_AI-concept_v0001.png`).
  - Cette stratégie permet de valider la nomenclature finale des `AI-concept` avec des fichiers temporaires. La véritable assignation des SQ/Plan basée sur les styles se fera plus tard.

### 2025-04-26
- **Décision** : Priorité à la finalisation du flux extraction PDF → affichage scènes (UX Deepsite, backend extraction PyMuPDF).
- **Tâche reportée** : Intégration API OpenAI/Midjourney (clé API, sélection moteur IA, fallback local/cloud, UX sécurisée) – à réaliser après le flux extraction/affichage.
- **Action** : Ajout des exigences OpenAI/Midjourney dans le cahier des charges (`003-todo-implementation.md`).
- **Note** : Schéma d’architecture, endpoints et UX pour l’intégration API IA à documenter dans une prochaine itération.

### Historique antérieur
- (À compléter rétroactivement si besoin)
