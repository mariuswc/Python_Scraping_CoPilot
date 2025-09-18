#!/usr/bin/env python3
"""
Analyze files in the 'Other' folder and reorganize them into proper system folders
based on their PDF headers and content patterns.
"""

import os
import shutil
import PyPDF2
import pdfplumber
from collections import Counter
import re

def extract_pdf_header(pdf_path):
    """Extract the header from a PDF file using multiple methods."""
    try:
        # Try pdfplumber first (better text extraction)
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                text = pdf.pages[0].extract_text()
                if text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    for line in lines[:15]:  # Check more lines
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

def find_header_in_text(text):
    """Find the most likely header in extracted text."""
    if not text:
        return None
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Skip common non-header patterns
    skip_patterns = [
        r'^\d+$',  # Just numbers
        r'^[\d\.\s]+$',  # Numbers, dots, spaces
        r'^[^\w]+$',  # No word characters
        r'^(side|page)\s*\d+',  # Page numbers
        r'^\d{1,2}[\.:]',  # Numbered lists like "1.", "12:"
    ]
    
    for line in lines[:20]:  # Check first 20 lines
        if len(line) < 5:
            continue
            
        # Skip if matches any skip pattern
        if any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue
            
        return line
    
    return None

def get_system_from_header(header):
    """Determine system folder based on header content."""
    if not header:
        return "Other"
    
    header_lower = header.lower()
    
    # Extended system mappings based on common Norwegian tax/government systems
    system_mappings = {
        # Existing systems
        'altinn': 'Altinn',
        'citrix': 'Citrix', 
        'dvh': 'DVH',
        'ess': 'ESS',
        'edge': 'Edge',
        'elements': 'Elements',
        'eskattekort': 'Eskattekort',
        'excel': 'Excel',
        'folkeregister': 'Folkeregister',
        'jabra': 'Jabra',
        'jira': 'Jira',
        'koss': 'KOSS',
        'mfa': 'MFA',
        'mattermost': 'Mattermost',
        'microsoft': 'Microsoft',
        'mobil': 'Mobil',
        'mva': 'Mva',
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
        'sme': 'Sme',
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
        
        # Additional systems to catch Aurora and other files
        'aurora': 'Aurora',
        'delingstjenester': 'Delingstjenester',
        'delingstjeneste': 'Delingstjenester',
        'eiendomsregister': 'Eiendomsregister',
        'adobe': 'Adobe',
        'figma': 'Figma',
        'mural': 'Mural',
        'balsamiq': 'Balsamiq',
        'calabrio': 'Calabrio',
        'phonero': 'Phonero',
        'lånekassen': 'Lånekassen',
        'lanekassen': 'Lånekassen',
        'valutaregister': 'Valutaregister',
        'valutaregisteret': 'Valutaregister',
        'confluence': 'Confluence',
        'wiki': 'Confluence',
        'passord': 'Passord',
        'password': 'Passord',
        'sikkerprint': 'Sikkerprint',
        'print': 'Sikkerprint',
        'utskrift': 'Sikkerprint',
        'firmaportal': 'Firmaportal',
        'company portal': 'Firmaportal',
        'chrome': 'Chrome',
        'browser': 'Chrome',
        'filutforsker': 'Filutforsker',
        'file explorer': 'Filutforsker',
        'oppgavebehandling': 'Oppgavebehandling',
        'task manager': 'Oppgavebehandling',
        'mac': 'Mac',
        'pc': 'PC',
        'computer': 'PC',
        'datamaskin': 'PC',
        'sql': 'SQL',
        'database': 'SQL',
        'lyd': 'Lyd',
        'audio': 'Lyd',
        'sound': 'Lyd',
        'startmeny': 'Startmeny',
        'start menu': 'Startmeny',
        'notater': 'Notater',
        'notes': 'Notater',
        'creative cloud': 'Adobe',
        'captivate': 'Adobe',
        'skatteetaten': 'Skatteetaten',
        'tax office': 'Skatteetaten',
        'kundeloggen': 'Kundeloggen',
        'customer log': 'Kundeloggen',
        'tilgangsportalen': 'Tilgangsportalen',
        'access portal': 'Tilgangsportalen',
        'viva engage': 'Viva',
        'viva': 'Viva',
        'office': 'Office',
        'bitlocker': 'Bitlocker',
        'kryptering': 'Bitlocker',
        'encryption': 'Bitlocker',
        'audit': 'Audit',
        'revisjon': 'Audit',
        'keesing': 'Keesing',
        'id kontroll': 'IDKontroll',
        'id-kontroll': 'IDKontroll',
        'identitetskontroll': 'IDKontroll',
        'zip': 'Zip',
        'arkiv': 'Arkiv',
        'archive': 'Arkiv',
        'esim': 'eSIM',
        'sim': 'eSIM',
    }
    
    # Check for exact matches first
    for keyword, system in system_mappings.items():
        if keyword in header_lower:
            return system
    
    # Check for number prefixes that might indicate systems
    if re.match(r'^\d+\s*(aurora|vis|sian|smia)', header_lower):
        match = re.match(r'^\d+\s*(aurora|vis|sian|smia)', header_lower)
        return system_mappings.get(match.group(1), 'Other')
    
    return "Other"

