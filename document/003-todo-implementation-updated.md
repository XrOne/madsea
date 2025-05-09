# Todo Implementation Madsea (09/05/2025)

## 1. Priorités immédiates (à faire aujourd'hui)

- [ ] **Tests ComfyUI locaux**
  - [ ] Tester la génération batch sur 3-5 plans avec le style "Ombres Chinoises"
  - [ ] Valider la nomenclature des sorties (AI-concept)
  - [ ] Mesurer la vitesse de génération/GPU (performance)

- [ ] **Commit sur la branche test**
  - [ ] Vérifier l'exclusion de `ComfyUI/models/` avec le nouveau .gitignore
  - [ ] Committer le reste de ComfyUI et les scripts d'automatisation
  - [ ] Vérifier l'intégrité du repository après commit

- [ ] **Intégration Puppeteer**
  - [ ] Installer les dépendances Node.js pour Puppeteer
  - [ ] Configurer le script Puppeteer avec les sélecteurs corrects pour ComfyUI
  - [ ] Tester le mode automatique sur 1-2 plans

## 2. Moyen terme (2-3 jours)

- [ ] **Finalisation du frontend**
  - [ ] Intégrer la grille de sélection visuelle dans le frontend actuel
  - [ ] Implémenter le panneau de configuration IA (style, workflow, params)
  - [ ] Ajouter le feedback temps réel et les logs de génération

- [ ] **Intégration backend**
  - [ ] Implémenter l'API `/api/generate_ai_concept` selon les specs
  - [ ] Connecter le backend à l'automation Puppeteer
  - [ ] Mettre en place le système de logs et suivi de batch

- [ ] **Préparation déploiement cloud**
  - [ ] Documenter la procédure de déploiement sur RunPod (ComfyUI)
  - [ ] Créer les scripts de synchronisation des modèles et workflows
  - [ ] Benchmark et optimisation des performances cloud vs local

## 3. Plus long terme (objectif 70 plans)

- [ ] **Pipeline d'assemblage vidéo**
  - [ ] Automatiser la génération des fichiers Animation à partir des AI-concept
  - [ ] Intégrer la conversion et le contrôle qualité vidéo

- [ ] **Finalisation de la documentation**
  - [ ] Créer un manuel utilisateur complet avec captures d'écran
  - [ ] Mettre à jour toute la documentation technique

- [ ] **Optimisations**
  - [ ] Implémentation du mode batch optimal (meilleur compromis vitesse/qualité)
  - [ ] Système de priorisation des plans

## Notes de production
- Le nouveau workflow doit être testé et validé sous 24h
- La nomenclature doit être respectée strictement à chaque étape
- Prévoir une démo au réalisateur pour validation des générations
- Documentation des fallbacks (API Dall-E, Krea) en cas de besoin
