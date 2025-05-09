# 005-plan-tests-local.md

## Résumé exécutif
Plan de tests pour valider la chaîne locale Madsea : extraction, sélection, génération IA, nomenclature, feedback et robustesse avant passage à l’industrialisation cloud.

---

## 1. Extraction PDF & OCR
- Tester l’import d’un storyboard PDF multi-pages
- Vérifier l’extraction correcte des images et des textes (PyMuPDF, Tesseract)
- Contrôler la nomenclature des fichiers extraits (`extracted-raw`)

## 2. Sélection & configuration
- Sélectionner manuellement un sous-ensemble de plans (ex : 3–5)
- Configurer le style IA, workflow JSON et paramètres personnalisés
- Tester le toggle auto/manuel

## 3. Génération IA locale (ComfyUI)
- Lancer la génération sur les plans sélectionnés (mode auto)
- Vérifier la réception des images générées dans la nomenclature attendue (`AI-concept`)
- Tester la génération manuelle (upload dans ComfyUI, puis import dans Madsea)

## 4. Assemblage vidéo
- Utiliser le script d’assemblage pour créer une vidéo à partir des images générées
- Vérifier le nommage et la structure des fichiers vidéo (`Animation`)

## 5. Feedback & logs
- Vérifier l’affichage de la progression, logs et erreurs dans le frontend
- Relancer un plan en erreur et vérifier la robustesse du process

## 6. Validation finale
- Contrôler le log CSV et la structure de dossiers générée
- Présenter la structure au réalisateur pour validation

---

## Checklist rapide
- [ ] Extraction PDF multi-pages OK
- [ ] Sélection et config UI OK
- [ ] Génération IA auto OK
- [ ] Génération IA manuelle OK
- [ ] Nomenclature respectée partout
- [ ] Feedback/logs clairs
- [ ] Assemblage vidéo OK
- [ ] Structure validée par le réalisateur

---

**Prêt pour la validation locale : une fois tous ces points validés, passage à l’industrialisation cloud et batch !**
