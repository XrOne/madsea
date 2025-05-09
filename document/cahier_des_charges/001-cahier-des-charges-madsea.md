# Cahier des Charges – Projet Madsea (Production 70 plans vidéo IA)

## 1. Objectif Global
- Générer, valider et livrer 70 plans vidéo stylisés IA en 4 jours, avec une chaîne de production industrialisée, traçable et validable par le réalisateur.

## 2. Livrables attendus
- **Images extraites du storyboard** (PDF → PNG/JPG, nomenclature stricte)
- **Images IA-concept** (générées par ComfyUI/LoRA ou placeholders blancs)
- **Vidéos** (assemblage automatique ou upload manuel, nomenclature stricte)
- **Structure de dossiers conforme** à la nomenclature Madsea
- **Log CSV de tous les fichiers générés**
- **Scripts automatisés** (génération batch, assemblage vidéo, vérification nomenclature)
- **Guide d’utilisation cloud (RunPod/ComfyUI)**
- **Fallback API (Dall-E 3, Krea, Freepik) documenté**

## 3. Nomenclature des fichiers (exemples)
- `E202_SQ0010-0010_AI-concept_v0001.png` (image IA)
- `E202_P0001-I0001_extracted-raw_v0001.png` (image extraite)
- `E202_SQ0010-0010_Animation_v0001.mp4` (vidéo du plan)

## 4. Pipeline de production
1. **Extraction PDF** → images + textes (PyMuPDF, OCR)
2. **Génération placeholders IA-concept** (si besoin)
3. **Génération images IA** (ComfyUI local/cloud, batch, LoRA Ombres Chinoises)
4. **Assemblage vidéo** (ffmpeg/script)
5. **Fallback API cloud** (si blocage local)
6. **Validation sur la brique du réalisateur**

## 5. Contraintes & exigences
- **Délais** : 4 jours pour 70 plans vidéo
- **Robustesse** : scripts batch, logs, nomenclature stricte
- **Fallback** : API cloud, upload manuel si besoin
- **Traçabilité** : log CSV, structure de dossiers
- **Simplicité d’usage** : tout doit être validable par un non-technicien

## 6. Points de vigilance
- Respect strict de la nomenclature
- Automatisation maximale (batch, logs)
- Prévoir les alternatives cloud/API en cas de saturation locale
- Validation rapide sur la brique du réalisateur

## 7. Documents & scripts à fournir
- Cahier des charges (ce document)
- Scripts : génération batch, assemblage vidéo, vérification nomenclature
- Guide cloud RunPod/ComfyUI
- Log CSV
- Dossier de sortie prêt à livrer

---

**Ce cahier des charges doit être validé, puis suivi à la lettre pour garantir la réussite de la production Madsea.**
