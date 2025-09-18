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
    
    # Take first meaningful part (usually the title)
    lines = text.split('\n')
    title = ""
    
    for line in lines:
        line = line.strip()
        # Skip empty lines, dates, and system names at start
        if (len(line) > 10 and 
            not re.match(r'^\d{2}\.\d{2}\.\d{4}', line) and  # Skip dates
            not re.match(r'^(SIAN|SMIA|KOSS|Teams|Outlook)', line.upper()) and  # Skip system names alone
            not line.lower().startswith('sist oppdatert')):
            title = line
            break
    
    if not title:
        # If no good title found, use first substantial line
        for line in lines:
            if len(line.strip()) > 5:
                title = line.strip()
                break
    
    if not title:
        return "Untitled"
    
    # Clean the title for filename use
    # Remove or replace invalid filename characters
    title = re.sub(r'[<>:"/\\|?*]', '', title)  # Remove invalid chars
    title = re.sub(r'\s+', ' ', title)  # Multiple spaces to single
    title = title.strip()
    
    # Limit length and ensure it's not empty
    title = title[:100] if title else "Untitled"
    
    # Remove trailing dots (problematic on Windows)
    title = title.rstrip('.')
    
    return title if title else "Untitled"

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
        
        # Initialize organizer for this folder
        organizer = SystemBasedPDFOrganizer(str(folder))
        
        renamed_in_folder = 0
        
        for pdf_file in pdf_files:
            total_files += 1
            
            try:
                # Extract header/content
                content = organizer.extract_pdf_header(pdf_file)
                
                # Generate clean filename
                new_name = clean_filename(content)
                
                # Add system prefix for clarity
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