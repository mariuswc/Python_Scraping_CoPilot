#!/usr/bin/env python3
"""
Fix Cross-System File Categorization

This script finds files that are categorized under the wrong system because they
were accessed through that system but are actually about a different system.

Examples:
- "Altinn - MVA ..." should be in MVA/ folder, not Altinn/MVA/
- "Intranett - JIRA ..." should be in Jira/ folder, not Intranett/JIRA/
- "ESS - Skatteplikt ..." should be in a Skatteplikt/ folder, not ESS/Skatteplikt/
"""

import os
import shutil
from pathlib import Path
import re
from collections import defaultdict

def get_independent_systems():
    """Return list of systems that should have their own folders, not be sub-folders."""
    return {
        'MVA', 'DELINGSTJENESTER', 'FOLKEREGISTER', 'SKATTEKORT', 'SME', 'ESKATTEKORT',
        'SIAN', 'KOSS', 'ELEMENTS', 'SOFIE', 'ESS', 'SMIA', 'TIDBANK',
        'TEAMS', 'OUTLOOK', 'SHAREPOINT', 'ONEDRIVE', 'WORD', 'EXCEL', 'POWERPOINT',
        'JIRA', 'REMEDY', 'VPN', 'ADOBE', 'CHROME', 'EDGE', 'SAFARI',
        'CISCO', 'JABBER', 'JABRA', 'UNIFLOW', 'BITLOCKER', 'WINDOWS', 'MAC',
        'IPHONE', 'ANDROID', 'MOBIL', 'VDI', 'CITRIX', 'OMNISSA', 'MICROSOFT',
        'PUZZEL', 'PHONERO', 'MURAL', 'ALTINN', 'AURORA', 'MFA', 'APPLE',
        'LÆRINGSPORTALEN', 'INTRANETT', 'UNIT4', 'VENTUS', 'AUTOHOTKEY',
        'OBI', 'POWERPOINT', 'UNIFLOW', 'MATTERMOST', 'DVH', 'BITLOCKER',
        'MATOMO', 'ONENOTE', 'PLANNER'
    }

def extract_primary_system_from_filename(filename: str):
    """
    Extract the primary system from a filename like "CurrentSystem - PrimarySystem topic...".
    
    Returns (current_system, primary_system, topic) or (None, None, None) if no match.
    """
    
    # Remove .pdf extension
    name_without_ext = filename
    if name_without_ext.lower().endswith('.pdf'):
        name_without_ext = name_without_ext[:-4]
    
    # Look for pattern: "System - Topic ..."
    if ' - ' in name_without_ext:
        parts = name_without_ext.split(' - ', 1)
        current_system = parts[0].strip()
        remaining = parts[1].strip()
        
        if remaining:
            # Extract first word as potential primary system
            topic_parts = remaining.split()
            if topic_parts:
                potential_primary = topic_parts[0].strip('.,;:!?()[]{}')
                
                independent_systems = get_independent_systems()
                
                if potential_primary.upper() in independent_systems:
                    return current_system, potential_primary.upper(), remaining
    
    return None, None, None

def find_cross_system_files():
    """Find all files that should be moved to different system folders."""
    
    organized_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    
    if not organized_path.exists():
        print(f"❌ Error: Organized folder not found at {organized_path}")
        return []
    
    cross_system_files = []
    
    # Scan all system folders
    for system_folder in organized_path.iterdir():
        if not system_folder.is_dir():
            continue
        
        # Scan files in system folder and all sub-folders
        for file_path in system_folder.rglob("*.pdf"):
            current_system, primary_system, topic = extract_primary_system_from_filename(file_path.name)
            
            if primary_system and primary_system != system_folder.name.upper():
                cross_system_files.append({
                    'file_path': file_path,
                    'current_system': system_folder.name,
                    'target_system': primary_system.title(),
                    'topic': topic,
                    'filename': file_path.name
                })
    
    return cross_system_files

