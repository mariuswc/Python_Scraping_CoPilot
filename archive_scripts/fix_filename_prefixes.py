#!/usr/bin/env python3
"""
Fix filename prefixes to match their folder names
Ensures all files have consistent naming: [FOLDER] - [Article Title]
"""

import sys
import os
import re
from pathlib import Path

def fix_filename_prefixes():
    """Fix all filenames to match their folder names"""
    
    # Paths to both organized locations
    organized_dir = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    alphabetical_dir = Path("/Users/marius.cook/Downloads/PDF splitt 2/alphabetical_all_pdfs")
    
    locations = []
    if organized_dir.exists():
        locations.append(("System Folders", organized_dir, True))  # True = has subfolders
    if alphabetical_dir.exists():
        locations.append(("Alphabetical Folder", alphabetical_dir, False))  # False = flat structure
    
    if not locations:
        print("❌ No organized folders found!")
        return
    
    total_fixed = 0
    
    for location_name, base_dir, has_subfolders in locations:
        print(f"\n🔧 Fixing filenames in: {location_name}")
        print("=" * 60)
        
        if has_subfolders:
            # Process system folders (organized_by_system)
            system_folders = [f for f in base_dir.iterdir() if f.is_dir()]
            
            for folder in system_folders:
                folder_name = folder.name
                pdf_files = list(folder.glob("*.pdf"))
                
                if not pdf_files:
                    continue
                
                print(f"\n📁 Processing {folder_name} folder ({len(pdf_files)} files)")
                
                fixed_in_folder = 0
                
                for pdf_file in pdf_files:
                    try:
                        current_name = pdf_file.name
                        
                        # Check if filename already starts with correct folder name
                        if current_name.upper().startswith(f"{folder_name.upper()} - "):
                            continue  # Already correct
                        
                        # Extract the article title part (remove any existing system prefix)
                        article_title = extract_title_from_filename(current_name)
                        
                        # Create new filename with correct folder prefix
                        new_name = f"{folder_name} - {article_title}.pdf"
                        new_path = folder / new_name
                        
                        # Handle duplicates
                        if new_path.exists() and new_path != pdf_file:
                            counter = 1
                            base_name = f"{folder_name} - {article_title}"
                            while new_path.exists():
                                new_name = f"{base_name} ({counter}).pdf"
                                new_path = folder / new_name
                                counter += 1
                        
                        # Rename the file
                        pdf_file.rename(new_path)
                        fixed_in_folder += 1
                        total_fixed += 1
                        
                        print(f"   ✅ {current_name}")
                        print(f"   → {new_name}")
                        
                    except Exception as e:
                        print(f"   ❌ Error fixing {pdf_file.name}: {e}")
                
                if fixed_in_folder > 0:
                    print(f"   📊 Fixed {fixed_in_folder} files in {folder_name}")
                else:
                    print(f"   ✅ All files already correctly named in {folder_name}")
        
        else:
            # Process alphabetical folder (flat structure)
            pdf_files = list(base_dir.glob("*.pdf"))
            print(f"\n📄 Processing {len(pdf_files)} files in alphabetical folder")
            
            fixed_count = 0
            
            for pdf_file in pdf_files:
                try:
                    current_name = pdf_file.name
                    
                    # Extract folder name from filename (should be at the start)
                    folder_name = extract_folder_from_filename(current_name)
                    
                    if folder_name:
                        # Check if filename already starts correctly
                        if current_name.upper().startswith(f"{folder_name.upper()} - "):
                            continue  # Already correct
                        
                        # Extract the article title part
                        article_title = extract_title_from_filename(current_name)
                        
                        # Create new filename with correct folder prefix
                        new_name = f"{folder_name} - {article_title}.pdf"
                        new_path = base_dir / new_name
                        
                        # Handle duplicates
                        if new_path.exists() and new_path != pdf_file:
                            counter = 1
                            base_name = f"{folder_name} - {article_title}"
                            while new_path.exists():
                                new_name = f"{base_name} ({counter}).pdf"
                                new_path = base_dir / new_name
                                counter += 1
                        
                        # Rename the file
                        pdf_file.rename(new_path)
                        fixed_count += 1
                        total_fixed += 1
                        
                        if fixed_count <= 10:  # Show first 10 fixes
                            print(f"   ✅ {current_name}")
                            print(f"   → {new_name}")
                
                except Exception as e:
                    print(f"   ❌ Error fixing {pdf_file.name}: {e}")
            
            if fixed_count > 10:
                print(f"   ... and {fixed_count - 10} more files")
            
            print(f"   📊 Fixed {fixed_count} files in alphabetical folder")
    
    # Summary
    print(f"\n📈 Filename Fix Results:")
    print("=" * 50)
    print(f"✅ Total files fixed: {total_fixed}")
    
    if total_fixed > 0:
        print(f"\n🎯 Success! All filenames now match their folder names!")
        print("   Format: [FOLDER] - [Article Title].pdf")
    else:
        print(f"\n💡 All filenames were already correctly formatted.")

