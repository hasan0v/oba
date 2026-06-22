#!/usr/bin/env python3
"""
Extract recipes from Azerbaijani cuisine PDF and convert to JSON format
"""
import json
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing PyMuPDF...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'PyMuPDF'])
    import fitz

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from PDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def parse_recipes(text: str) -> list:
    """Parse extracted text into structured recipes"""
    recipes = []
    
    # Split by common recipe patterns
    # This is a basic parser - may need adjustment based on PDF structure
    
    # Common Azerbaijani dish patterns
    dish_patterns = [
        r'(Plov|Dolma|Qutab|Dushbara|Xengel|Kabab|Lyulya|Piti|Bozbash|Dovga|Qovurma|Bozartma|Lavangi|Baliq|Şorbası|Küftə)',
    ]
    
    print(f"Total text length: {len(text)} characters")
    print("\n--- First 3000 characters of PDF ---")
    print(text[:3000])
    print("\n--- End of preview ---\n")
    
    return recipes

def main():
    pdf_path = Path(__file__).parent.parent / "mobile/assets/recipes/Azerbaycan_metbexi.pdf"
    
    if not pdf_path.exists():
        print(f"PDF not found at: {pdf_path}")
        return
    
    print(f"Reading PDF from: {pdf_path}")
    
    # Extract text
    text = extract_text_from_pdf(str(pdf_path))
    
    # Parse recipes
    recipes = parse_recipes(text)
    
    # Save full text for manual review
    output_path = Path(__file__).parent / "pdf_content.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"\nFull PDF content saved to: {output_path}")

if __name__ == "__main__":
    main()
