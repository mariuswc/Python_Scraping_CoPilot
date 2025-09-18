#!/usr/bin/env python3
"""
Flatten System Folders

This script moves all PDF files from sub-folders back to their main system folders,
eliminating the sub-folder structure for a cleaner organization.

Before: Teams/Calendar/file.pdf, Teams/Chat/file2.pdf
After:  Teams/file.pdf, Teams/file2.pdf
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

def flatten_system_folder(system_folder: Path):
    """Move all PDFs from sub-folders to the main system folder."""
    
    if not system_folder.is_dir():
        return 0, 0
    
    moved_files = 0
    removed_folders = 0
    
    print(f"📁 Flattening {system_folder.name}/")
    
    # Find all PDF files in sub-folders
    pdf_files_in_subfolders = []
    sub_folders = []
    
    for item in system_folder.iterdir():
        if item.is_dir():
            sub_folders.append(item)
            # Find PDFs recursively in this sub-folder
            for pdf_file in item.rglob("*.pdf"):
                pdf_files_in_subfolders.append((pdf_file, item))
    
    if not pdf_files_in_subfolders:
        print(f"   ✅ No sub-folders with PDFs found")
        return 0, 0
    
    # Move files to main folder
    for pdf_file, source_subfolder in pdf_files_in_subfolders:
        try:
            target_path = system_folder / pdf_file.name
            
            # Handle duplicates
            counter = 1
            original_target = target_path
            while target_path.exists():
                stem = original_target.stem
                suffix = original_target.suffix
                target_path = system_folder / f"{stem} ({counter}){suffix}"
                counter += 1
            
            # Move the file
            shutil.move(str(pdf_file), str(target_path))
            moved_files += 1
            print(f"   📄 Moved: {pdf_file.name[:50]}...")
            
        except Exception as e:
            print(f"   ❌ Failed to move {pdf_file.name}: {e}")
    
    # Remove empty sub-folders
    for sub_folder in sub_folders:
        try:
            # Check if folder is empty (recursively)
            if not any(sub_folder.rglob("*")):
                sub_folder.rmdir()
                removed_folders += 1
                print(f"   🗑️  Removed empty folder: {sub_folder.name}/")
            else:
                # Remove empty sub-sub-folders first, then try again
                for item in sub_folder.rglob("*"):
                    if item.is_dir() and not any(item.iterdir()):
                        item.rmdir()
                
                # Try to remove the main sub-folder again
                if not any(sub_folder.iterdir()):
                    sub_folder.rmdir()
                    removed_folders += 1
                    print(f"   🗑️  Removed empty folder: {sub_folder.name}/")
                else:
                    print(f"   ⚠️  Folder not empty, keeping: {sub_folder.name}/")
        except Exception as e:
            print(f"   ⚠️  Could not remove folder {sub_folder.name}: {e}")
    
    return moved_files, removed_folders

def flatten_all_system_folders():
    """Flatten all system folders in the organized directory."""
    
    organized_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    
    if not organized_path.exists():
        print(f"❌ Error: Organized folder not found at {organized_path}")
        return False
    
    print("🗂️  Flattening System Folders")
    print("=" * 50)
    print("Moving all files from sub-folders to main system folders...\n")
    
    total_moved = 0
    total_folders_removed = 0
    processed_systems = 0
    
    # Process each system folder
    for system_folder in sorted(organized_path.iterdir()):
        if not system_folder.is_dir():
            continue
        
        moved, removed = flatten_system_folder(system_folder)
        total_moved += moved
        total_folders_removed += removed
        
        if moved > 0:
            processed_systems += 1
        
        print()  # Empty line between systems
    
    print("=" * 50)
    print(f"✅ Flattening complete!")
    print(f"📊 Results:")
    print(f"   📂 Systems processed: {processed_systems}")
    print(f"   📄 Files moved to main folders: {total_moved}")
    print(f"   🗑️  Sub-folders removed: {total_folders_removed}")
    
    if total_moved > 0:
        print(f"\n🎯 All files are now directly in their system folders!")
        print(f"💡 Run create_alphabetical_copy.py to update the alphabetical view!")
    else:
        print(f"\n💡 All files were already in main system folders!")
    
    return True

if __name__ == "__main__":
    print("🗂️  System Folder Flattener")
    print("=" * 40)
    print("This tool moves all PDFs from sub-folders directly")
    print("into their main system folders for cleaner organization.\n")
    
    success = flatten_all_system_folders()
    
    if not success:
        print("\n❌ Failed to flatten system folders")