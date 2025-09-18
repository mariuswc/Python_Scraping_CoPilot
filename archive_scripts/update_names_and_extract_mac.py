#!/usr/bin/env python3
"""
1. Update alphabetical folder filenames to format: "(appname) - title"
2. Extract files containing "mac" to a "Possibly Mac" folder
"""

import os
import shutil
import PyPDF2
import pdfplumber
import re

def extract_pdf_header(pdf_path):
    """Extract the header from a PDF file using multiple methods."""
    try:
        # Try pdfplumber first
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                text = pdf.pages[0].extract_text()
                if text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    for line in lines[:15]:
                        if len(line) > 5 and not line.isdigit() and not re.match(r'^[\d\.\s]+$', line):
                            return line
    except:
        pass
    
    try:
        # Fallback to PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) > 0:
                text = reader.pages[0].extract_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                for line in lines[:15]:
                    if len(line) > 5 and not line.isdigit() and not re.match(r'^[\d\.\s]+$', line):
                        return line
    except:
        pass
    
    return None

def get_system_from_header(header):
    """Determine system/app name based on header content."""
    if not header:
        return "Unknown"
    
    header_lower = header.lower()
    
    # System mappings - return the proper case name for the app
    system_mappings = {
        'altinn': 'Altinn',
        'citrix': 'Citrix', 
        'dvh': 'DVH',
        'ess': 'ESS',
        'edge': 'Edge',
        'elements': 'Elements',
        'eskattekort': 'eSkattekort',
        'excel': 'Excel',
        'folkeregister': 'Folkeregister',
        'jabra': 'Jabra',
        'jira': 'Jira',
        'koss': 'KOSS',
        'mfa': 'MFA',
        'mattermost': 'Mattermost',
        'microsoft': 'Microsoft',
        'mobil': 'Mobil',
        'mva': 'MVA',
        'obi': 'OBI',
        'omnissa': 'Omnissa',
        'onedrive': 'OneDrive',
        'onenote': 'OneNote',
        'outlook': 'Outlook',
        'powerpoint': 'PowerPoint',
        'sian': 'SIAN',
        'smia': 'SMIA',
        'sharepoint': 'SharePoint',
        'skatteplikt': 'Skatteplikt',
        'sme': 'SME',
        'sofie': 'Sofie',
        'teams': 'Teams',
        'tidbank': 'Tidbank',
        'uniflow': 'Uniflow',
        'unit4': 'Unit4',
        'vdi': 'VDI',
        'vis': 'VIS',
        'ventus': 'Ventus',
        'windows': 'Windows',
        'word': 'Word',
        'iphone': 'iPhone',
        'aurora': 'Aurora',
        'delingstjenester': 'Delingstjenester',
        'eiendomsregister': 'Eiendomsregister',
        'adobe': 'Adobe',
        'figma': 'Figma',
        'mural': 'Mural',
        'balsamiq': 'Balsamiq',
        'calabrio': 'Calabrio',
        'phonero': 'Phonero',
        'lånekassen': 'Lånekassen',
        'valutaregister': 'Valutaregister',
        'confluence': 'Confluence',
        'wiki': 'Confluence',
        'passord': 'Passord',
        'sikkerprint': 'Sikkerprint',
        'firmaportal': 'Firmaportal',
        'chrome': 'Chrome',
        'filutforsker': 'Filutforsker',
        'mac': 'Mac',
        'pc': 'PC',
        'sql': 'SQL',
        'lyd': 'Lyd',
        'startmeny': 'Startmeny',
        'notater': 'Notater',
        'skatteetaten': 'Skatteetaten',
        'kundeloggen': 'Kundeloggen',
        'tilgangsportalen': 'Tilgangsportalen',
        'viva': 'Viva',
        'office': 'Office',
        'bitlocker': 'BitLocker',
        'audit': 'Audit',
        'keesing': 'Keesing',
        'zip': 'Zip',
    }
    
    # Check for exact matches first
    for keyword, system in system_mappings.items():
        if keyword in header_lower:
            return system
    
    # Check for number prefixes that might indicate systems
    if re.match(r'^\d+\s*(aurora|vis|sian|smia)', header_lower):
        match = re.match(r'^\d+\s*(aurora|vis|sian|smia)', header_lower)
        return system_mappings.get(match.group(1), 'Unknown')
    
    return "Unknown"

