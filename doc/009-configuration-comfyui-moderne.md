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
- **Switch Auto/Manuel** : Dans l'UI, bascule entre mode manuel et automatique, implémenté dans `SceneToolbar.jsx`.
- **Configuration** : Les paramètres par défaut pour l'ombre chinoise incluent des prompts optimisés et une force LoRA de 0.8.

## Interface Utilisateur
- **Composant ConfigUploader** : Permet d'uploader des workflows JSON via l'interface.
- **Composant ImageTester** : Permet d'uploader des images de test et de voir les résultats générés.
- **Composant LoRATrainer** : Permet d'entraîner un LoRA personnalisé avec upload d'images, paramètres, et suivi de progression.
- **Switch Auto/Manuel** : Situé dans `SceneToolbar`, bascule entre les modes de génération et déclenche les endpoints appropriés.
- **Feedback Amélioré** : Dans `SceneGenerationView`, affiche une barre de progression et des mises à jour en temps réel pendant la génération.

## Gestion de la Nomenclature
- **Validation Automatique** : Ajoutée dans le backend (`file_manager/mnager.py`), écriture automatique dans `log-nomenclature.csv` avec timestamp après chaque génération d'image pour assurer la conformité.

## Training LoRA Personnalisé
- **Endpoint Backend** : `/api/lora/train` reçoit un zip d'images et des paramètres (nom, epochs, learning rate), lance l'entraînement via un script externe, et retourne le modèle `.safetensors`.
- **Interface Frontend** : Via `LoRATrainer.jsx`, l'utilisateur upload un dataset d'images, définit les paramètres, et suit la progression. Le modèle entraîné est téléchargeable et peut être utilisé dans ComfyUI.
- **Instructions** : Uploadez un archive ZIP d'images, spécifiez les paramètres, lancez l'entraînement, et intégrez le modèle dans un workflow ComfyUI pour des styles personnalisés.

## Instructions Générales
1. Lancez ComfyUI avec MCP activé sur `localhost:8188`.
2. Utilisez l'interface frontend pour uploader un workflow JSON, une image de test, ou entraîner un LoRA.
3. Activez le mode automatique pour déclencher la génération via MCP Puppeteer.
4. Vérifiez les résultats dans le dossier `outputs` et consultez les logs pour toute erreur.

## Prochaines Étapes
- Installer Playwright (`npx playwright install`) pour les tests automatisés.
- Lancer ComfyUI et tester le workflow complet.
