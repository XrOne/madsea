# Madsea – Vision Globale, Fonctionnement, et Règles Structurantes

## 1. Vision du projet
Madsea est la plateforme centrale de génération de séquences visuelles animées à partir de storyboards, pensée pour la production scientifique/historique exigeante (ex : série Déclic saison 2). Elle garantit :
- **Fiabilité historique et scientifique** (pas d’erreur de représentation)
- **Gain de productivité** (automatisation extraction, génération IA multi-moteurs)
- **Traçabilité et validation** (workflow réalisateur, notifications, logs)
- **Ergonomie pour les artistes** (UX simple, feedback immédiat, édition facile)

## 2. Fonctionnement global
- **Import storyboard (PDF/images)**
    - Extraction automatique : images, textes, dialogues, découpage technique
    - Respect de la structure plans/séquences
- **Grille interactive**
    - Chaque carte = une scène/plan
    - Affichage/édition : hashtags, texte, dialogue, découpage, style IA
    - Sélection des images à générer
- **Gestion des styles IA**
    - Styles préconfigurés (Ombre chinoise, Labo scientifique)
    - Onglet LoRA : création/gestion de styles personnalisés via LoRA
- **Génération IA multi-moteurs**
    - Backend ComfyUI/SwarmUI, Dall-E, Midjourney, Stable Diffusion, LoRA, Civitai, etc.
    - Sélection du moteur, gestion des prompts, suivi de progression
- **Validation et notifications**
    - Workflow réalisateur : validation/rejet des images générées
    - Notifications (cloche front), retour UX immédiat
- **Export et animation**
    - Génération d’images clés, vidéo, export pour post-prod

## 3. Règles structurantes et bonnes pratiques
- **Intégration continue** : tout est dans le projet Madsea, aucune brique externe
- **Documentation systématique** : chaque étape, script, schéma, UI, API documentés dans `/document` et dans le code
- **Extraction adaptative** : pipeline auto-réévaluable, profils d’extraction, correction UI si changement de format
- **Sécurité** : backup avant toute opération critique, nettoyage automatisé, jamais d’assets générés dans Git
- **UX/ergonomie** : simplicité, feedback immédiat (toasts, logs, notifications), édition directe
- **Validation/itération** : chaque étape validée par l’équipe avant passage à la suivante

## 4. Gouvernance et évolutivité
- **Ouverture à de nouveaux moteurs IA, styles, workflows**
- **Possibilité d’intégrer de nouveaux formats storyboard via profils d’extraction**
- **Traçabilité complète (logs, notifications, validation, historique)**

---

**Ce document synthétise la vision, le fonctionnement, et les règles de Madsea, et doit être mis à jour à chaque évolution majeure.**

*(Dernière mise à jour : 2025-04-24)*
