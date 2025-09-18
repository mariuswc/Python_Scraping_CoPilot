#!/usr/bin/env python3
"""
Extract proper article titles from PDFs for filename generation
"""

import sys
import os
import re
from pathlib import Path
import PyPDF2
import pdfplumber

def extract_article_title(pdf_path: Path) -> str:
    """Extract the actual article title from a PDF"""
    
    try:
        # Try pdfplumber first for better text extraction
        with pdfplumber.open(pdf_path) as pdf:
            if pdf.pages:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                if text:
                    return find_title_in_text(text)
    except Exception as e:
        print(f"pdfplumber failed for {pdf_path.name}: {e}")
    
    try:
        # Fallback to PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.pages:
                page = reader.pages[0]
                text = page.extract_text()
                
                if text:
                    return find_title_in_text(text)
    except Exception as e:
        print(f"PyPDF2 failed for {pdf_path.name}: {e}")
    
    return "Untitled"

def find_title_in_text(text: str) -> str:
    """Find the actual article title in the extracted text"""
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    # Look for common title patterns
    for i, line in enumerate(cleaned_lines):
        line_clean = line.strip()
        
        # Skip very short lines (less than 3 chars)
        if len(line_clean) < 3:
            continue
            
        # Skip dates (dd.mm.yyyy format)
        if re.match(r'^\d{2}\.\d{2}\.\d{4}', line_clean):
            continue
            
        # Skip time stamps
        if re.match(r'^\d{2}:\d{2}', line_clean):
            continue
            
        # Skip "Sist oppdatert" lines
        if line_clean.lower().startswith('sist oppdatert'):
            continue
            
        # Skip pure system names as standalone titles
        if line_clean.upper() in ['TEAMS', 'OUTLOOK', 'SIAN', 'SMIA', 'KOSS', 'SHAREPOINT', 'ONEDRIVE']:
            continue
            
        # Skip URLs
        if 'http' in line_clean.lower() or 'www.' in line_clean.lower():
            continue
            
        # Skip lines that are just numbers or codes
        if re.match(r'^[\d\.\-\s]+$', line_clean):
            continue
            
        # Skip very long lines (likely descriptions, not titles)
        if len(line_clean) > 80:
            continue
            
        # Look for title patterns - usually appear early in document
        # and are not too long, not too short
        if 5 <= len(line_clean) <= 60:
            # Check if this looks like a title
            # Titles often have certain patterns
            
            # If it contains a dash with system name, it might be formatted title
            if ' - ' in line_clean:
                parts = line_clean.split(' - ', 1)
                if len(parts) == 2:
                    system_part, title_part = parts
                    # If first part is a system name, use the second part
                    if system_part.upper() in ['TEAMS', 'OUTLOOK', 'SIAN', 'SMIA', 'KOSS', 'SHAREPOINT', 'ONEDRIVE', 'MOBIL', 'WINDOWS', 'MAC', 'IPHONE']:
                        return title_part.strip()
                    else:
                        return line_clean  # Use the whole line
            
            # If it's a reasonable length and appears early, it's likely a title
            if i < 10:  # Within first 10 lines
                return line_clean
    
    # If no good title found, try to find anything reasonable
    for line in cleaned_lines[:5]:  # Just check first 5 lines
        if 3 <= len(line) <= 100:
            return line
    
    return "Untitled"

def clean_filename(title: str) -> str:
    """Clean title text to make it suitable for a filename"""
    if not title:
        return "Untitled"
    
    # Remove invalid filename characters
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    
    # Replace multiple spaces with single space
    title = re.sub(r'\s+', ' ', title)
    
    # Remove leading/trailing whitespace
    title = title.strip()
    
    # Remove trailing dots (problematic on Windows)
    title = title.rstrip('.')
    
    # Limit length
    if len(title) > 80:
        title = title[:80].rsplit(' ', 1)[0]  # Cut at word boundary
    
    return title if title else "Untitled"

def test_title_extraction():
    """Test the title extraction on a few files"""
    organized_dir = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    
    if not organized_dir.exists():
        print("❌ Organized directory not found!")
        return
    
    # Test on a few files from different folders
    test_count = 0
    for folder in organized_dir.iterdir():
        if folder.is_dir() and test_count < 10:
            pdf_files = list(folder.glob("*.pdf"))
            if pdf_files:
                test_file = pdf_files[0]  # Take first file
                print(f"\n📁 Folder: {folder.name}")
                print(f"📄 File: {test_file.name}")
                
                title = extract_article_title(test_file)
                clean_title = clean_filename(title)
                suggested_name = f"{folder.name} - {clean_title}.pdf"
                
                print(f"📝 Extracted title: '{title}'")
                print(f"🎯 Suggested filename: '{suggested_name}'")
                
                test_count += 1

if __name__ == "__main__":
    print("🧪 Testing Article Title Extraction")
    print("=" * 50)
    test_title_extraction()