def analyze_other_folder(base_path):
    """Analyze all files in the Other folder and suggest reorganization."""
    other_folder = os.path.join(base_path, "organized_by_system", "Other")
    
    if not os.path.exists(other_folder):
        print("❌ Other folder not found!")
        return
    
    print("🔍 Analyzing files in Other folder...")
    
    files = [f for f in os.listdir(other_folder) if f.endswith('.pdf')]
    print(f"📄 Found {len(files)} PDF files to analyze")
    
    analysis_results = []
    system_counts = Counter()
    
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(other_folder, filename)
        
        if i % 50 == 0:
            print(f"   Processed {i}/{len(files)} files...")
        
        header = extract_pdf_header(file_path)
        if header:
            suggested_system = get_system_from_header(header)
            analysis_results.append((filename, header, suggested_system))
            system_counts[suggested_system] += 1
        else:
            analysis_results.append((filename, "No header found", "Other"))
            system_counts["Other"] += 1
    
    print(f"\n📊 Analysis complete! Found these system distributions:")
    for system, count in system_counts.most_common():
        print(f"   {system}: {count} files")
    
    return analysis_results, system_counts

def reorganize_other_folder(base_path, analysis_results):
    """Reorganize files from Other folder into appropriate system folders."""
    organized_path = os.path.join(base_path, "organized_by_system")
    other_folder = os.path.join(organized_path, "Other")
    
    moves_made = 0
    
    for filename, header, suggested_system in analysis_results:
        if suggested_system == "Other":
            continue  # Keep in Other folder
        
        source_path = os.path.join(other_folder, filename)
        target_folder = os.path.join(organized_path, suggested_system)
        target_path = os.path.join(target_folder, filename)
        
        # Create target folder if it doesn't exist
        os.makedirs(target_folder, exist_ok=True)
        
        try:
            if os.path.exists(source_path):
                shutil.move(source_path, target_path)
                print(f"📦 Moved: {filename[:60]}...")
                print(f"   Header: {header[:80]}...")
                print(f"   From: Other → {suggested_system}")
                moves_made += 1
        except Exception as e:
            print(f"❌ Error moving {filename}: {e}")
    
    print(f"\n✅ Reorganization complete! Moved {moves_made} files from Other folder")

def main():
    """Main execution function."""
    base_path = input("Enter the base path (e.g., /Users/marius.cook/Downloads/PDF splitt 2): ").strip()
    
    if not os.path.exists(base_path):
        print("❌ Path does not exist!")
        return
    
    # Step 1: Analyze the Other folder
    analysis_results, system_counts = analyze_other_folder(base_path)
    
    if not analysis_results:
        print("❌ No files to analyze!")
        return
    
    # Step 2: Show preview of what will be moved
    print(f"\n📋 Preview of reorganization:")
    print(f"   Files staying in Other: {system_counts.get('Other', 0)}")
    print(f"   Files being moved to system folders: {sum(count for system, count in system_counts.items() if system != 'Other')}")
    
    # Step 3: Auto-confirm and execute
    print("\nProceeding with reorganization...")
    reorganize_other_folder(base_path, analysis_results)
        
    # Show final counts
    print(f"\n📊 Final folder structure:")
    organized_path = os.path.join(base_path, "organized_by_system")
    for folder in sorted(os.listdir(organized_path)):
        folder_path = os.path.join(organized_path, folder)
        if os.path.isdir(folder_path):
            count = len([f for f in os.listdir(folder_path) if f.endswith('.pdf')])
            print(f"   {folder}: {count} files")

if __name__ == "__main__":
    main()