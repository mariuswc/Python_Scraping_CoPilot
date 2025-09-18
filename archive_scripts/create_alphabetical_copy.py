#!/usr/bin/env python3
"""
Create an alphabetical copy of all organized PDFs in a single folder.
This script copies all PDFs from the organized system folders into one flat folder
sorted alphabetically by filename.
"""

import os
import shutil
from pathlib import Path
import sys

def create_alphabetical_copy():
    """Copy all organized PDFs into a single alphabetical folder."""
    
    # Define paths
    organized_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    alphabetical_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/alphabetical_all_pdfs")
    
    # Check if organized folder exists
    if not organized_path.exists():
        print(f"❌ Error: Organized folder not found at {organized_path}")
        print("Please run system_organizer.py first.")
        return False
    
    # Create alphabetical folder
    alphabetical_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created alphabetical folder: {alphabetical_path}")
    
    # Collect all PDF files from system folders
    all_pdfs = []
    total_files = 0
    
    print("\n🔍 Scanning organized folders...")
    
    # Walk through all system folders
    for system_folder in organized_path.iterdir():
        if system_folder.is_dir():
            folder_count = 0
            for pdf_file in system_folder.glob("*.pdf"):
                if pdf_file.is_file():
                    all_pdfs.append(pdf_file)
                    folder_count += 1
                    total_files += 1
            
            if folder_count > 0:
                print(f"   📂 {system_folder.name}: {folder_count} PDFs")
    
    print(f"\n📊 Found {total_files} total PDFs across {len([f for f in organized_path.iterdir() if f.is_dir()])} system folders")
    
    # Sort alphabetically by filename
    all_pdfs.sort(key=lambda x: x.name.lower())
    
    print(f"\n📋 Copying files in alphabetical order...")
    
    copied_count = 0
    errors = []
    
    # Copy files with progress
    for i, pdf_file in enumerate(all_pdfs, 1):
        try:
            # Create destination path
            dest_path = alphabetical_path / pdf_file.name
            
            # Handle duplicates by adding counter
            counter = 1
            original_dest = dest_path
            while dest_path.exists():
                stem = original_dest.stem
                suffix = original_dest.suffix
                dest_path = alphabetical_path / f"{stem} ({counter}){suffix}"
                counter += 1
            
            # Copy file
            shutil.copy2(pdf_file, dest_path)
            copied_count += 1
            
            # Show progress every 100 files
            if i % 100 == 0 or i == len(all_pdfs):
                print(f"   📄 Copied {i}/{len(all_pdfs)} files...")
                
        except Exception as e:
            error_msg = f"Failed to copy {pdf_file.name}: {str(e)}"
            errors.append(error_msg)
            print(f"   ❌ {error_msg}")
    
    # Print results
    print(f"\n✅ Alphabetical copy complete!")
    print(f"📊 Results:")
    print(f"   ✅ Successfully copied: {copied_count} files")
    print(f"   ❌ Errors: {len(errors)}")
    print(f"   📁 Destination: {alphabetical_path}")
    
    if errors:
        print(f"\n❌ Errors encountered:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"   • {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more errors")
    
    # Show first and last files as sample
    if copied_count > 0:
        sorted_files = sorted([f.name for f in alphabetical_path.glob("*.pdf")])
        print(f"\n📋 Sample of alphabetical order:")
        print(f"   🔤 First: {sorted_files[0]}")
        if len(sorted_files) > 1:
            print(f"   🔤 Last: {sorted_files[-1]}")
        
        print(f"\n🎯 All {copied_count} PDFs are now available in alphabetical order!")
        print(f"💡 You can browse them at: {alphabetical_path}")
    
    return True

if __name__ == "__main__":
    print("🔤 PDF Alphabetical Copy Tool")
    print("=" * 50)
    
    success = create_alphabetical_copy()
    
    if success:
        print("\n✅ Done! You now have:")
        print("   📁 Organized by system: /Users/marius.cook/Downloads/PDF splitt 2/organized_by_system/")
        print("   🔤 Alphabetical copy: /Users/marius.cook/Downloads/PDF splitt 2/alphabetical_all_pdfs/")
    else:
        print("\n❌ Failed to create alphabetical copy")
        sys.exit(1)