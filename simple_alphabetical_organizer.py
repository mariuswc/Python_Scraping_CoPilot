#!/usr/bin/env python3
"""
Simple Alphabetical PDF Organizer
=================================

Extract headers from PDFs and create alphabetical files with article names only.
No system folders - just one alphabetical directory.
"""

import os
import re
import shutil
from pathlib import Path
import PyPDF2
import pdfplumber
from typing import Optional

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

def safe_filename(filename: str) -> str:
    """Make filename safe for filesystem."""
    # Remove/replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'[\r\n\t]', ' ', filename)
    filename = re.sub(r'\s+', ' ', filename)
    
    # Limit length
    if len(filename) > 240:
        filename = filename[:240]
    
    return filename.strip()

def get_system_from_header(header: str) -> str:
    """Extract the system name from the header (first word)."""
    if not header:
        return "Other"
    
    first_word = header.split()[0].strip()
    
    # System mapping for consistency
    system_mapping = {
        'OUTLOOK': 'Outlook',
        'TEAMS': 'Teams', 
        'MFA': 'MFA',
        'ONEDRIVE': 'OneDrive',
        'SHAREPOINT': 'SharePoint',
        'CITRIX': 'Citrix',
        'SMIA': 'SMIA',
        'KOSS': 'KOSS',
        'SIAN': 'SIAN',
        'SKATTEPLIKT': 'Skatteplikt',
        'MVA': 'Mva',
        'ESS': 'ESS',
        'TIDBANK': 'Tidbank',
        'VIS': 'VIS',
        'AURORA': 'Aurora',
        'WORD': 'Word',
        'EXCEL': 'Excel',
        'POWERPOINT': 'PowerPoint',
        'WINDOWS': 'Windows',
        'MOBIL': 'Mobil',
        'CHROME': 'Chrome',
        'ALTINN': 'Altinn',
    }
    
    return system_mapping.get(first_word.upper(), first_word.capitalize())

def organize_pdfs():
    """Main function to organize PDFs alphabetically by system name."""
    
    source_dir = Path("/Users/marius.cook/Downloads/PDF splitt 3")
    output_dir = Path("/Users/marius.cook/Desktop/scrape/alphabetical_articles")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return
    
    # Find all PDFs
    pdf_files = list(source_dir.glob("*.pdf"))
    print(f"📄 Found {len(pdf_files)} PDF files")
    
    processed = 0
    errors = 0
    no_header = 0
    
    for pdf_file in pdf_files:
        try:
            # Extract header
            header = extract_pdf_header(str(pdf_file))
            
            if header:
                # Get system name from first word
                system = get_system_from_header(header)
                
                # Get article title (everything after first word)
                words = header.split()
                if len(words) > 1:
                    article_title = " ".join(words[1:])
                    filename = f"{system} - {article_title}.pdf"
                else:
                    filename = f"{system}.pdf"
                
                filename = safe_filename(filename)
            else:
                # Fallback to original name if no header found
                filename = f"Other - {pdf_file.stem}.pdf"
                no_header += 1
            
            # Handle duplicate filenames
            dest_path = output_dir / filename
            counter = 2
            while dest_path.exists():
                base_name = filename.rsplit('.pdf', 1)[0]
                filename = f"{base_name} ({counter}).pdf"
                dest_path = output_dir / filename
                counter += 1
            
            # Copy file
            shutil.copy2(pdf_file, dest_path)
            processed += 1
            
            if processed % 100 == 0:
                print(f"✅ Processed {processed} files...")
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
            errors += 1
    
    print(f"\n🎉 Processing complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"✅ Successfully processed: {processed} files")
    print(f"📝 Files with headers: {processed - no_header}")
    print(f"❓ Files without headers: {no_header}")
    print(f"❌ Errors: {errors}")

def test_extraction():
    """Test header extraction on a few sample files."""
    source_dir = Path("/Users/marius.cook/Downloads/PDF splitt 3")
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return
    
    pdf_files = list(source_dir.glob("*.pdf"))[:5]
    print(f"🧪 Testing header extraction on {len(pdf_files)} sample files:\n")
    
    for pdf_file in pdf_files:
        header = extract_pdf_header(str(pdf_file))
        print(f"File: {pdf_file.name}")
        print(f"Header: {header or '(No header found)'}")
        print("-" * 50)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_extraction()
    else:
        organize_pdfs()