from backend.services.extraction_service import PDFExtractor
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_extraction.py <pdf_path> <output_dir> [episode] [version]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    episode = sys.argv[3] if len(sys.argv) > 3 else "202"
    version = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    
    extractor = PDFExtractor()
    results = extractor.extract(pdf_path, output_dir, episode, version)
    
    print(f"{len(results)} panels extraits :")
    for panel in results:
        print(f"- {panel.image_path}")