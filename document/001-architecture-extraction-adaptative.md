# 001-architecture-extraction-adaptative.md

## Objectif
Industrialiser l’extraction automatique et adaptative d’images, textes, dialogues et découpages depuis des PDF de storyboard, quelle que soit leur structure, avec gestion de profils et fallback UX.

---

### Pipeline Extraction Adaptative Madsea

1. **Import PDF storyboard**
   - Chargement du fichier PDF (PyMuPDF)
2. **Détection structurelle**
   - Analyse dynamique : nombre de pages, zones images/textes, titres, séquences
   - Heuristiques : mots-clés (Plan, Séquence, Dialogue), position, style
3. **Extraction brute**
   - Images (PyMuPDF)
   - Textes (PyMuPDF + OCR fallback)
4. **Matching images/textes**
   - Par page, par zone, par heuristique
5. **Application d’un profil d’extraction**
   - Mapping automatique si profil connu (JSON/config)
   - Si incertitude : log, proposition de correction UI
6. **Correction/validation utilisateur (si besoin)**
   - UI “drag & match” ou tableau mapping
   - Sauvegarde du nouveau profil
7. **Structuration finale**
   - Pour chaque scène/plan : {plan_id, image, texte, dialogue, découpage}
8. **Injection dans pipeline IA et front**
   - API REST backend, structuration pour front Madsea

---

## Points clés
- Extraction robuste à tout changement de format
- Correction/mapping UI rapide si parsing incertain
- Sauvegarde et réutilisation des profils d’extraction
- Documentation et traçabilité à chaque étape

*(Dernière mise à jour : 2025-04-24)*
