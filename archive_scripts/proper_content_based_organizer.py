#!/usr/bin/env python3
"""
Proper Content-Based PDF Organizer
==================================

This script properly organizes PDFs by:
1. Reading the actual PDF content to extract the real article title
2. Determining the correct system based on content analysis
3. Moving files to appropriate folders with correct naming

The key insight is that many PDFs are misplaced because they mention multiple systems,
but we need to categorize based on the PRIMARY system the article is about.
"""

import os
import re
import shutil
from pathlib import Path
import PyPDF2
import pdfplumber
from typing import Dict, List, Tuple, Optional

# System detection patterns (prioritized by specificity)
SYSTEM_PATTERNS = {
    # Primary Tax Systems (highest priority for Norwegian tax office)
    'Skatteplikt': [
        r'\bSkatteplikt\b', r'\bskattepliktig\b', r'\bskattepliktbegrensning\b',
        r'\bFritak fra skatteplikt\b', r'\bbegrenset skattepliktig\b'
    ],
    'SMIA': [
        r'\bSMIA\b(?!\s*-\s*)', r'\bSkattemeldingsløsning\b', 
        r'\bSkattemelding\b(?=.*behandling)', r'\bmyndighetsfastsetting\b'
    ],
    'KOSS': [
        r'\bKOSS\b(?!\s*-\s*)', r'\bKontrollsak\b', r'\bkontrollaktivitet\b',
        r'\bkontrollteam\b', r'\bleveranse\b(?=.*kontroll)'
    ],
    'Sme': [
        r'\bSME\b(?!\s*-\s*)', r'\bSkattemelding\b(?=.*elektronisk)',
        r'\bNæringsspesifikasjon\b', r'\bRF-1030\b'
    ],
    'SIAN': [
        r'\bSIAN\b(?!\s*-\s*)', r'\bSaksbehandlingsløsning\b',
        r'\bSaksbehandling\b(?=.*administrativ)'
    ],
    'Mva': [
        r'\bMVA\b(?!\s*-\s*)', r'\bMerverdiavgift\b', r'\bMVA-melding\b',
        r'\bMVA-sak\b', r'\bMVA-kontroll\b'
    ],
    'VIS': [
        r'\bVIS\b(?!\s*-\s*)', r'\bVirksomhetsinformasjonssystem\b',
        r'\bVirksomhetsopplysninger\b'
    ],
    'ESS': [
        r'\bESS\b(?!\s*-\s*)', r'\bEmployee Self Service\b',
        r'\bReiseregning\b', r'\bAttest\b(?=.*reise)'
    ],
    'Folkeregister': [
        r'\bFolkeregister\b', r'\bFREG\b', r'\bFolkeregistrering\b',
        r'\bD-nummer\b', r'\bBosetting\b'
    ],
    'Tidbank': [
        r'\btidBANK\b', r'\bTidbank\b', r'\bTidregistrering\b',
        r'\bFleksitid\b', r'\bOvertid\b'
    ],
    
    # Microsoft Office Suite
    'Teams': [
        r'\bTeams\b(?!\s*-\s*)', r'\bMicrosoft Teams\b', r'\bTeams-møte\b',
        r'\bTeamsmøter\b', r'\bChat\b(?=.*Teams)'
    ],
    'Outlook': [
        r'\bOutlook\b(?!\s*-\s*)', r'\bE-post\b', r'\bKalender\b(?=.*Outlook)',
        r'\bPostboks\b', r'\bE-mail\b'
    ],
    'SharePoint': [
        r'\bSharePoint\b(?!\s*-\s*)', r'\bSharepoint\b', r'\bSamarbeidsområde\b',
        r'\bDokumentbibliotek\b'
    ],
    'Word': [
        r'\bWord\b(?!\s*-\s*)', r'\bMicrosoft Word\b', r'\bDokument\b(?=.*Word)',
        r'\bTekstbehandling\b'
    ],
    'Excel': [
        r'\bExcel\b(?!\s*-\s*)', r'\bMicrosoft Excel\b', r'\bRegneark\b',
        r'\bSpreadsheet\b'
    ],
    'PowerPoint': [
        r'\bPowerPoint\b(?!\s*-\s*)', r'\bMicrosoft PowerPoint\b',
        r'\bPresentasjon\b'
    ],
    'OneNote': [
        r'\bOneNote\b(?!\s*-\s*)', r'\bMicrosoft OneNote\b', r'\bNotatblokk\b',
        r'\bDigitale notater\b'
    ],
    
    # IT Infrastructure & Security
    'MFA': [
        r'\bMFA\b(?!\s*-\s*)', r'\bMulti-factor authentication\b',
        r'\bTofaktor\b', r'\bAuthenticator\b'
    ],
    'Citrix': [
        r'\bCitrix\b(?!\s*-\s*)', r'\bCitrix Workspace\b', r'\bVDI\b(?=.*Citrix)',
        r'\bVirtuell desktop\b'
    ],
    'VDI': [
        r'\bVDI\b(?!\s*-\s*)', r'\bVirtuell desktop\b', r'\bVMware\b',
        r'\bVirtual Desktop Infrastructure\b'
    ],
    'Windows': [
        r'\bWindows\b(?!\s*-\s*)', r'\bWindows 10\b', r'\bWindows 11\b',
        r'\bOperativsystem\b'
    ],
    'Chrome': [
        r'\bChrome\b(?!\s*-\s*)', r'\bGoogle Chrome\b', r'\bNettleser\b(?=.*Chrome)'
    ],
    'Edge': [
        r'\bEdge\b(?!\s*-\s*)', r'\bMicrosoft Edge\b', r'\bNettleser\b(?=.*Edge)'
    ],
    
    # Mobile & Communication
    'Mobil': [
        r'\bMobil\b(?!\s*-\s*)', r'\bMobiltelefon\b', r'\bTelefon\b(?=.*mobil)',
        r'\bSmartphone\b', r'\biPhone\b(?=.*mobil)'
    ],
    'iPhone': [
        r'\biPhone\b(?!\s*-\s*)', r'\bApple\b(?=.*telefon)', r'\biOS\b'
    ],
    'Android': [
        r'\bAndroid\b(?!\s*-\s*)', r'\bAndroid-telefon\b'
    ],
    
    # Business Applications
    'Unit4': [
        r'\bUnit4\b(?!\s*-\s*)', r'\bUnit 4\b', r'\bØkonomi\b(?=.*Unit4)',
        r'\bFaktura\b(?=.*Unit4)'
    ],
    'Jira': [
        r'\bJira\b(?!\s*-\s*)', r'\bJIRA\b', r'\bService Desk\b(?=.*Jira)',
        r'\bProsjektstyring\b'
    ],
    'Mattermost': [
        r'\bMattermost\b(?!\s*-\s*)', r'\bChat\b(?=.*Mattermost)'
    ],
    
    # Specialized Tools
    'Aurora': [
        r'\bAurora\b(?!\s*-\s*)(?!\s*konsoll)', r'\bAurora-system\b',
        r'\bAurora-plattform\b'
    ],
    'Elements': [
        r'\bElements\b(?!\s*-\s*)', r'\bArkivsystem\b', r'\bDokumentarkiv\b'
    ],
    'Sofie': [
        r'\bSOFIE\b(?!\s*-\s*)', r'\bSofie\b(?!\s*-\s*)', 
        r'\bSentralt\s+oppfølgings\s+og\s+fakturasystem\b'
    ],
    'OBI': [
        r'\bOBI\b(?!\s*-\s*)', r'\bOracle Business Intelligence\b'
    ],
    'DVH': [
        r'\bDVH\b(?!\s*-\s*)', r'\bData Warehouse\b', r'\bDatavarehus\b'
    ],
    'Uniflow': [
        r'\bUniFLOW\b(?!\s*-\s*)', r'\bUniflow\b(?!\s*-\s*)', r'\bPrint\b(?=.*Uniflow)'
    ],
    'Bitlocker': [
        r'\bBitLocker\b(?!\s*-\s*)', r'\bBitlocker\b(?!\s*-\s*)', r'\bKryptering\b'
    ],
    'Autohotkey': [
        r'\bAutoHotkey\b(?!\s*-\s*)', r'\bAutoHotKey\b(?!\s*-\s*)', r'\bAHK\b'
    ],
    'Omnissa': [
        r'\bOmnissa\b(?!\s*-\s*)', r'\bHorizon Client\b'
    ],
    'Ventus': [
        r'\bVentus\b(?!\s*-\s*)', r'\bTimebestilling\b(?=.*Ventus)'
    ],
    'Matomo': [
        r'\bMatomo\b(?!\s*-\s*)', r'\bAnalytics\b(?=.*Matomo)'
    ],
    'Eskattekort': [
        r'\beSkattekort\b(?!\s*-\s*)', r'\bElektronisk skattekort\b'
    ],
    'Microsoft': [
        r'\bMicrosoft\b(?!\s*-\s*)(?!.*Teams|.*Outlook|.*Word|.*Excel|.*PowerPoint)',
        r'\bWhiteboard\b(?=.*Microsoft)'
    ],
    'Jabra': [
        r'\bJabra\b(?!\s*-\s*)', r'\bHodetelefoner\b(?=.*Jabra)', r'\bEarbuds\b'
    ],
    'Altinn': [
        r'\bAltinn\b(?!\s*-\s*)', r'\bDigital forvaltning\b'
    ]
}

