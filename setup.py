from setuptools import setup, find_packages

setup(
    name="madsea",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pymupdf",
        "pillow",
        "pytesseract",
        "opencv-python",
        "numpy",
    ],
    python_requires=">=3.8",
    description="Madsea - transformation de storyboards en séquences stylisées par IA",
)