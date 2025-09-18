#!/usr/bin/env python3
"""
Simple Title-Based PDF Organizer
================================

Simple rule: The FIRST WORD in the PDF title determines which folder it goes in.

Examples:
- "OneDrive Citrix ikke synkronisert" → OneDrive folder
- "Teams møte fungerer ikke" → Teams folder  
- "SMIA skattemelding problem" → SMIA folder
"""

import os
import re
import shutil
from pathlib import Path
import PyPDF2
import pdfplumber
from typing import Optional

# System folder mapping (normalize different variations)
SYSTEM_MAPPING = {
    # Exact matches first
    'ONEDRIVE': 'OneDrive',
    'TEAMS': 'Teams', 
    'OUTLOOK': 'Outlook',
    'SHAREPOINT': 'SharePoint',
    'CITRIX': 'Citrix',
    'SMIA': 'SMIA',
    'KOSS': 'KOSS',
    'SIAN': 'SIAN',
    'MFA': 'MFA',
    'SKATTEPLIKT': 'Skatteplikt',
    'MVA': 'Mva',
    'ESS': 'ESS',
    'TIDBANK': 'Tidbank',
    'FOLKEREGISTER': 'Folkeregister',
    'VIS': 'VIS',
    'ELEMENTS': 'Elements',
    'SOFIE': 'Sofie',
    'AURORA': 'Aurora',
    'WORD': 'Word',
    'EXCEL': 'Excel',
    'POWERPOINT': 'PowerPoint',
    'ONENOTE': 'OneNote',
    'WINDOWS': 'Windows',
    'MOBIL': 'Mobil',
    'IPHONE': 'iPhone',
    'ANDROID': 'Android',
    'CHROME': 'Chrome',
    'EDGE': 'Edge',
    'JIRA': 'Jira',
    'UNIT4': 'Unit4',
    'VDI': 'VDI',
    'BITLOCKER': 'Bitlocker',
    'DVH': 'DVH',
    'OBI': 'OBI',
    'UNIFLOW': 'Uniflow',
    'AUTOHOTKEY': 'Autohotkey',
    'OMNISSA': 'Omnissa',
    'VENTUS': 'Ventus',
    'MATOMO': 'Matomo',
    'ESKATTEKORT': 'Eskattekort',
    'MICROSOFT': 'Microsoft',
    'JABRA': 'Jabra',
    'ALTINN': 'Altinn',
    'MATTERMOST': 'Mattermost',
    
    # Common variations
    'SME': 'Sme',
    'TIDBANK': 'Tidbank',
    'SHAREPOINT': 'SharePoint',
}

def extract_title_from_pdf(file_path: str) -> Optional[str]:
    """Extract the first line/title from PDF content."""
    try:
        # Try pdfplumber first
        with pdfplumber.open(file_path) as pdf:
            if pdf.pages:
                text = pdf.pages[0].extract_text()
                if text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    if lines:
                        return lines[0]
    except:
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if pdf_reader.pages:
                    text = pdf_reader.pages[0].extract_text()
                    if text:
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        if lines:
                            return lines[0]
        except:
            pass
    
    return None

def get_first_word_system(title: str) -> str:
    """Get the system name based on the first word of the title."""
    if not title:
        return 'Other'
    
    # Clean the title and get first word
    title = title.strip()
    first_word = title.split()[0] if title.split() else ''
    
    # Remove common prefixes and clean
    first_word = re.sub(r'^(SYSTEM|APP|APPLICATION)[:.]?\s*', '', first_word, flags=re.IGNORECASE)
    first_word = first_word.upper().strip('.,;:')
    
    # Check direct mapping
    if first_word in SYSTEM_MAPPING:
        return SYSTEM_MAPPING[first_word]
    
    return 'Other'

def fix_title_based_organization(base_dir: str):
    """Fix organization based on first word in PDF titles."""
    organized_dir = os.path.join(base_dir, "organized_by_system")
    
    if not os.path.exists(organized_dir):
        print(f"Error: {organized_dir} not found")
        return
    
    print(f"🔧 Fixing organization based on PDF title first words...")
    print(f"📂 Processing: {organized_dir}")
    
    total_files = 0
    moved_files = 0
    
    # Process each folder
    for folder_name in os.listdir(organized_dir):
        folder_path = os.path.join(organized_dir, folder_name)
        
        if not os.path.isdir(folder_path):
            continue
            
        print(f"\n📁 Processing {folder_name} folder...")
        
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        
        for filename in pdf_files:
            file_path = os.path.join(folder_path, filename)
            total_files += 1
            
            try:
                # Extract title from PDF
                title = extract_title_from_pdf(file_path)
                if not title:
                    print(f"   ⚠️  No title found: {filename}")
                    continue
                
                # Determine correct system based on first word
                correct_system = get_first_word_system(title)
                current_system = folder_name
                
                print(f"   📄 {filename}")
                print(f"      Title: {title}")
                print(f"      First word → {correct_system}")
                
                # Check if file needs to be moved
                if current_system != correct_system:
                    # Create correct folder
                    correct_folder_path = os.path.join(organized_dir, correct_system)
                    os.makedirs(correct_folder_path, exist_ok=True)
                    
                    # Create new filename with correct prefix
                    clean_title = title
                    if ' - ' in filename:
                        # Keep the part after the first " - "
                        parts = filename.split(' - ', 1)
                        if len(parts) > 1:
                            clean_title = parts[1].replace('.pdf', '')
                    
                    new_filename = f"{correct_system.upper()} - {clean_title}.pdf"
                    new_filename = re.sub(r'[<>:"/\\|?*]', '_', new_filename)
                    new_filename = new_filename.replace('  ', ' ')
                    
                    # Create target path
                    target_path = os.path.join(correct_folder_path, new_filename)
                    
                    # Handle duplicates
                    counter = 1
                    base_name = new_filename.replace('.pdf', '')
                    while os.path.exists(target_path):
                        new_filename = f"{base_name} ({counter}).pdf"
                        target_path = os.path.join(correct_folder_path, new_filename)
                        counter += 1
                    
                    # Move file
                    shutil.move(file_path, target_path)
                    print(f"      ✅ Moved: {current_system} → {correct_system}")
                    moved_files += 1
                else:
                    print(f"      ✅ Already correct")
                
            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")
    
    print(f"\n✅ Title-based organization fix complete!")
    print(f"   📄 Total files processed: {total_files}")
    print(f"   📦 Files moved: {moved_files}")
    
    # Show final folder statistics
    print(f"\n📊 Final organization:")
    for folder_name in sorted(os.listdir(organized_dir)):
        folder_path = os.path.join(organized_dir, folder_name)
        if os.path.isdir(folder_path):
            count = len([f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')])
            if count > 0:
                print(f"   {folder_name}: {count} files")

if __name__ == "__main__":
    # Get base directory path
    base_dir = input("Enter the path to your PDF base directory (contains organized_by_system folder): ").strip()
    
    if not os.path.exists(base_dir):
        print(f"Error: Directory {base_dir} does not exist")
        exit(1)
    
    fix_title_based_organization(base_dir)