def clean_filename(filename):
    """Clean filename for filesystem compatibility."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Replace multiple spaces/underscores with single space
    filename = re.sub(r'[\s_]+', ' ', filename)
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename.strip()

def contains_mac(text):
    """Check if text contains 'mac' (case insensitive)."""
    if not text:
        return False
    return 'mac' in text.lower()

def update_alphabetical_names(base_path):
    """Update alphabetical folder to use (appname) - title format."""
    alphabetical_folder = os.path.join(base_path, "alphabetical_all_pdfs")
    
    if not os.path.exists(alphabetical_folder):
        print("❌ Alphabetical folder not found!")
        return
    
    print("🔄 Updating alphabetical folder names to (appname) - title format...")
    
    files = [f for f in os.listdir(alphabetical_folder) if f.endswith('.pdf')]
    updated_count = 0
    
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(alphabetical_folder, filename)
        
        if i % 100 == 0:
            print(f"   Processed {i}/{len(files)} files...")
        
        # Extract header from PDF
        header = extract_pdf_header(file_path)
        if not header:
            continue
        
        # Get app/system name
        app_name = get_system_from_header(header)
        
        # Create new filename: (appname) - title
        new_filename = f"({app_name}) - {header}"
        new_filename = clean_filename(new_filename) + ".pdf"
        
        # Skip if filename is already correct
        if filename == new_filename:
            continue
        
        new_file_path = os.path.join(alphabetical_folder, new_filename)
        
        # Handle duplicates
        counter = 1
        original_new_filename = new_filename
        while os.path.exists(new_file_path):
            name_part = original_new_filename[:-4]  # Remove .pdf
            new_filename = f"{name_part} ({counter}).pdf"
            new_file_path = os.path.join(alphabetical_folder, new_filename)
            counter += 1
        
        try:
            os.rename(file_path, new_file_path)
            print(f"📝 Renamed: {filename[:50]}...")
            print(f"     To: {new_filename[:50]}...")
            updated_count += 1
        except Exception as e:
            print(f"❌ Error renaming {filename}: {e}")
    
    print(f"✅ Updated {updated_count} filenames in alphabetical folder!")

def extract_mac_files(base_path):
    """Extract files containing 'mac' to a 'Possibly Mac' folder."""
    organized_folder = os.path.join(base_path, "organized_by_system")
    mac_folder = os.path.join(organized_folder, "Possibly Mac")
    
    if not os.path.exists(organized_folder):
        print("❌ Organized folder not found!")
        return
    
    # Create Possibly Mac folder
    os.makedirs(mac_folder, exist_ok=True)
    
    print("🔍 Searching for files containing 'mac'...")
    
    mac_files_found = []
    
    # Search through all system folders
    for folder_name in os.listdir(organized_folder):
        folder_path = os.path.join(organized_folder, folder_name)
        
        if not os.path.isdir(folder_path) or folder_name == "Possibly Mac":
            continue
        
        for filename in os.listdir(folder_path):
            if not filename.endswith('.pdf'):
                continue
            
            file_path = os.path.join(folder_path, filename)
            
            # Check filename for 'mac'
            if contains_mac(filename):
                mac_files_found.append((file_path, filename, folder_name, "filename"))
                continue
            
            # Check PDF content for 'mac'
            header = extract_pdf_header(file_path)
            if contains_mac(header):
                mac_files_found.append((file_path, filename, folder_name, "content"))
    
    print(f"📄 Found {len(mac_files_found)} files containing 'mac'")
    
    # Move files to Possibly Mac folder
    moved_count = 0
    for file_path, filename, source_folder, match_type in mac_files_found:
        target_path = os.path.join(mac_folder, filename)
        
        # Handle duplicates
        counter = 1
        original_filename = filename
        while os.path.exists(target_path):
            name_part = original_filename[:-4]  # Remove .pdf
            new_filename = f"{name_part} ({counter}).pdf"
            target_path = os.path.join(mac_folder, new_filename)
            counter += 1
        
        try:
            shutil.move(file_path, target_path)
            print(f"📦 Moved: {filename[:60]}...")
            print(f"     From: {source_folder} → Possibly Mac (matched in {match_type})")
            moved_count += 1
        except Exception as e:
            print(f"❌ Error moving {filename}: {e}")
    
    print(f"✅ Moved {moved_count} files to 'Possibly Mac' folder!")

def main():
    """Main execution function."""
    base_path = input("Enter the base path (e.g., /Users/marius.cook/Downloads/PDF splitt 2): ").strip()
    
    if not os.path.exists(base_path):
        print("❌ Path does not exist!")
        return
    
    print("🚀 Starting updates...")
    
    # Task 1: Update alphabetical folder names
    update_alphabetical_names(base_path)
    
    print("\n" + "="*60 + "\n")
    
    # Task 2: Extract Mac files
    extract_mac_files(base_path)
    
    print("\n✅ All tasks completed!")

if __name__ == "__main__":
    main()