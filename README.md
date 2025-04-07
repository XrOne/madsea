# Storyboard-to-Video AI Platform

This application converts movie storyboards (sequences of sketched scenes with text annotations) into stylized animated videos. It parses input PDF/images, generates key frame images for each scene using AI (Stable Diffusion + custom styles), and compiles these into an animated video.

## Features

- **Storyboard Parsing**: Extract images and text from PDFs or image sets
- **AI Image Generation**: Convert storyboard scenes to high-quality images using Stable Diffusion and ControlNet
- **Style Management**: Load pre-trained styles or train new ones using LoRA
- **Video Generation**: Assemble generated images into video sequences with transitions
- **Flexible Processing**: Use local computation or cloud-based resources

## Technical Stack

- **Frontend UI**: SwarmUI (web interface built on ComfyUI)
- **Backend**: Python
- **AI Models**: Stable Diffusion, ControlNet, LoRA, AnimateDiff
- **Tools**: PyMuPDF/pdfplumber, Tesseract OCR, ComfyUI, FFmpeg

## Project Structure

```
├── parsing/            # Storyboard parsing module
├── generation/         # Image generation module
├── styles/             # Style management module
├── video/              # Video generation module
├── ui/                 # User interface module
├── utils/              # Utility functions
├── config/             # Configuration files
├── requirements.txt    # Project dependencies
└── main.py             # Main entry point
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Or use the web interface by running:

```bash
python -m ui.app
```