#!/usr/bin/env python3
"""
Simple Header-Based PDF Organizer
=================================

Rules:
1. Extract the header/title from the PDF (usually the first bold line)
2. First word of header = Folder name
3. Full header text = Filename (no prefixes added)

Example:
- PDF header: "OneDrive Citrix ikke synkronisert med OneDrive utenfor"
- Folder: OneDrive/
- Filename: "OneDrive Citrix ikke synkronisert med OneDrive utenfor.pdf"
"""

import os
import re
import shutil
from pathlib import Path
import PyPDF2
import pdfplumber
from typing import Optional

# System folder mapping (normalize different variations)
SYSTEM_MAPPING = {
    'ONEDRIVE': 'OneDrive',
    'TEAMS': 'Teams', 
    'OUTLOOK': 'Outlook',
    'SHAREPOINT': 'SharePoint',
    'CITRIX': 'Citrix',
    'SMIA': 'SMIA',
    'KOSS': 'KOSS',
    'SIAN': 'SIAN',
    'MFA': 'MFA',
    'SKATTEPLIKT': 'Skatteplikt',
    'MVA': 'Mva',
    'ESS': 'ESS',
    'TIDBANK': 'Tidbank',
    'FOLKEREGISTER': 'Folkeregister',
    'VIS': 'VIS',
    'ELEMENTS': 'Elements',
    'SOFIE': 'Sofie',
    'AURORA': 'Aurora',
    'WORD': 'Word',
    'EXCEL': 'Excel',
    'POWERPOINT': 'PowerPoint',
    'ONENOTE': 'OneNote',
    'WINDOWS': 'Windows',
    'MOBIL': 'Mobil',
    'IPHONE': 'iPhone',
    'ANDROID': 'Android',
    'CHROME': 'Chrome',
    'EDGE': 'Edge',
    'JIRA': 'Jira',
    'UNIT4': 'Unit4',
    'VDI': 'VDI',
    'BITLOCKER': 'Bitlocker',
    'DVH': 'DVH',
    'OBI': 'OBI',
    'UNIFLOW': 'Uniflow',
    'AUTOHOTKEY': 'Autohotkey',
    'OMNISSA': 'Omnissa',
    'VENTUS': 'Ventus',
    'MATOMO': 'Matomo',
    'ESKATTEKORT': 'Eskattekort',
    'MICROSOFT': 'Microsoft',
    'JABRA': 'Jabra',
    'ALTINN': 'Altinn',
    'MATTERMOST': 'Mattermost',
    'SME': 'Sme',
}

def extract_pdf_header(file_path: str) -> Optional[str]:
    """Extract the main header/title from PDF (first meaningful line)."""
    try:
        # Try pdfplumber first
        with pdfplumber.open(file_path) as pdf:
            if pdf.pages:
                text = pdf.pages[0].extract_text()
                if text:
                    return find_header_in_text(text)
    except:
        pass
    
    # Fallback to PyPDF2
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            if pdf_reader.pages:
                text = pdf_reader.pages[0].extract_text()
                if text:
                    return find_header_in_text(text)
    except:
        pass
    
    return None

