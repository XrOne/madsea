# Madsea Project

## Overview

Madsea is an innovative application designed to transform storyboards into AI-stylized visual sequences. It streamlines the pre-production workflow for creators by automating image generation while respecting artistic intent and composition.

This document provides a central hub for understanding the project's goals, architecture, and components.

## Core Features

- **Storyboard Ingestion:** Import PDF storyboards.
- **Intelligent Extraction:** Automatically extract scenes, images, and textual annotations (dialogue, actions, shot type) using OCR and layout analysis.
- **AI-Powered Styling:** Apply various pre-trained visual styles (e.g., "silhouette cinématographique") to extracted scenes.
- **Composition Respect:** Utilize techniques like ControlNet to ensure generated images adhere to the original storyboard's composition, framing, and poses.
- **Custom Style Training:** Allow users to train and integrate their own visual styles.
- **Iterative Refinement:** Provide tools for users to review, adjust, and regenerate images.
- **Standardized Nomenclature:** Enforce a clear file naming convention for all assets.
- **ComfyUI Integration:** Leverage ComfyUI for advanced image generation workflows.

## Target Users

- Film Directors
- Storyboard Artists
- Animators
- Pre-production Teams

## Project Goals

- Accelerate the creation of animatics and mood boards.
- Enable rapid visual exploration of different styles.
- Reduce manual labor in adapting storyboards to stylized visuals.
- Provide an intuitive and creative-friendly user experience.

## Navigation

- [Project Structure](project_structure.md)
- [Frontend Guide](frontend_guide.md)
- [Backend API](backend_api.md)
- [Extraction Workflow](workflow_extraction.md)
- [ComfyUI Integration Details](comfyui_integration.md) (To be created)
- [Development Log](log-projet.md)