def extract_folder_from_filename(filename):
    """Extract the folder/system name from a filename"""
    # Remove .pdf extension
    name = filename.replace('.pdf', '').replace('.PDF', '')
    
    # Common system names in order of preference
    systems = [
        'SHAREPOINT', 'ONEDRIVE', 'TEAMS', 'OUTLOOK', 'EXCEL', 'WORD', 'POWERPOINT',
        'SMIA', 'ELEMENTS', 'KOSS', 'SIAN', 'SOFIE', 'PUZZEL', 'TIDBANK', 'INTRANETT',
        'DELINGSTJENESTER', 'FOLKEREGISTER', 'ESKATTEKORT', 'SKATTEKORT', 'MVA',
        'JABRA', 'VDI', 'REMEDY', 'JIRA', 'UNIT4', 'PHONERO', 'ADOBE', 'PLANNER',
        'MURAL', 'UNIFLOW', 'BITLOCKER', 'MICROSOFT', 'WINDOWS', 'APPLE', 'MAC',
        'IPHONE', 'ANDROID', 'MOBIL', 'ALTINN', 'MATOMO', 'ONENOTE', 'EDGE',
        'CHROME', 'CISCO', 'AURORA', 'VENTUS', 'OBI', 'MATTERMOST', 'LÆRINGSPORTALEN',
        'ESS', 'AUTOHOTKEY', 'VPN', 'MFA', 'DVH', 'CITRIX', 'OMNISSA'
    ]
    
    name_upper = name.upper()
    
    # Look for system name at the start of filename
    for system in systems:
        if name_upper.startswith(system.upper()):
            return system
    
    # If no match found, try to extract from pattern "SYSTEM - Title"
    if ' - ' in name:
        potential_system = name.split(' - ')[0].strip()
        if len(potential_system) <= 20:  # Reasonable system name length
            return potential_system
    
    return None

def extract_title_from_filename(filename):
    """Extract the article title from a filename, removing system prefixes"""
    # Remove .pdf extension
    title = filename.replace('.pdf', '').replace('.PDF', '')
    
    # If it has a system prefix pattern "SYSTEM - Title", extract the title part
    if ' - ' in title:
        parts = title.split(' - ', 1)
        if len(parts) == 2:
            # Check if first part looks like a system name
            system_part = parts[0].strip()
            title_part = parts[1].strip()
            
            # If system part is short and uppercase-ish, use title part
            if len(system_part) <= 20 and any(c.isupper() for c in system_part):
                return title_part
    
    # Otherwise return the whole thing
    return title

if __name__ == "__main__":
    print("🔧 PDF Filename Prefix Fixer")
    print("=" * 50)
    print("This will ensure all files have format: [FOLDER] - [Article Title].pdf")
    print("Example: Files in Teams folder will start with 'TEAMS - ...'")
    
    response = input("\nFix all filename prefixes to match folder names? (y/n): ").strip().lower()
    
    if response == 'y':
        fix_filename_prefixes()
        print(f"\n✅ Filename fixing complete!")
    else:
        print("❌ Filename fixing cancelled.")