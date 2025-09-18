#!/usr/bin/env python3
"""
Rename PDF files to use their actual article titles/headers
"""

import sys
import os
import re
from pathlib import Path
sys.path.append('/Users/marius.cook/Desktop/scrape')

from system_organizer import SystemBasedPDFOrganizer

def clean_filename(text: str) -> str:
    """Clean text to make it suitable for a filename"""
    if not text:
        return "Untitled"
    
    # This is now the extracted title, so we just need to clean it
    # Remove invalid filename characters
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove trailing dots (problematic on Windows)
    text = text.rstrip('.')
    
    # Limit length
    if len(text) > 80:
        text = text[:80].rsplit(' ', 1)[0]  # Cut at word boundary
    
    return text if text else "Untitled"

def extract_article_title(pdf_path: Path) -> str:
    """Extract the actual article title from a PDF"""
    
    try:
        # Try pdfplumber first for better text extraction
        import pdfplumber
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
        import PyPDF2
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

def rename_pdfs_with_headers():
    """Rename all PDF files to use their article titles"""
    
    # Path to organized folders
    organized_dir = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    
    if not organized_dir.exists():
        print("❌ Organized directory not found!")
        return
    
    # Get all system folders
    system_folders = [f for f in organized_dir.iterdir() if f.is_dir()]
    
    total_renamed = 0
    total_files = 0
    errors = []
    
    print(f"🔄 Renaming PDF files in {len(system_folders)} system folders...")
    print("=" * 70)
    
    for folder in system_folders:
        folder_name = folder.name
        pdf_files = list(folder.glob("*.pdf"))
        
        if not pdf_files:
            continue
            
        print(f"\n📁 Processing {folder_name} folder ({len(pdf_files)} files)")
        
        renamed_in_folder = 0
        
        for pdf_file in pdf_files:
            total_files += 1
            
            try:
                # Extract article title directly
                article_title = extract_article_title(pdf_file)
                
                # Generate clean filename
                new_name = clean_filename(article_title)
                
                # Add system prefix for clarity (avoid duplication)
                if not new_name.upper().startswith(folder_name.upper()):
                    new_name = f"{folder_name} - {new_name}"
                
                # Ensure .pdf extension
                if not new_name.lower().endswith('.pdf'):
                    new_name += '.pdf'
                
                new_path = folder / new_name
                
                # Skip if already has a good name (not side_xxx.pdf pattern)
                if not re.match(r'side_\d+\.pdf|Trim\(\d+\)\.pdf\.pdf', pdf_file.name):
                    print(f"   ⏭️  Skipping {pdf_file.name} (already has descriptive name)")
                    continue
                
                # Skip if target name already exists
                if new_path.exists() and new_path != pdf_file:
                    counter = 1
                    base_name = new_name[:-4]  # Remove .pdf
                    while new_path.exists():
                        new_name = f"{base_name} ({counter}).pdf"
                        new_path = folder / new_name
                        counter += 1
                
                # Rename the file
                pdf_file.rename(new_path)
                renamed_in_folder += 1
                total_renamed += 1
                
                print(f"   ✅ {pdf_file.name} → {new_name}")
                
            except Exception as e:
                error_msg = f"Error renaming {pdf_file.name}: {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ {error_msg}")
        
        if renamed_in_folder > 0:
            print(f"   📊 Renamed {renamed_in_folder} files in {folder_name}")
    
    # Summary
    print(f"\n📈 Renaming Results:")
    print("=" * 50)
    print(f"✅ Total files renamed: {total_renamed}")
    print(f"📁 Total files processed: {total_files}")
    print(f"❌ Errors encountered: {len(errors)}")
    
    if errors:
        print(f"\n❌ Errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   • {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more errors")
    
    if total_renamed > 0:
        print(f"\n🎯 Success! {total_renamed} PDF files now have descriptive names!")
        print("   Files are now named based on their article titles instead of generic names.")
    else:
        print(f"\n💡 No files needed renaming - they already have descriptive names.")

if __name__ == "__main__":
    print("📝 PDF File Renamer - Give files descriptive names based on content")
    print("=" * 70)
    print("This will rename files like 'side_123.pdf' to 'Teams - How to create channels.pdf'")
    
    response = input("\nRename PDF files to use article titles? (y/n): ").strip().lower()
    
    if response == 'y':
        rename_pdfs_with_headers()
        print(f"\n✅ File renaming complete!")
    else:
        print("❌ Renaming cancelled.")