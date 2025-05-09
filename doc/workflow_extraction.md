# PDF Storyboard Extraction Workflow

This document details the process by which Madsea ingests a PDF storyboard, extracts relevant information (images, text, structure), and prepares it for AI-powered visual generation.

## 1. Upload

-   **Trigger:** User uploads a PDF file via the frontend (`UploadArea` component).
-   **Data Sent to Backend (`/upload_storyboard` endpoint):**
    -   The PDF file itself.
    -   `project_id`: Identifier of the current project.
    -   `episode_id`: Identifier of the current episode.
    -   `sequence_number`: A default sequence number (e.g., `SQ0010`) for this batch of extractions. This is used for initial file naming of AI concept placeholders. The user can refine this per plan later in the UI.
    -   Optional `options` (JSON string): e.g., OCR language, skip OCR.

## 2. Backend Processing (`extraction_api.py`)

### a. File Reception and Setup

-   The PDF is saved temporarily.
-   Output directories are prepared based on `project_id`, `episode_id`, and the default `sequence_number` within the `data/projects/` structure. Example:
    -   `data/projects/{project_id}/episodes/{episode_id}/sequences/{sequence_number}/extracted-raw/`
    -   `data/projects/{project_id}/episodes/{episode_id}/sequences/{sequence_number}/AI-concept/` (for placeholders)

### b. PDF Parsing (PyMuPDF)

-   The backend iterates through each page of the PDF.
-   **Image Extraction:**
    -   PyMuPDF extracts raster images (PNG, JPG) directly from the PDF page's resources.
    -   Each extracted image is saved to the `extracted-raw` directory following the nomenclature:
        `E{episode_id_short}_{sequence_number}-{plan_number_str}_extracted-raw_v0001.png`
        -   `{episode_id_short}`: e.g., E202 from E202_Pilot.
        -   `{sequence_number}`: The default sequence number from upload (e.g., SQ0010).
        -   `{plan_number_str}`: Increments by 10 for each image found (0010, 0020, 0030...). This is the initial plan number.
-   **Text Extraction (OCR with Tesseract if needed):**
    -   PyMuPDF extracts text blocks with their bounding box coordinates.
    -   If text quality is low or for image-based PDFs, Tesseract OCR can be invoked (language specified in options or default 'fra').
    -   **Voice-Over Detection:** A heuristic is applied to identify text likely to be dialogue or voice-over based on its position (e.g., bottom center of a panel, specific font styles if detectable - though font style detection is complex).
    -   All extracted text, including identified voice-over and other annotations (shot type, action notes), is associated with the closest image/panel based on proximity of bounding boxes.

### c. Placeholder Generation (Conceptual)

-   For each extracted raw image (plan), a corresponding placeholder entry for the AI-concept image is created.
-   The filename for this placeholder follows the nomenclature:
    `E{episode_id_short}_{sequence_number}-{plan_number_str}_AI-concept_v0001.png`
-   Initially, this might be an empty file or a copy of the raw image, or a generic placeholder image. The key is that its *filename* is established.

### d. Response Generation

-   The backend compiles a JSON response listing all extracted plans.
-   Each plan object in the response includes:
    -   `id`: A unique identifier for the plan (for frontend keying).
    -   `path`: Relative path to the saved `extracted-raw` image.
    -   `filename`: Full filename of the `extracted-raw` image.
    -   `ai_concept_placeholder_path`: Relative path to the (future) `AI-concept` image.
    -   `ai_concept_filename`: Full filename for the `AI-concept` image.
    -   `plan_number`: The assigned plan number (e.g., "0010").
    -   `sequence_number`: The default sequence number used for this extraction batch (e.g., "SQ0010").
    -   `text_content`: General text associated with the plan.
    -   `voice_off`: Specifically identified voice-over text.
    -   `page_number`, `image_index_on_page`.

## 3. Frontend Display and Refinement

-   The frontend receives the JSON response.
-   It prepends the backend URL (`http://localhost:5000/`) to the relative image paths for display.
-   Scenes are rendered in `SceneGrid` or `SceneList`.
-   Crucially, the user can now **edit the `sequence_number` for each plan individually** in the UI. This allows correction if the default sequence number was not appropriate for all extracted plans (e.g., if a new sequence starts mid-PDF).

## 4. Preparation for AI Generation

-   When the user triggers "Envoyer à ComfyUI":
    -   The frontend gathers data for selected plans.
    -   This data includes the **user-confirmed `sequence_number`** for each plan and the path to its `extracted-raw` image.
    -   **(Future Step - Backend):** Before sending to ComfyUI, if the user changed a `sequence_number` for a plan, the backend might need to rename the corresponding `AI-concept` placeholder file on disk to match the new `sequence_number` to maintain consistency for ComfyUI's output.
        -   Example: Original placeholder: `E202_SQ0010-0020_AI-concept_v0001.png`
        -   User changes SQ in UI for this plan to `SQ0030`.
        -   Backend renames placeholder to: `E202_SQ0030-0020_AI-concept_v0001.png`.
        -   ComfyUI will then save its output using this new base name.

This workflow ensures that initial processing is automated while providing flexibility for the user to refine sequence organization before final AI generation.