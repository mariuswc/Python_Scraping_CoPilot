#!/usr/bin/env python3
"""
Fresh start: Organize all PDFs from the original PDF Splitt folder
- Extract PDF headers
- Determine system names from headers
- Create alphabetical folder with format: (System) - Header
"""

import os
import shutil
import PyPDF2
import pdfplumber
import re
from collections import Counter

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
                            # Clean up the header
                            line = re.sub(r'\s+', ' ', line).strip()
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
                        # Clean up the header
                        line = re.sub(r'\s+', ' ', line).strip()
                        return line
    except:
        pass
    
    return None

def get_system_from_header(header):
    """Determine system name based on header content."""
    if not header:
        return "Unknown"
    
    header_lower = header.lower()
    
    # Comprehensive system mappings
    system_mappings = {
        'altinn': 'Altinn',
        'citrix': 'Citrix', 
        'dvh': 'DVH',
        'ess': 'ESS',
        'edge': 'Edge',
        'elements': 'Elements',
        'eskattekort': 'eSkattekort',
        'e-skattekort': 'eSkattekort',
        'excel': 'Excel',
        'folkeregister': 'Folkeregister',
        'freg': 'Folkeregister',
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
        'vmware': 'Omnissa',
        'onedrive': 'OneDrive',
        'onenote': 'OneNote',
        'outlook': 'Outlook',
        'powerpoint': 'PowerPoint',
        'sian': 'SIAN',
        'smia': 'SMIA',
        'sme': 'SME',
        'sharepoint': 'SharePoint',
        'skatteplikt': 'Skatteplikt',
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
        'acrobat': 'Adobe',
        'skatteetaten': 'Skatteetaten',
        'tax office': 'Skatteetaten',
        'kundeloggen': 'Kundeloggen',
        'customer log': 'Kundeloggen',
        'tilgangsportalen': 'Tilgangsportalen',
        'access portal': 'Tilgangsportalen',
        'viva engage': 'Viva',
        'viva': 'Viva',
        'office': 'Office',
        'bitlocker': 'BitLocker',
        'kryptering': 'BitLocker',
        'encryption': 'BitLocker',
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
        'forskudd': 'Forskudd',
        'skatteoppgjør': 'Skatteoppgjør',
        'puzzel': 'Puzzel',
        'magnet': 'Magnet',
        'checkpoint': 'CheckPoint',
        'vpn': 'VPN',
        'nemo': 'Ventus',
        'forms': 'Forms',
        'planner': 'Planner',
        'stream': 'Stream',
        'prean': 'PREAN',
        'innfri': 'INNFRI',
        'sharepoint': 'SharePoint',
        'sharepoint': 'SharePoint',
    }
    
    # Check for exact matches first (prioritize longer matches)
    sorted_keywords = sorted(system_mappings.keys(), key=len, reverse=True)
    for keyword in sorted_keywords:
        if keyword in header_lower:
            return system_mappings[keyword]
    
    # Check for number prefixes that might indicate systems
    if re.match(r'^\d+[\s\-]*([a-zA-Z]+)', header_lower):
        match = re.match(r'^\d+[\s\-]*([a-zA-Z]+)', header_lower)
        potential_system = match.group(1).lower()
        if potential_system in system_mappings:
            return system_mappings[potential_system]
    
    return "Other"

def clean_filename(filename):
    """Clean filename for filesystem compatibility."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Replace multiple spaces/underscores with single space
    filename = re.sub(r'[\s_]+', ' ', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename.strip()

def organize_pdfs_fresh_start(source_path):
    """Fresh organization of all PDFs from the original folder."""
    
    # Create output directory
    output_base = os.path.join(os.path.dirname(source_path), "PDF_Organized_Fresh")
    alphabetical_folder = os.path.join(output_base, "Alphabetical_All_PDFs")
    
    # Clean up if exists
    if os.path.exists(output_base):
        shutil.rmtree(output_base)
    
    os.makedirs(alphabetical_folder, exist_ok=True)
    
    print(f"🚀 Starting fresh organization from: {source_path}")
    print(f"📁 Output folder: {output_base}")
    
    # Find all PDF files
    all_pdfs = []
    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                all_pdfs.append(file_path)
    
    print(f"📄 Found {len(all_pdfs)} PDF files to process")
    
    if len(all_pdfs) == 0:
        print("❌ No PDF files found!")
        return
    
    processed_files = []
    skipped_files = []
    system_counts = Counter()
    
    for i, pdf_path in enumerate(all_pdfs, 1):
        if i % 100 == 0:
            print(f"   Processing {i}/{len(all_pdfs)} files...")
        
        try:
            # Extract header
            header = extract_pdf_header(pdf_path)
            if not header:
                print(f"⚠️  No header found: {os.path.basename(pdf_path)}")
                header = "Unknown Header"
            
            # Determine system
            system = get_system_from_header(header)
            system_counts[system] += 1
            
            # Create new filename: (System) - Header
            new_filename = f"({system}) - {header}"
            new_filename = clean_filename(new_filename) + ".pdf"
            
            # Handle duplicates
            target_path = os.path.join(alphabetical_folder, new_filename)
            counter = 1
            original_filename = new_filename
            while os.path.exists(target_path):
                name_part = original_filename[:-4]  # Remove .pdf
                new_filename = f"{name_part} ({counter}).pdf"
                target_path = os.path.join(alphabetical_folder, new_filename)
                counter += 1
            
            # Copy file
            shutil.copy2(pdf_path, target_path)
            
            processed_files.append({
                'original': pdf_path,
                'new_name': new_filename,
                'system': system,
                'header': header
            })
            
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(pdf_path)}: {e}")
            skipped_files.append(pdf_path)
    
    print(f"\n✅ Processing complete!")
    print(f"📄 Total files found: {len(all_pdfs)}")
    print(f"✅ Successfully processed: {len(processed_files)}")
    print(f"❌ Skipped files: {len(skipped_files)}")
    
    print(f"\n📊 System distribution:")
    for system, count in system_counts.most_common():
        print(f"   {system}: {count} files")
    
    print(f"\n📁 All files organized in: {alphabetical_folder}")
    print(f"📝 Files are named as: (System) - Header.pdf")
    
    return output_base

def main():
    """Main execution function."""
    # Default path - user can change this
    source_path = "/Users/marius.cook/Downloads/PDF splitt"
    
    print("🔍 Fresh PDF Organization Script")
    print("=" * 50)
    
    if not os.path.exists(source_path):
        print(f"❌ Source path does not exist: {source_path}")
        return
    
    # Start the organization
    result_path = organize_pdfs_fresh_start(source_path)
    
    if result_path:
        print(f"\n🎉 Organization complete!")
        print(f"📁 Check your results in: {result_path}")

if __name__ == "__main__":
    main()