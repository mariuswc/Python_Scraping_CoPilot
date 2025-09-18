#!/usr/bin/env python3
"""
Fix miscategorized files by analyzing the actual system name in the filename
and moving files to their correct folders.

This script looks for files that have been named like:
"Intranett - JIRA Service Desk..." → should be in Jira folder
"Teams - SharePoint Endre..." → should be in SharePoint folder
etc.
"""

import os
import shutil
from pathlib import Path
import re
from collections import defaultdict

def extract_actual_system_from_filename(filename: str) -> str:
    """Extract the actual system name from a filename, ignoring folder prefixes."""
    
    # Remove .pdf extension
    name = filename.replace('.pdf', '')
    
    # System mapping - more comprehensive list
    system_keywords = {
        'SHAREPOINT': 'SharePoint',
        'TEAMS': 'Teams', 
        'OUTLOOK': 'Outlook',
        'WORD': 'Word',
        'EXCEL': 'Excel',
        'POWERPOINT': 'PowerPoint',
        'ONEDRIVE': 'OneDrive',
        'ONENOTE': 'OneNote',
        'JIRA': 'Jira',
        'SIAN': 'Sian',
        'SMIA': 'SMIA',
        'KOSS': 'KOSS',
        'ELEMENTS': 'Elements',
        'SOFIE': 'Sofie',
        'ESS': 'ESS',
        'TIDBANK': 'Tidbank',
        'TIDBANK': 'Tidbank',
        'WINDOWS': 'Windows',
        'MAC': 'Mac',
        'APPLE': 'Apple',
        'ADOBE': 'Adobe',
        'CHROME': 'Chrome',
        'EDGE': 'Edge',
        'VPN': 'VPN',
        'REMEDY': 'Remedy',
        'PUZZEL': 'Puzzel',
        'PHONERO': 'Phonero',
        'JABRA': 'Jabra',
        'JABBER': 'Jabber',
        'CITRIX': 'VDI',  # Citrix often relates to VDI
        'WEBEX': 'Webex',
        'ZOOM': 'Webex',  # Group video tools
        'MFA': 'MFA',
        'AUTHENTICATOR': 'Authenticator',
        'BITLOCKER': 'Bitlocker',
        'MOBIL': 'Mobil',
        'IPHONE': 'iPhone',
        'ANDROID': 'Android',
        'SAMSUNG': 'Android',
        'DVH': 'DVH',
        'OBI': 'OBI',
        'ALTINN': 'Altinn',
        'VENTUS': 'Ventus',
        'UNIFORM': 'Uniflow',
        'UNIFLOW': 'Uniflow',
        'FORMS': 'Forms',
        'PLANNER': 'Planner',
        'MURAL': 'Mural',
        'LOOP': 'Loop',
        'MATOMO': 'Matomo',
        'MATTERMOST': 'Mattermost',
        'PIXVIEW': 'Pixview',
        'UNIT4': 'Unit4',
        'AURORA': 'Aurora',
        'LÆRINGSPORTALEN': 'Læringsportalen',
        'AUTOHOTKEY': 'Autohotkey',
        'SKATTEETATEN': 'Skatteetaten'
    }
    
    # Look for system names after any prefix
    # Pattern: "AnyPrefix - SystemName ..." or just "SystemName ..."
    words = name.upper().split()
    
    for i, word in enumerate(words):
        # Clean the word of special characters
        clean_word = re.sub(r'[^\w]', '', word)
        
        # Check if this word matches a system
        if clean_word in system_keywords:
            return system_keywords[clean_word]
        
        # Check partial matches for compound systems
        for keyword, system in system_keywords.items():
            if keyword in clean_word or clean_word in keyword:
                return system
    
    return None

def analyze_folder_for_miscategorized_files(folder_path: Path) -> dict:
    """Analyze a folder and find files that should be in other folders."""
    
    folder_name = folder_path.name
    miscategorized = defaultdict(list)
    
    pdf_files = list(folder_path.glob("*.pdf"))
    
    for pdf_file in pdf_files:
        # Extract what system this file is actually about
        actual_system = extract_actual_system_from_filename(pdf_file.name)
        
        # If the actual system is different from the folder name, it's miscategorized
        if actual_system and actual_system.upper() != folder_name.upper():
            miscategorized[actual_system].append(pdf_file)
    
    return dict(miscategorized)

