# Guide Express : Déploiement ComfyUI sur RunPod (Cloud GPU)

## 1. Créer un compte sur https://runpod.io

## 2. Lancer une instance GPU
- Aller dans "Pods" > "Deploy a Pod"
- Choisir une carte (RTX 4090, A100, etc.)
- Sélectionner "ComfyUI serverless" ou charger votre propre template Docker

## 3. Uploader vos workflows Madsea
- Utiliser l'interface ComfyUI web (URL fournie par RunPod)
- Importer vos fichiers JSON de workflow
- Vérifier les modèles LoRA/checkpoints nécessaires

## 4. Générer vos images par batch
- Utiliser l'interface graphique ou l'API (voir comfyui_bridge.py)
- Télécharger les images générées

## 5. Rapatrier les outputs dans Madsea
- Copier les images dans la structure nomenclature
- Lancer l'assemblage vidéo si besoin

## 6. Fallback : API Dall-E 3, Krea, Freepik
- Si besoin, utiliser les APIs pour générer des images et les uploader manuellement

---

**Astuce :** Pour automatiser, adapter comfyui_bridge.py pour pointer vers l'URL cloud RunPod.