def find_header_in_text(text: str) -> Optional[str]:
    """Find the main header in the extracted text."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Skip common metadata lines and find the actual header
    skip_patterns = [
        r'^(Innhold fra skjema|System eller applikasjon|Din henvendelse)',
        r'^(Beskriv|Hva gjorde du|Hvilke)',
        r'^(Page \d+|Side \d+)',
        r'^(\d{1,2}[./]\d{1,2}[./]\d{2,4})',  # Dates
        r'^(https?://)',  # URLs
        r'^(PDF|Document|File)',
        r'^(Portal|Brukerportalen)',
        r'^\w+@\w+\.',  # Email addresses
        r'^Sist\s+oppdatert',  # "Sist oppdatert"
    ]
    
    for line in lines[:10]:  # Check first 10 lines
        if not line or len(line.strip()) < 3:
            continue
            
        # Skip lines matching skip patterns
        if any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue
            
        # This should be the main header
        if len(line) > 5 and len(line) < 200:
            return clean_header(line)
    
    return None

def clean_header(header: str) -> str:
    """Clean the header for use as filename."""
    # Remove file extension if present
    header = re.sub(r'\.(pdf|PDF)$', '', header)
    
    # Clean up spacing
    header = re.sub(r'\s+', ' ', header)
    header = header.strip()
    
    return header

def get_folder_from_header(header: str) -> str:
    """Get folder name from the first word of the header."""
    if not header:
        return 'Other'
    
    first_word = header.split()[0] if header.split() else ''
    first_word = first_word.upper().strip('.,;:')
    
    # Check mapping
    if first_word in SYSTEM_MAPPING:
        return SYSTEM_MAPPING[first_word]
    
    return 'Other'

def clean_filename(filename: str) -> str:
    """Clean filename to be filesystem-safe."""
    # Replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple spaces
    filename = re.sub(r'\s+', ' ', filename)
    # Trim
    filename = filename.strip()
    return filename

def organize_by_headers(base_dir: str):
    """Organize PDFs using their actual headers as filenames."""
    organized_dir = os.path.join(base_dir, "organized_by_system")
    
    if not os.path.exists(organized_dir):
        print(f"Error: {organized_dir} not found")
        return
    
    print(f"📋 Organizing PDFs by their actual headers...")
    print(f"📂 Processing: {organized_dir}")
    
    total_files = 0
    processed_files = 0
    moved_files = 0
    
    # Process each folder
    for folder_name in os.listdir(organized_dir):
        folder_path = os.path.join(organized_dir, folder_name)
        
        if not os.path.isdir(folder_path):
            continue
            
        print(f"\n📁 Processing {folder_name} folder...")
        
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        
        for filename in pdf_files:
            file_path = os.path.join(folder_path, filename)
            total_files += 1
            
            try:
                # Extract header from PDF
                header = extract_pdf_header(file_path)
                if not header:
                    print(f"   ⚠️  No header found: {filename}")
                    continue
                
                # Determine correct folder from first word
                correct_folder = get_folder_from_header(header)
                
                # Create correct filename (just the header + .pdf)
                correct_filename = clean_filename(header) + ".pdf"
                
                print(f"   📄 {filename}")
                print(f"      Header: {header}")
                print(f"      → Folder: {correct_folder}")
                print(f"      → Filename: {correct_filename}")
                
                # Create correct folder path
                correct_folder_path = os.path.join(organized_dir, correct_folder)
                os.makedirs(correct_folder_path, exist_ok=True)
                
                # Create target path
                target_path = os.path.join(correct_folder_path, correct_filename)
                
                # Handle duplicates
                counter = 1
                base_name = correct_filename.replace('.pdf', '')
                while os.path.exists(target_path):
                    new_filename = f"{base_name} ({counter}).pdf"
                    target_path = os.path.join(correct_folder_path, new_filename)
                    counter += 1
                    correct_filename = new_filename
                
                # Check if file needs to be moved or renamed
                current_folder = folder_name
                needs_move = (current_folder != correct_folder) or (filename != correct_filename)
                
                if needs_move:
                    # Move/rename file
                    shutil.move(file_path, target_path)
                    if current_folder != correct_folder:
                        print(f"      ✅ Moved: {current_folder} → {correct_folder}")
                        moved_files += 1
                    else:
                        print(f"      ✅ Renamed in same folder")
                else:
                    print(f"      ✅ Already correct")
                
                processed_files += 1
                
            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")
    
    print(f"\n✅ Header-based organization complete!")
    print(f"   📄 Total files: {total_files}")
    print(f"   🔧 Files processed: {processed_files}")
    print(f"   📦 Files moved to different folders: {moved_files}")
    
    # Show final folder statistics
    print(f"\n📊 Final organization:")
    for folder_name in sorted(os.listdir(organized_dir)):
        folder_path = os.path.join(organized_dir, folder_name)
        if os.path.isdir(folder_path):
            count = len([f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')])
            if count > 0:
                print(f"   {folder_name}: {count} files")

if __name__ == "__main__":
    # Get base directory path
    base_dir = input("Enter the path to your PDF base directory (contains organized_by_system folder): ").strip()
    
    if not os.path.exists(base_dir):
        print(f"Error: Directory {base_dir} does not exist")
        exit(1)
    
    organize_by_headers(base_dir)