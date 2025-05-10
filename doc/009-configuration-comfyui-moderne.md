# Configuration ComfyUI Moderne

## Introduction
Ce document décrit la configuration moderne de ComfyUI pour le projet Madsea, incluant l'intégration avec MCP Puppeteer pour l'automatisation one-click et les nouvelles fonctionnalités d'interface utilisateur.

## Modèles et Styles
- **Modèle Principal** : RealVisXL_V5.0
- **LoRA pour Ombre Chinoise** : shadow_style_xl.safetensors (situé dans `styles/`)
- **Workflow par Défaut** : shadow_style_xl_workflow.json (situé dans `ComfyUI/workflows/`)

## Automatisation MCP Puppeteer
- **Endpoint Backend** : `/api/puppeteer/process` pour l'automatisation one-click des workflows ComfyUI.
- **Endpoint d'Upload de Workflow** : `/api/workflow/upload` permet d'uploader des fichiers JSON de workflow.
- **Endpoint de Test d'Image** : `/api/puppeteer/process-image` permet d'uploader des images de test pour génération.
- **Configuration** : Les paramètres par défaut pour l'ombre chinoise incluent des prompts optimisés et une force LoRA de 0.8.

## Interface Utilisateur
- **Composant ConfigUploader** : Permet d'uploader des workflows JSON via l'interface.
- **Composant ImageTester** : Permet d'uploader des images de test et de voir les résultats générés.
- **Switch Auto/Manuel** : Situé dans `SceneToolbar`, bascule entre les modes de génération manuelle et automatique (MCP Puppeteer).

## Instructions
1. Lancez ComfyUI avec MCP activé sur `localhost:8188`.
2. Utilisez l'interface frontend pour uploader un workflow JSON ou une image de test.
3. Activez le mode automatique pour déclencher la génération via MCP Puppeteer.
4. Vérifiez les résultats dans le dossier `outputs`.

## Prochaines Étapes
- Ajouter des scripts de nettoyage automatique pour `outputs`.
- Archiver les dossiers obsolètes comme `Workflow`.