def move_cross_system_files(cross_system_files, dry_run=True):
    """Move files to their correct system folders."""
    
    organized_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    moved_count = 0
    created_folders = set()
    
    for file_info in cross_system_files:
        source_path = file_info['file_path']
        target_system = file_info['target_system']
        target_folder = organized_path / target_system
        
        # Create target folder if it doesn't exist
        if not target_folder.exists():
            if not dry_run:
                target_folder.mkdir(exist_ok=True)
            created_folders.add(target_system)
        
        # Determine target file path
        target_file_path = target_folder / source_path.name
        
        # Handle duplicates
        counter = 1
        original_target = target_file_path
        while target_file_path.exists():
            stem = original_target.stem
            suffix = original_target.suffix
            target_file_path = target_folder / f"{stem} ({counter}){suffix}"
            counter += 1
        
        if dry_run:
            print(f"   📄 Would move: {source_path.name[:60]}...")
            print(f"      From: {file_info['current_system']}/")
            print(f"      To:   {target_system}/")
        else:
            try:
                shutil.move(str(source_path), str(target_file_path))
                moved_count += 1
                print(f"   ✅ Moved: {source_path.name[:60]}...")
            except Exception as e:
                print(f"   ❌ Failed to move {source_path.name}: {e}")
    
    return moved_count, created_folders

def clean_empty_folders():
    """Remove empty folders after moving files."""
    
    organized_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    removed_folders = []
    
    # Find and remove empty sub-folders first, then empty system folders
    for system_folder in organized_path.iterdir():
        if not system_folder.is_dir():
            continue
        
        # Remove empty sub-folders
        for sub_folder in system_folder.iterdir():
            if sub_folder.is_dir() and not any(sub_folder.iterdir()):
                try:
                    sub_folder.rmdir()
                    removed_folders.append(f"{system_folder.name}/{sub_folder.name}")
                except Exception as e:
                    print(f"   ⚠️  Could not remove empty folder {sub_folder}: {e}")
        
        # Remove empty system folders
        if not any(system_folder.iterdir()):
            try:
                system_folder.rmdir()
                removed_folders.append(system_folder.name)
            except Exception as e:
                print(f"   ⚠️  Could not remove empty system folder {system_folder}: {e}")
    
    return removed_folders

def main():
    print("🔄 Cross-System File Fixer")
    print("=" * 50)
    print("Finding files that belong in different system folders...\n")
    
    # Find cross-system files
    cross_system_files = find_cross_system_files()
    
    if not cross_system_files:
        print("✅ No cross-system files found! All files are in correct system folders.")
        return
    
    # Group by target system for better overview
    by_target_system = defaultdict(list)
    for file_info in cross_system_files:
        by_target_system[file_info['target_system']].append(file_info)
    
    print(f"🔍 Found {len(cross_system_files)} files that need to be moved:")
    print("=" * 60)
    
    for target_system, files in sorted(by_target_system.items()):
        print(f"\n📂 {target_system}/ ({len(files)} files)")
        for file_info in files[:3]:  # Show first 3 examples
            print(f"   📄 {file_info['filename'][:70]}...")
            print(f"      Currently in: {file_info['current_system']}/")
        if len(files) > 3:
            print(f"   📄 ... and {len(files) - 3} more files")
    
    print(f"\n" + "=" * 60)
    print("🔄 Performing dry run to show what would be moved...")
    print("=" * 60)
    
    # Dry run
    move_cross_system_files(cross_system_files, dry_run=True)
    
    print(f"\n" + "=" * 60)
    user_input = input("Do you want to proceed with moving these files? (y/N): ").strip().lower()
    
    if user_input in ['y', 'yes']:
        print("\n🔄 Moving files to correct system folders...")
        moved_count, created_folders = move_cross_system_files(cross_system_files, dry_run=False)
        
        print("\n🧹 Cleaning up empty folders...")
        removed_folders = clean_empty_folders()
        
        print(f"\n✅ Cross-system file organization complete!")
        print(f"📊 Results:")
        print(f"   📄 Files moved: {moved_count}")
        print(f"   📁 New system folders created: {len(created_folders)}")
        if created_folders:
            print(f"      {', '.join(sorted(created_folders))}")
        print(f"   🗑️  Empty folders removed: {len(removed_folders)}")
        
        print(f"\n🎯 Recommendation: Run create_alphabetical_copy.py to update the alphabetical view!")
    else:
        print("\n❌ Operation cancelled. No files were moved.")

if __name__ == "__main__":
    main()