def fix_all_miscategorized_files():
    """Scan all folders and fix miscategorized files."""
    
    organized_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    
    if not organized_path.exists():
        print(f"❌ Error: Organized folder not found at {organized_path}")
        return False
    
    print("🔍 Scanning all folders for miscategorized files...")
    print("=" * 60)
    
    all_moves = defaultdict(list)  # target_folder -> [(source_file, source_folder)]
    total_miscategorized = 0
    
    # Scan each folder
    for folder in organized_path.iterdir():
        if not folder.is_dir():
            continue
            
        print(f"\n📁 Analyzing {folder.name} folder...")
        
        miscategorized = analyze_folder_for_miscategorized_files(folder)
        
        if miscategorized:
            folder_total = sum(len(files) for files in miscategorized.values())
            total_miscategorized += folder_total
            print(f"   ⚠️  Found {folder_total} miscategorized files:")
            
            for target_system, files in miscategorized.items():
                print(f"      → {len(files)} files should be in {target_system}/")
                for file in files:
                    all_moves[target_system].append((file, folder.name))
                    print(f"         • {file.name}")
        else:
            print(f"   ✅ All files correctly categorized")
    
    if total_miscategorized == 0:
        print(f"\n🎉 Great! No miscategorized files found.")
        return True
    
    print(f"\n📊 Summary:")
    print(f"   🔄 Total files to move: {total_miscategorized}")
    print(f"   📂 Target folders: {len(all_moves)}")
    
    # Ask for confirmation
    print(f"\n❓ Do you want to move these files to their correct folders?")
    response = input("Type 'yes' to proceed: ").lower().strip()
    
    if response != 'yes':
        print("❌ Operation cancelled.")
        return False
    
    # Execute moves
    print(f"\n🔄 Moving files to correct folders...")
    
    moved_count = 0
    errors = []
    
    for target_system, file_moves in all_moves.items():
        target_folder = organized_path / target_system
        
        # Create target folder if it doesn't exist
        target_folder.mkdir(exist_ok=True)
        
        print(f"\n📂 Moving to {target_system}/ folder:")
        
        for source_file, source_folder_name in file_moves:
            try:
                # Remove old prefix and add correct prefix
                old_name = source_file.name
                
                # Remove old system prefix if it exists
                if ' - ' in old_name:
                    # Split on first ' - ' and take everything after
                    parts = old_name.split(' - ', 1)
                    if len(parts) > 1:
                        content_part = parts[1]
                    else:
                        content_part = old_name
                else:
                    content_part = old_name
                
                # Create new name with correct prefix
                if not content_part.upper().startswith(target_system.upper()):
                    new_name = f"{target_system} - {content_part}"
                else:
                    new_name = content_part
                
                dest_path = target_folder / new_name
                
                # Handle duplicates
                counter = 1
                original_dest = dest_path
                while dest_path.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    dest_path = target_folder / f"{stem} ({counter}){suffix}"
                    counter += 1
                
                # Move file
                shutil.move(str(source_file), str(dest_path))
                moved_count += 1
                
                print(f"   ✅ {old_name}")
                print(f"      → {dest_path.name}")
                
            except Exception as e:
                error_msg = f"Failed to move {source_file.name}: {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ {error_msg}")
    
    # Print results
    print(f"\n✅ File reorganization complete!")
    print(f"📊 Results:")
    print(f"   ✅ Successfully moved: {moved_count} files")
    print(f"   ❌ Errors: {len(errors)}")
    
    if errors:
        print(f"\n❌ Errors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   • {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more errors")
    
    return True

if __name__ == "__main__":
    print("🔧 Fix Miscategorized Files Tool")
    print("=" * 50)
    print("This tool scans all folders and moves files to their correct system folders")
    print("based on the actual system name in the filename content.\n")
    
    success = fix_all_miscategorized_files()
    
    if success:
        print("\n🎯 Recommendation: Run create_alphabetical_copy.py again to update the alphabetical folder!")
    else:
        print("\n❌ Failed to fix miscategorized files")