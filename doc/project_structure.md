# Project Structure

This document outlines the main directory structure of the Madsea project.

```
Madsea/
├── backend/                  # Python/FastAPI backend services
│   ├── extraction_api.py     # API for PDF parsing, OCR, and image extraction
│   ├── comfyui_bridge.py     # Service to interact with ComfyUI API
│   ├── file_manager.py       # Handles file naming and organization
│   ├── models/               # Pydantic models for API requests/responses
│   ├── utils/                # Utility functions
│   └── main.py               # FastAPI application entry point
├── frontend/                 # React/TailwindCSS frontend application
│   └── index.html            # Main HTML file with embedded React+JS (Babel setup)
├── ComfyUI/                  # ComfyUI related files
│   └── workflows/            # ComfyUI workflow templates (JSON)
│       └── Windsurf_Template.json
├── data/                     # Data storage (managed by backend)
│   ├── projects/             # Root for all project data
│   │   └── {project_id}/
│   │       ├── project_meta.json # Metadata about the project
│   │       └── episodes/
│   │           └── {episode_id}/
│   │               ├── episode_meta.json
│   │               ├── source_files/       # Original uploaded storyboards
│   │               │   └── {original_filename}.pdf
│   │               └── sequences/
│   │                   └── {sequence_number}/
│   │                       ├── extracted-raw/    # Raw images from PDF
│   │                       │   └── E..._SQ...-xxxx_extracted-raw_v0001.png
│   │                       ├── AI-concept/       # AI generated concept images (placeholders/final)
│   │                       │   └── E..._SQ...-xxxx_AI-concept_v0001.png
│   │                       └── sequence_meta.json
├── doc/                      # Project documentation (Markdown files)
│   ├── README.md
│   ├── project_structure.md
│   ├── frontend_guide.md
│   ├── backend_api.md
│   ├── workflow_extraction.md
│   └── log-projet.md
├── scripts/                  # Utility scripts (installation, maintenance)
│   └── install_comfyui_models.ps1
├── .gitignore
├── requirements.txt          # Python backend dependencies
└── README.md                 # Main project README (could point to doc/README.md)
```

## Key Directories Explained

- **`backend/`**: Contains all server-side logic. Built with FastAPI.
    - `extraction_api.py`: Handles the core PDF processing and data extraction.
    - `comfyui_bridge.py`: Manages communication with the ComfyUI server for image generation.
    - `file_manager.py`: Enforces the standardized file naming convention: `E{episode}_SQ{sequence}-{plan}_{task}_v{version}.{ext}`.
- **`frontend/`**: Contains the user interface. Currently a single `index.html` using React via CDN and TailwindCSS.
- **`ComfyUI/workflows/`**: Stores JSON templates for ComfyUI image generation pipelines, including ControlNet setups.
- **`data/projects/`**: This is the primary storage for all user-generated content, organized by project, episode, and sequence. The structure is designed to be self-contained for each project.
- **`doc/`**: Houses all project-related documentation.
- **`scripts/`**: Contains helper scripts, e.g., for setting up ComfyUI models.