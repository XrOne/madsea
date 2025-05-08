# Frontend Guide (index.html)

This document describes the structure and functionality of the Madsea frontend, currently implemented within `frontend/index.html` using React (via CDN) and TailwindCSS.

## Overview

The frontend provides an interface for users to manage projects, upload storyboards, view extracted scenes, and initiate AI image generation.

## Main Components (React)

- **`App`**: The root component, managing global state and orchestrating other components.
    - **State:** `projects`, `activeProject`, `activeEpisode`, `scenes`, `selectedScenes`, `notifications`, `viewMode`, etc.
    - **Functions:** Handles project/episode creation, selection, storyboard uploads, scene selection, communication with backend.

- **`AppContext`**: React Context used to provide global state and actions to nested components.

- **`Sidebar`**: Displays the list of projects and episodes. Allows project/episode creation and selection.
    - `ProjectList`: Renders individual projects.
    - `EpisodeList`: Renders episodes for the active project.

- **`MainContent`**: The primary area for user interaction.
    - **`UploadArea`**: Component for uploading storyboard PDFs. Displays context of active project/episode for the upload.
    - **`SceneToolbar`**: Provides controls for managing scenes (e.g., view mode toggle Grid/List).
    - **`SceneGrid` / `SceneList`**: Displays extracted scenes (images and data).
        - Each scene card/row shows:
            - Extracted raw image.
            - AI concept placeholder image.
            - Plan number.
            - **Editable Sequence Number:** Allows users to adjust the sequence number post-extraction (format: `SQxxxx`).
            - Filenames (original and AI concept).
            - Extracted voice-over text.
            - Checkbox for selection.
    - **`PlanActions`**: Buttons that appear when scenes are loaded.
        - "Envoyer à ComfyUI": Logs selected plan details to the console (placeholder for actual ComfyUI integration).
        - "Exporter Sélection": Logs selected plan details to the console (placeholder for local export functionality).

- **`Modal`**: Generic modal component used for various pop-ups (e.g., new project/episode creation).

- **`NotificationCenter`**: Displays success, error, warning, or info messages to the user.

## Workflow

1.  **Project/Episode Management:**
    *   User creates a new project (e.g., "P001_MaProduction", type "Film" or "Série").
    *   If "Série", a season number can be specified (e.g., "S01").
    *   User creates one or more episodes within a project (e.g., "E0101_NomEpisode").
    *   The active project and episode set the context for uploads.

2.  **Storyboard Upload:**
    *   User selects an active episode.
    *   User drags & drops or selects a PDF storyboard file in the `UploadArea`.
    *   The frontend sends the file along with `project_id`, `episode_id`, and a default `sequence_number` (e.g., from active episode's number or `SQ0010`) to the backend's `/upload_storyboard` endpoint.

3.  **Scene Display and Refinement:**
    *   The backend processes the PDF, extracts images and text, and creates placeholder AI concept files.
    *   The frontend receives a list of scene data and displays them in `SceneGrid` or `SceneList`.
    *   Each scene shows:
        *   The extracted image.
        *   A placeholder for the AI-generated image.
        *   Associated metadata: plan number, filenames.
        *   An **editable sequence number field** (e.g., initialized to `SQ0010`, user can change to `SQ0020`).
        *   Extracted voice-over text.
    *   Users can select individual scenes using checkboxes.

4.  **Actions on Selected Scenes:**
    *   **"Envoyer à ComfyUI"**: Gathers data for selected scenes (including the potentially modified sequence numbers and paths to extracted raw images) and logs it. This will later trigger the ComfyUI workflow.
    *   **"Exporter Sélection"**: Gathers data for selected scenes for local export (functionality to be fully defined).

## Key Data Structures (Frontend State)

-   **`projects`**: Array of project objects.
    ```json
    [{
      "id": "P001_MaProd", 
      "name": "Ma Production", 
      "type": "Film", // "Série"
      "season_number": "1", // if type is "Série"
      "episodes": [
        {"id": "E0101_Intro", "name": "Introduction", "number": "SQ0010"} 
      ]
    }]
    ```
-   **`scenes`**: Array of scene objects (after extraction).
    ```json
    [{
      "id": "unique_scene_id_123", 
      "path": "http://localhost:5000/data/projects/.../extracted-raw/E0101_SQ0010-0010_extracted-raw_v0001.png",
      "ai_concept_placeholder_path": "http://localhost:5000/data/projects/.../AI-concept/E0101_SQ0010-0010_AI-concept_v0001.png",
      "filename": "storyboard_page_1_img_1.png",
      "ai_concept_filename": "E0101_SQ0010-0010_AI-concept_v0001.png",
      "plan_number": "0010",
      "sequence_number": "SQ0010", // Editable by user
      "voice_off": "Narrateur: Il était une fois..."
    }]
    ```

## Styling

-   TailwindCSS is used for styling, directly through CDN classes in the HTML elements.

This guide will be updated as the frontend evolves.