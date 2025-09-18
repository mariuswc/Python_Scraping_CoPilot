#!/usr/bin/env python3
"""
Clean up weird format files from alphabetical_articles
Move files that start with numbers or non-system names to a separate folder
"""

import os
import shutil
from pathlib import Path
import re

def is_valid_system_name(filename: str) -> bool:
    """Check if filename starts with a valid system name."""
    
    # Known system names that should be kept in main folder (including short ones)
    valid_systems = {
        'adobe', 'altinn', 'aurora', 'citrix', 'confluence', 'chrome',
        'delingstjenester', 'docker', 'edge', 'ess', 'excel', 'exchange',
        'jira', 'koss', 'kubernetes', 'mac', 'mfa', 'microsoft', 'mobil',
        'mva', 'onenote', 'onedrive', 'oracle', 'outlook', 'pc', 'powerbi',
        'powerpoint', 'postgres', 'sap', 'sharepoint', 'sian', 'skatteplikt',
        'smia', 'sql', 'teams', 'tidbank', 'tilgangsportalen', 'uniflow',
        'unit4', 'vdi', 'ventus', 'vis', 'windows', 'word', 'jabra',
        'mattermost', 'autohotkey', 'omnissa', 'matomo', 'eskattekort',
        'bitlocker', 'dvh', 'obi', 'iphone', 'android', 'folkeregister',
        'elements', 'sofie', 'valutaregister', 'activedirectory', 'azure',
        'office365', 'o365', 'sl', 'i', 'n', 'zip', 'ublock', 'ørepropper'
    }
    
    # Extract first word before " - "
    if ' - ' in filename:
        first_part = filename.split(' - ')[0].lower().strip()
    else:
        # No " - " separator, use first word
        first_part = filename.split()[0].lower().strip()
    
    # Check various conditions for weird formats
    
    # 1. Starts with number - these are weird
    if re.match(r'^\d', first_part):
        return False
    
    # 2. Starts with special characters - these are weird
    if re.match(r'^[!@#$%^&*(),.?":{}|<>]', first_part):
        return False
    
    # 3. Check if it's a known valid system (case insensitive)
    if first_part in valid_systems:
        return True
    
    # 4. Check for non-system words that are clearly not systems
    non_system_words = {
        'når', 'lånekassen', 'trådløst', 'telefonkø', 'set-mailboxregionalconfiguration',
        'har', 'ikke', 'feil', 'hvordan', 'det', 'en', 'til', 'fra', 'med', 'på',
        'i', 'er', 'som', 'kan', 'skal', 'vil', 'blir', 'må', 'får', 'gjør',
        'bruker', 'innstillinger', 'problem', 'feilmelding', 'melding', 'varsel'
    }
    
    if first_part in non_system_words:
        return False
    
    # 5. If it's a proper word starting with letter, consider it valid
    # (This allows short system names like "Pc", "Sl", etc.)
    if re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', first_part):
        return True
    
    # Everything else is considered weird
    return False

def analyze_weird_files():
    """Analyze and categorize weird format files."""
    
    source_dir = Path("/Users/marius.cook/Desktop/scrape/alphabetical_articles")
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return
    
    pdf_files = list(source_dir.glob("*.pdf"))
    print(f"📄 Analyzing {len(pdf_files)} files...")
    
    weird_files = []
    valid_files = []
    
    categories = {
        'starts_with_number': [],
        'starts_with_special': [],
        'very_short': [],
        'only_special_chars': [],
        'other_weird': []
    }
    
    for pdf_file in pdf_files:
        filename = pdf_file.name
        
        if is_valid_system_name(filename):
            valid_files.append(pdf_file)
        else:
            weird_files.append(pdf_file)
            
            # Categorize the weird file
            first_char = filename[0] if filename else ''
            if first_char.isdigit():
                categories['starts_with_number'].append(filename)
            elif re.match(r'^[!@#$%^&*(),.?":{}|<>]', first_char):
                categories['starts_with_special'].append(filename)
            elif len(filename.split()[0] if filename.split() else '') <= 2:
                categories['very_short'].append(filename)
            elif re.match(r'^[^a-zA-Z]+', filename):
                categories['only_special_chars'].append(filename)
            else:
                categories['other_weird'].append(filename)
    
    print(f"\n📊 Analysis Results:")
    print(f"✅ Valid system files: {len(valid_files)}")
    print(f"❓ Weird format files: {len(weird_files)}")
    
    print(f"\n📋 Weird file categories:")
    for category, files in categories.items():
        if files:
            print(f"  {category.replace('_', ' ').title()}: {len(files)} files")
            # Show first 5 examples
            for i, filename in enumerate(files[:5]):
                print(f"    - {filename}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")
            print()
    
    return weird_files, valid_files

def move_weird_files():
    """Move weird format files to separate folder."""
    
    source_dir = Path("/Users/marius.cook/Desktop/scrape/alphabetical_articles")
    weird_dir = Path("/Users/marius.cook/Desktop/scrape/weird_format_files")
    
    # Create weird files directory
    weird_dir.mkdir(parents=True, exist_ok=True)
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return
    
    pdf_files = list(source_dir.glob("*.pdf"))
    moved = 0
    kept = 0
    
    print(f"🔍 Processing {len(pdf_files)} files...")
    
    for pdf_file in pdf_files:
        if is_valid_system_name(pdf_file.name):
            kept += 1
        else:
            # Move to weird folder
            dest_path = weird_dir / pdf_file.name
            
            # Handle duplicates
            counter = 2
            while dest_path.exists():
                stem = pdf_file.stem
                dest_path = weird_dir / f"{stem} ({counter}).pdf"
                counter += 1
            
            shutil.move(str(pdf_file), str(dest_path))
            moved += 1
    
    print(f"\n🎉 Cleanup complete!")
    print(f"📁 Valid files kept in: {source_dir}")
    print(f"📁 Weird files moved to: {weird_dir}")
    print(f"✅ Files kept: {kept}")
    print(f"📦 Files moved: {moved}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "analyze":
        analyze_weird_files()
    elif len(sys.argv) > 1 and sys.argv[1] == "move":
        move_weird_files()
    else:
        print("Usage:")
        print("  python cleanup_weird_files.py analyze  - Analyze weird files")
        print("  python cleanup_weird_files.py move     - Move weird files to separate folder")