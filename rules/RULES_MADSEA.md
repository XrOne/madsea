# Règle Madsea – Autosauvegarde, gestion de projets et archivage

## 1. Autosauvegarde automatique par projet
- Chaque projet Madsea doit disposer d’un dossier d’autosauvegarde dédié (ex : `/backups/<project_id>/` ou `/projects/<project_id>/autosave/`).
- À chaque modification critique (édition, extraction, génération, annotation…), une version autosave est créée automatiquement.
- Les autosaves sont horodatées et conservées selon une politique FIFO (ex : 10 dernières versions par projet).
- L’utilisateur peut restaurer un projet depuis n’importe quelle autosave (UX façon “restaurer version” d’Adobe Premiere).

## 2. Gestion des projets façon ChatGPT
- Page/liste des projets avec aperçu, date de dernière modif, statut (actif, archivé).
- Possibilité d’archiver/désarchiver un projet (UX simple, accessible depuis la liste ou la fiche projet).
- Recherche, filtrage, et restauration rapide des projets archivés.

## 3. Sécurité et traçabilité
- Les autosaves ne sont jamais supprimées sans confirmation utilisateur (hors politique FIFO).
- Les autosaves sont stockées hors du dossier uploads/ pour éviter toute suppression accidentelle.
- Documentation et logs de chaque restauration/archivage.

---

**Ces règles sont obligatoires pour garantir la sécurité, la continuité et la productivité sur Madsea, même en cas de crash ou d’erreur humaine.**
