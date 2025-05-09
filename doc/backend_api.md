# Backend API Documentation

This document details the API endpoints provided by the Madsea backend (Python/FastAPI).

## Base URL

Typically `http://localhost:5000` (or as configured).

## Authentication

(To be defined - currently no explicit authentication for local development).

## Endpoints

### 1. Project Management

(Conceptual - Actual implementation of project/episode management directly via frontend state or file system for now. API endpoints for these can be added for more robust management if needed.)

### 2. Storyboard Processing

#### `POST /upload_storyboard`

-   **Description:** Uploads a storyboard PDF, processes it to extract images and text per plan, and generates initial placeholder AI concept filenames according to nomenclature.
-   **Request Type:** `multipart/form-data`
-   **Form Data Parameters:**
    -   `file`: The PDF file to be uploaded.
    -   `project_id` (string): The ID of the project (e.g., "P001_MaProd").
    -   `episode_id` (string): The ID of the episode (e.g., "E202_Pilot").
    -   `sequence_number` (string): The default sequence number for this upload batch (e.g., "SQ0010"). This is used for initial naming of AI concept placeholders.
    -   `options` (string, JSON formatted, optional): Additional processing options.
        ```json
        {
          "ocr_language": "fra", // Optional: language for OCR (default: 'fra')
          "skip_ocr": false       // Optional: if true, skips OCR text extraction
        }
        ```
-   **Success Response (200 OK):**
    -   **Content-Type:** `application/json`
    -   **Body:** An object containing details of the extracted plans.
        ```json
        {
          "message": "Storyboard processed successfully.",
          "project_id": "P001_MaProd",
          "episode_id": "E202_Pilot",
          "upload_default_sequence_number": "SQ0010",
          "base_output_path": "data/projects/P001_MaProd/episodes/E202_Pilot/sequences/SQ0010",
          "plans": [
            {
              "id": "unique_id_for_plan_1", // Generated unique ID for frontend use
              "original_filename_component": "storyboard_page1_img1.png", // Component from original PDF processing
              "plan_number": "0010", // Incremental plan number (0010, 0020, ...)
              "page_number": 1, 
              "image_index_on_page": 0, 
              "path": "data/projects/P001_MaProd/episodes/E202_Pilot/sequences/SQ0010/extracted-raw/E202_SQ0010-0010_extracted-raw_v0001.png", // Relative path to extracted raw image
              "filename": "E202_SQ0010-0010_extracted-raw_v0001.png",
              "ai_concept_placeholder_path": "data/projects/P001_MaProd/episodes/E202_Pilot/sequences/SQ0010/AI-concept/E202_SQ0010-0010_AI-concept_v0001.png", // Relative path to AI concept placeholder
              "ai_concept_filename": "E202_SQ0010-0010_AI-concept_v0001.png",
              "text_content": "Description of panel 1...", // Extracted text for the panel
              "voice_off": "Dialogue or VO for panel 1...", // Extracted voice-over text specifically
              "structured_text": { /* Detailed text blocks and their positions */ }
            },
            // ... more plans
          ]
        }
        ```
-   **Error Responses:**
    -   `400 Bad Request`: Invalid input (e.g., no file, missing parameters).
    -   `500 Internal Server Error`: Processing error on the backend.

### 3. ComfyUI Bridge

(Endpoints to be defined for triggering ComfyUI workflows and retrieving results.)

#### `POST /comfyui/generate_sequence` (Conceptual)

-   **Description:** Sends a list of selected plans (with their raw image paths and target sequence numbers/styles) to ComfyUI for generation.
-   **Request Body (JSON):**
    ```json
    {
      "project_id": "P001_MaProd",
      "episode_id": "E202_Pilot",
      "comfy_workflow_id": "Windsurf_Template_ControlNet", // ID of the ComfyUI workflow to use
      "plans_to_process": [
        {
          "source_image_path": "data/projects/.../extracted-raw/E202_SQ0010-0010_extracted-raw_v0001.png",
          "target_sequence_number": "SQ0010", // User-confirmed sequence number
          "target_plan_number": "0010",
          "output_filename_base": "E202_SQ0010-0010_AI-concept_final", // Base for final output name
          "style_parameters": { "prompt_suffix": "cinematic lighting, silhouette style" }
        }
        // ... more plans
      ]
    }
    ```

### 4. File System Operations

(The backend implicitly handles file system operations based on API calls. No direct file system API is exposed for security reasons, other than serving static files for image display.)

#### Serving Static Files for Images

The FastAPI backend is configured to serve files from the `data/projects` directory. This allows the frontend to display images using URLs like `http://localhost:5000/data/projects/{project_id}/episodes/{episode_id}/sequences/{sequence_number}/extracted-raw/{filename.png}`.

This documentation will be expanded as new endpoints are added or existing ones are modified.