def extract_article_title(file_path: str, max_pages: int = 3) -> Optional[str]:
    """
    Extract the main article title from PDF content.
    
    Args:
        file_path: Path to the PDF file
        max_pages: Maximum number of pages to analyze
        
    Returns:
        Extracted title or None if not found
    """
    try:
        # Try with pdfplumber first (better text extraction)
        with pdfplumber.open(file_path) as pdf:
            for page_num in range(min(max_pages, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if text:
                    # Look for title patterns
                    title = find_title_in_text(text)
                    if title:
                        return title
                        
        # Fallback to PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(min(max_pages, len(pdf_reader.pages))):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                if text:
                    title = find_title_in_text(text)
                    if title:
                        return title
                        
    except Exception as e:
        print(f"Error extracting title from {file_path}: {e}")
        
    return None

def find_title_in_text(text: str) -> Optional[str]:
    """
    Find the main title in extracted text.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        Title string or None if not found
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        return None
    
    # Skip common headers and metadata
    skip_patterns = [
        r'^(Innhold fra skjema|System eller applikasjon|Din henvendelse)',
        r'^(Beskriv|Hva gjorde du|Hvilke)',
        r'^(Page \d+|Side \d+)',
        r'^(\d{1,2}[./]\d{1,2}[./]\d{2,4})',  # Dates
        r'^(https?://)',  # URLs
        r'^[A-Z]{2,}\s*$',  # All caps single words
        r'^(PDF|Document|File)',
        r'^(Portal|Brukerportalen)',
        r'^\w+@\w+\.',  # Email addresses
    ]
    
    for line in lines[:10]:  # Check first 10 lines
        # Skip empty lines or lines with only special characters
        if not line or len(line.strip()) < 5:
            continue
            
        # Skip lines matching skip patterns
        if any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue
            
        # Look for lines that look like titles
        # Title characteristics:
        # - Usually one of the first meaningful lines
        # - Contains actual content (not just system names)
        # - Not too long (under 200 chars)
        # - Contains letters (not just numbers/symbols)
        
        if (len(line) > 10 and len(line) < 200 and 
            re.search(r'[a-zA-ZæøåÆØÅ]', line) and
            not line.isupper()):  # Not all uppercase
            
            # Clean up the title
            title = clean_title(line)
            if title and len(title) > 5:
                return title
    
    return None

def clean_title(title: str) -> str:
    """
    Clean and normalize the extracted title.
    
    Args:
        title: Raw title string
        
    Returns:
        Cleaned title string
    """
    # Remove common prefixes and suffixes
    title = re.sub(r'^(System eller applikasjon|Beskriv problemet|Din henvendelse)\s*:?\s*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*(Beskriv|Hva|Hvilke).*$', '', title, flags=re.IGNORECASE)
    
    # Remove file format indicators
    title = re.sub(r'\.(pdf|PDF)$', '', title)
    
    # Clean up spacing and punctuation
    title = re.sub(r'\s+', ' ', title)
    title = title.strip(' .,;:')
    
    return title

def determine_primary_system(file_path: str, content: str, filename: str) -> str:
    """
    Determine the primary system based on content analysis.
    
    Args:
        file_path: Path to the PDF file
        content: Full text content of the PDF
        filename: Original filename
        
    Returns:
        Primary system name
    """
    # Count matches for each system
    system_scores = {}
    
    for system, patterns in SYSTEM_PATTERNS.items():
        score = 0
        for pattern in patterns:
            # Count matches in content (weight: 3)
            content_matches = len(re.findall(pattern, content, re.IGNORECASE))
            score += content_matches * 3
            
            # Count matches in filename (weight: 1)
            filename_matches = len(re.findall(pattern, filename, re.IGNORECASE))
            score += filename_matches * 1
        
        if score > 0:
            system_scores[system] = score
    
    if not system_scores:
        return 'Other'
    
    # Return system with highest score
    primary_system = max(system_scores.items(), key=lambda x: x[1])[0]
    
    # Debug output for problematic cases
    if len(system_scores) > 1:
        sorted_scores = sorted(system_scores.items(), key=lambda x: x[1], reverse=True)
        print(f"Multi-system file: {filename}")
        print(f"  Scores: {sorted_scores[:3]}")
        print(f"  Primary: {primary_system}")
    
    return primary_system

def process_pdf_file(file_path: str, organized_dir: str) -> bool:
    """
    Process a single PDF file: extract title, determine system, move to correct folder.
    
    Args:
        file_path: Path to the PDF file to process
        organized_dir: Base directory for organized files
        
    Returns:
        True if successful, False otherwise
    """
    try:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}")
        
        # Extract full content
        full_content = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages[:5]:  # First 5 pages
                    text = page.extract_text()
                    if text:
                        full_content += text + "\n"
        except:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages[:5]:
                        text = page.extract_text()
                        if text:
                            full_content += text + "\n"
            except Exception as e:
                print(f"  Error reading content: {e}")
                return False
        
        if not full_content.strip():
            print(f"  No content extracted")
            return False
        
        # Determine primary system
        primary_system = determine_primary_system(file_path, full_content, filename)
        
        # Extract article title
        article_title = extract_article_title(file_path)
        if not article_title:
            article_title = filename.replace('.pdf', '')
        
        # Create new filename
        new_filename = f"{primary_system.upper()} - {article_title}.pdf"
        
        # Ensure filename is valid
        new_filename = re.sub(r'[<>:"/\\|?*]', '_', new_filename)
        new_filename = new_filename.replace('  ', ' ')
        
        # Create target directory
        target_dir = os.path.join(organized_dir, primary_system)
        os.makedirs(target_dir, exist_ok=True)
        
        # Create target path
        target_path = os.path.join(target_dir, new_filename)
        
        # Handle duplicate filenames
        counter = 1
        base_name = new_filename.replace('.pdf', '')
        while os.path.exists(target_path):
            new_filename = f"{base_name} ({counter}).pdf"
            target_path = os.path.join(target_dir, new_filename)
            counter += 1
        
        # Move file
        shutil.move(file_path, target_path)
        print(f"  → {primary_system}/{new_filename}")
        
        return True
        
    except Exception as e:
        print(f"  Error processing {filename}: {e}")
        return False

def reorganize_all_pdfs(source_dir: str):
    """
    Reorganize all PDFs in the source directory using proper content analysis.
    
    Args:
        source_dir: Directory containing the organized_by_system folder
    """
    organized_dir = os.path.join(source_dir, "organized_by_system")
    
    if not os.path.exists(organized_dir):
        print(f"Error: {organized_dir} not found")
        return
    
    print(f"🔧 Starting proper content-based reorganization")
    print(f"📂 Source: {organized_dir}")
    
    # Collect all PDF files
    all_pdfs = []
    for root, dirs, files in os.walk(organized_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                all_pdfs.append(file_path)
    
    print(f"📄 Found {len(all_pdfs)} PDF files")
    
    # Create temporary directory for processing
    temp_dir = os.path.join(source_dir, "temp_reorganize")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Move all files to temp directory first
    print("📦 Moving files to temporary directory...")
    for file_path in all_pdfs:
        filename = os.path.basename(file_path)
        temp_path = os.path.join(temp_dir, filename)
        
        # Handle duplicates
        counter = 1
        base_name = filename.replace('.pdf', '')
        while os.path.exists(temp_path):
            new_name = f"{base_name}_{counter}.pdf"
            temp_path = os.path.join(temp_dir, new_name)
            counter += 1
        
        shutil.move(file_path, temp_path)
    
    # Remove old organized directory
    shutil.rmtree(organized_dir)
    os.makedirs(organized_dir, exist_ok=True)
    
    # Process all files from temp directory
    temp_files = [f for f in os.listdir(temp_dir) if f.lower().endswith('.pdf')]
    successful = 0
    failed = 0
    
    print(f"\n🔄 Processing {len(temp_files)} files...")
    
    for filename in temp_files:
        temp_path = os.path.join(temp_dir, filename)
        if process_pdf_file(temp_path, organized_dir):
            successful += 1
        else:
            failed += 1
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    print(f"\n✅ Reorganization complete!")
    print(f"   Successfully processed: {successful}")
    print(f"   Failed: {failed}")
    
    # Show final statistics
    print(f"\n📊 Final organization:")
    system_counts = {}
    for item in os.listdir(organized_dir):
        item_path = os.path.join(organized_dir, item)
        if os.path.isdir(item_path):
            count = len([f for f in os.listdir(item_path) if f.lower().endswith('.pdf')])
            system_counts[item] = count
    
    for system, count in sorted(system_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {system}: {count} files")

if __name__ == "__main__":
    # Get source directory
    source_dir = input("Enter the path to your PDF directory (contains organized_by_system folder): ").strip()
    
    if not os.path.exists(source_dir):
        print(f"Error: Directory {source_dir} does not exist")
        exit(1)
    
    reorganize_all_pdfs(source_dir)