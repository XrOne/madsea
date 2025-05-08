# Madsea Project Log

## Session: 2025-05-08

### Decisions & Key Developments:

1.  **Refined Sequence Number Handling (Frontend):**
    *   Removed `Project ID`, `Episode ID`, `Sequence Number` display from the main `UploadArea` in `frontend/index.html` to simplify UI. These are now handled via active project/episode context.
    *   Added `updateSceneData(sceneId, updatedData)` function to `AppContext` for targeted updates to scene information.
    *   In `SceneGrid`, the `sequence_number` for each plan is now an editable input field.
        *   Initial value is taken from `scene.sequence_number` (defaulted from backend upload process, e.g., `SQ0010`).
        *   `onChange` updates the local scene state.
        *   `onBlur` includes validation to format the input to `SQxxxx` (e.g., `SQ0020`) and updates the state via `updateSceneData`.
    *   This allows users to correct or assign sequence numbers *after* PDF extraction and before sending to ComfyUI.

2.  **Nomenclature for AI Concept Placeholders (Backend Implication):**
    *   The backend's `/upload_storyboard` endpoint will use the provided default `sequence_number` from the frontend to initially name the `AI-concept` placeholder files (e.g., `E{ep}_{seq}-{plan}_AI-concept_v0001.png`).
    *   **Future Consideration:** When sequence numbers are modified in the frontend for specific plans, a backend mechanism will be needed (likely triggered before ComfyUI generation) to rename these placeholder files on disk to match the user's updated sequence numbers. This ensures ComfyUI outputs to correctly named files based on the user's final decision.

3.  **Documentation Structure Created:**
    *   Created `i:\Madsea\doc\` directory.
    *   Initialized the following documentation files with basic content:
        *   `README.md` (Overall project overview)
        *   `project_structure.md` (Directory and file organization)
        *   `frontend_guide.md` (Frontend components and workflow)
        *   `backend_api.md` (API endpoint details)
        *   `workflow_extraction.md` (Detailed PDF extraction process)
        *   `log-projet.md` (This file, for tracking decisions)

4.  **Season Number in Project Creation:**
    *   Confirmed that the existing "New Project" modal already includes a "Saison" number input when the project type "Série" is selected. This seems to meet the requirement for specifying season numbers.

### Next Steps / Open Questions:

-   **User Confirmation:**
    *   Confirm satisfaction with the new editable sequence number UI in `SceneGrid`.
    *   Confirm that the existing season number input in project creation is sufficient.
-   **Backend Renaming Logic:** Implement the backend logic to rename `AI-concept` placeholder files if their sequence number is changed by the user in the frontend before ComfyUI processing.
-   **ComfyUI Integration:** Define the exact data payload and backend endpoint for sending processed plans to ComfyUI.
-   **Automated Sequence Detection (Long-term):** Explore feasibility of automatically suggesting sequence breaks based on style changes in the storyboard (a more advanced feature).

---