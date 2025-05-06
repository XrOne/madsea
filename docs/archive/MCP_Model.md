# MODEL MADSEA

## Définition
Madsea est une application de transformation de storyboards en séquences visuelles stylisées par IA.

## Architecture fondamentale
- Backend modulaire Python/FastAPI
- Intégration ComfyUI comme moteur principal
- Architecture ouverte : possibilité d’intégrer d’autres moteurs IA (SwarmUI, Dall-E, Midjourney, Stable Diffusion, etc.) selon les besoins de production ou d’innovation
- Interface simple pour créatifs non-techniciens
- Workflow linéaire d'extraction → stylisation → export

## Composants essentiels
- Service d'extraction PDF/OCR
- Service de génération d'images via ComfyUI
- Service de gestion des fichiers (nomenclature stricte)
- Interface utilisateur visuelle et intuitive
- Grille interactive (future version) : chaque scène/plan est éditable, feedback immédiat (toasts, logs, notifications HTML), sélection et édition directe des images à générer

## Valeurs fondamentales
- Respect de la composition du storyboard
- Application cohérente des styles visuels
- Traitement local (sans API externe)
- Simplicité d'utilisation pour les créatifs
