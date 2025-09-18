#!/usr/bin/env python3
"""
Content-Based PDF Renaming Script
=================================

This script properly renames PDFs by:
1. Reading the actual PDF content to extract the real article title
2. Determining what the file is ACTUALLY about (not just what folder it's in)
3. Renaming files correctly as "[PRIMARY_SYSTEM] - [ACTUAL_TITLE]"

The key insight: A file named "Intranett - MFA" should actually be "MFA - [article title]"
if the content is primarily about MFA, not Intranett.
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
    # Authentication & Security (high priority)
    'MFA': [
        r'\bMFA\b(?!\s*-)', r'\bMulti-factor\s+authentication\b', r'\bTofaktor\b', 
        r'\bAuthenticator\b', r'\bGoogle\s+Authenticator\b', r'\bMicrosoft\s+Authenticator\b',
        r'\bSikkerhetsapp\b', r'\bTotrinnsbekreftelse\b'
    ],
    'Bitlocker': [
        r'\bBitLocker\b(?!\s*-)', r'\bBitlocker\b(?!\s*-)', r'\bKryptering\b', 
        r'\bDiskryptering\b', r'\bHarddisk\s+kryptering\b'
    ],
    
    # Primary Norwegian Tax Systems
    'Skatteplikt': [
        r'\bSkatteplikt\b(?!\s*-)', r'\bskattepliktig\b', r'\bskattepliktbegrensning\b',
        r'\bFritak\s+fra\s+skatteplikt\b', r'\bbegrenset\s+skattepliktig\b',
        r'\bskattekort\b', r'\bD-nummer\b(?=.*skatteplikt)'
    ],
    'SMIA': [
        r'\bSMIA\b(?!\s*-)', r'\bSkattemeldingsløsning\b', 
        r'\bSkattemelding\b(?=.*behandling)', r'\bmyndighetsfastsetting\b',
        r'\bSkatteoppgjør\b', r'\btilleggsskatt\b'
    ],
    'KOSS': [
        r'\bKOSS\b(?!\s*-)', r'\bKontrollsak\b', r'\bkontrollaktivitet\b',
        r'\bkontrollteam\b', r'\bleveranse\b(?=.*kontroll)', r'\bkontroll\b(?=.*KOSS)'
    ],
    'Sme': [
        r'\bSME\b(?!\s*-)', r'\bSkattemelding\b(?=.*elektronisk)',
        r'\bNæringsspesifikasjon\b', r'\bRF-1030\b', r'\bSkattemelding\b(?=.*næring)'
    ],
    'SIAN': [
        r'\bSIAN\b(?!\s*-)', r'\bSaksbehandlingsløsning\b',
        r'\bSaksbehandling\b(?=.*administrativ)', r'\bSentralt\s+inntaksapparat\b'
    ],
    'Mva': [
        r'\bMVA\b(?!\s*-)', r'\bMerverdiavgift\b', r'\bMVA-melding\b',
        r'\bMVA-sak\b', r'\bMVA-kontroll\b', r'\bMVA\s+SAK\b', r'\bMVA\s+SYS\b'
    ],
    'VIS': [
        r'\bVIS\b(?!\s*-)', r'\bVirksomhetsinformasjonssystem\b',
        r'\bVirksomhetsopplysninger\b'
    ],
    'ESS': [
        r'\bESS\b(?!\s*-)', r'\bEmployee\s+Self\s+Service\b',
        r'\bReiseregning\b', r'\bAttest\b(?=.*reise)', r'\bSelvbetjening\b(?=.*ansatt)'
    ],
    'Folkeregister': [
        r'\bFolkeregister\b(?!\s*-)', r'\bFREG\b(?!\s*-)', r'\bFolkeregistrering\b',
        r'\bD-nummer\b(?=.*folkeregister)', r'\bBosetting\b', r'\bInnflytting\b', r'\bUtflytting\b'
    ],
    'Tidbank': [
        r'\btidBANK\b(?!\s*-)', r'\bTidbank\b(?!\s*-)', r'\bTidregistrering\b',
        r'\bFleksitid\b', r'\bOvertid\b', r'\bFravær\b(?=.*tid)', r'\bFeriedager\b'
    ],
    'Sofie': [
        r'\bSOFIE\b(?!\s*-)', r'\bSofie\b(?!\s*-)', 
        r'\bSentralt\s+oppfølgings\s+og\s+fakturasystem\b', r'\bGebyr\b(?=.*SOFIE)',
        r'\bForfallsdato\b(?=.*giro)', r'\bBetalingskort\b'
    ],
    
    # Microsoft Office Suite
    'Teams': [
        r'\bTeams\b(?!\s*-)', r'\bMicrosoft\s+Teams\b', r'\bTeams-møte\b',
        r'\bTeamsmøter\b', r'\bChat\b(?=.*Teams)', r'\bMøte\b(?=.*Teams)'
    ],
    'Outlook': [
        r'\bOutlook\b(?!\s*-)', r'\bE-post\b', r'\bKalender\b(?=.*Outlook)',
        r'\bPostboks\b', r'\bE-mail\b', r'\bEpost\b', r'\bFellespostkasse\b'
    ],
    'SharePoint': [
        r'\bSharePoint\b(?!\s*-)', r'\bSharepoint\b(?!\s*-)', r'\bSamarbeidsområde\b',
        r'\bDokumentbibliotek\b', r'\bTeamområde\b'
    ],
    'Word': [
        r'\bWord\b(?!\s*-)(?!\s+dokument)', r'\bMicrosoft\s+Word\b', 
        r'\bTekstbehandling\b', r'\bDokument\b(?=.*Word)'
    ],
    'Excel': [
        r'\bExcel\b(?!\s*-)', r'\bMicrosoft\s+Excel\b', r'\bRegneark\b',
        r'\bSpreadsheet\b', r'\bKalkyl\b'
    ],
    'PowerPoint': [
        r'\bPowerPoint\b(?!\s*-)', r'\bMicrosoft\s+PowerPoint\b',
        r'\bPresentasjon\b(?=.*PowerPoint)'
    ],
    'OneNote': [
        r'\bOneNote\b(?!\s*-)', r'\bMicrosoft\s+OneNote\b', r'\bNotatblokk\b',
        r'\bDigitale\s+notater\b'
    ],
    
    # IT Infrastructure
    'Citrix': [
        r'\bCitrix\b(?!\s*-)', r'\bCitrix\s+Workspace\b', 
        r'\bApplikasjon\b(?=.*Citrix)', r'\bVirtuell\s+desktop\b(?=.*Citrix)'
    ],
    'VDI': [
        r'\bVDI\b(?!\s*-)', r'\bVirtuell\s+desktop\b(?!.*Citrix)', r'\bVMware\b',
        r'\bVirtual\s+Desktop\s+Infrastructure\b', r'\bOmnissa\b(?=.*VDI)'
    ],
    'Windows': [
        r'\bWindows\b(?!\s*-)', r'\bWindows\s+10\b', r'\bWindows\s+11\b',
        r'\bOperativsystem\b(?=.*Windows)', r'\bPC\b(?=.*Windows)'
    ],
    'Chrome': [
        r'\bChrome\b(?!\s*-)', r'\bGoogle\s+Chrome\b', r'\bNettleser\b(?=.*Chrome)'
    ],
    'Edge': [
        r'\bEdge\b(?!\s*-)', r'\bMicrosoft\s+Edge\b', r'\bNettleser\b(?=.*Edge)'
    ],
    
    # Mobile & Communication
    'Mobil': [
        r'\bMobil\b(?!\s*-)(?!\s*svar)', r'\bMobiltelefon\b', r'\bTelefon\b(?=.*mobil)',
        r'\bSmartphone\b', r'\bAndroid\b(?=.*telefon)', r'\bMobildata\b',
        r'\bWifi\b(?=.*mobil)', r'\bLadekabel\b'
    ],
    'iPhone': [
        r'\biPhone\b(?!\s*-)', r'\bApple\b(?=.*telefon)', r'\biOS\b(?=.*telefon)',
        r'\bICloud\b', r'\bFirmaportal\b(?=.*iPhone)'
    ],
    'Android': [
        r'\bAndroid\b(?!\s*-)(?!.*telefon)', r'\bAndroid-telefon\b'
    ],
    
    # Business Applications
    'Unit4': [
        r'\bUnit4\b(?!\s*-)', r'\bUnit\s+4\b', r'\bØkonomi\b(?=.*Unit4)',
        r'\bFaktura\b(?=.*Unit4)', r'\bAttest\b(?=.*Unit4)'
    ],
    'Jira': [
        r'\bJira\b(?!\s*-)', r'\bJIRA\b(?!\s*-)', r'\bService\s+Desk\b(?=.*Jira)',
        r'\bProsjektstyring\b(?=.*Jira)', r'\bSak\b(?=.*Jira)'
    ],
    'Mattermost': [
        r'\bMattermost\b(?!\s*-)', r'\bChat\b(?=.*Mattermost)', r'\bMF\b(?=.*Mattermost)'
    ],
    
    # Specialized Tools
    'Aurora': [
        r'\bAurora\b(?!\s*-)(?!\s*konsoll)(?!\s*-\s*\w)', r'\bAurora-system\b',
        r'\bAurora-plattform\b', r'\bAurora\s+konsoll\b'
    ],
    'Elements': [
        r'\bElements\b(?!\s*-)', r'\bArkivsystem\b(?=.*Elements)', 
        r'\bDokumentarkiv\b', r'\bArkivering\b(?=.*Elements)'
    ],
    'OBI': [
        r'\bOBI\b(?!\s*-)', r'\bOracle\s+Business\s+Intelligence\b',
        r'\bBI\s+Publisher\b(?=.*MVA)'
    ],
    'DVH': [
        r'\bDVH\b(?!\s*-)', r'\bData\s+Warehouse\b', r'\bDatavarehus\b',
        r'\bOracle\b(?=.*DVH)'
    ],
    'Uniflow': [
        r'\bUniFLOW\b(?!\s*-)', r'\bUniflow\b(?!\s*-)', 
        r'\bPrint\b(?=.*Uniflow)', r'\bSkriver\b(?=.*Uniflow)'
    ],
    'Autohotkey': [
        r'\bAutoHotkey\b(?!\s*-)', r'\bAutoHotKey\b(?!\s*-)', r'\bAHK\b(?!\s*-)'
    ],
    'Omnissa': [
        r'\bOmnissa\b(?!\s*-)', r'\bHorizon\s+Client\b'
    ],
    'Ventus': [
        r'\bVentus\b(?!\s*-)', r'\bTimebestilling\b(?=.*Ventus)'
    ],
    'Matomo': [
        r'\bMatomo\b(?!\s*-)', r'\bAnalytics\b(?=.*Matomo)'
    ],
    'Eskattekort': [
        r'\beSkattekort\b(?!\s*-)', r'\bElektronisk\s+skattekort\b',
        r'\bSkattekort\b(?=.*elektronisk)'
    ],
    'Microsoft': [
        r'\bMicrosoft\b(?!\s*-)(?!.*Teams|.*Outlook|.*Word|.*Excel|.*PowerPoint|.*OneNote)',
        r'\bWhiteboard\b(?=.*Microsoft)'
    ],
    'Jabra': [
        r'\bJabra\b(?!\s*-)', r'\bHodetelefoner\b(?=.*Jabra)', 
        r'\bEarbuds\b', r'\bEvolve\b(?=.*Jabra)'
    ],
    'Altinn': [
        r'\bAltinn\b(?!\s*-)', r'\bDigital\s+forvaltning\b',
        r'\bRolle\b(?=.*Altinn)', r'\bSigneringsrett\b'
    ]
}

def extract_pdf_content(file_path: str, max_pages: int = 3) -> str:
    """Extract text content from PDF file."""
    content = ""
    
    try:
        # Try pdfplumber first
        with pdfplumber.open(file_path) as pdf:
            for page_num in range(min(max_pages, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text()
                if text:
                    content += text + "\n"
    except:
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(min(max_pages, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
        except Exception as e:
            print(f"    Error reading {file_path}: {e}")
    
    return content

def extract_article_title(content: str) -> Optional[str]:
    """Extract the main article title from PDF content."""
    if not content.strip():
        return None
    
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
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
    
    for line in lines[:15]:  # Check first 15 lines
        if not line or len(line.strip()) < 5:
            continue
            
        # Skip lines matching skip patterns
        if any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue
            
        # Look for title-like lines
        if (len(line) > 10 and len(line) < 200 and 
            re.search(r'[a-zA-ZæøåÆØÅ]', line) and
            not line.isupper() and
            not re.match(r'^[\d\s\-_.]+$', line)):
            
            # Clean the title
            title = clean_title(line)
            if title and len(title) > 5:
                return title
    
    return None

def clean_title(title: str) -> str:
    """Clean and normalize the extracted title."""
    # Remove common prefixes
    title = re.sub(r'^(System eller applikasjon|Beskriv problemet|Din henvendelse)\s*:?\s*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*(Beskriv|Hva|Hvilke).*$', '', title, flags=re.IGNORECASE)
    
    # Remove file format indicators
    title = re.sub(r'\.(pdf|PDF)$', '', title)
    
    # Clean up spacing and punctuation
    title = re.sub(r'\s+', ' ', title)
    title = title.strip(' .,;:')
    
    return title

def determine_primary_system(content: str, filename: str) -> str:
    """Determine what system the file is primarily about based on content analysis."""
    system_scores = {}
    
    for system, patterns in SYSTEM_PATTERNS.items():
        score = 0
        for pattern in patterns:
            # Count matches in content (higher weight)
            content_matches = len(re.findall(pattern, content, re.IGNORECASE))
            score += content_matches * 5
            
            # Count matches in filename (lower weight)
            filename_matches = len(re.findall(pattern, filename, re.IGNORECASE))
            score += filename_matches * 1
        
        if score > 0:
            system_scores[system] = score
    
    if not system_scores:
        return 'Other'
    
    # Return system with highest score
    primary_system = max(system_scores.items(), key=lambda x: x[1])[0]
    
    return primary_system

def process_file(file_path: str) -> Tuple[str, str]:
    """
    Process a single PDF file to determine correct naming.
    
    Returns:
        Tuple of (primary_system, article_title)
    """
    filename = os.path.basename(file_path)
    
    # Extract content
    content = extract_pdf_content(file_path)
    
    # Determine primary system based on content
    primary_system = determine_primary_system(content, filename)
    
    # Extract article title
    article_title = extract_article_title(content)
    if not article_title:
        # Fallback to cleaning current filename
        article_title = re.sub(r'^[A-Z]+ - ', '', filename.replace('.pdf', ''))
        article_title = clean_title(article_title)
    
    return primary_system, article_title

def fix_content_based_naming(base_dir: str):
    """Fix all PDF names based on actual content analysis."""
    organized_dir = os.path.join(base_dir, "organized_by_system")
    
    if not os.path.exists(organized_dir):
        print(f"Error: {organized_dir} not found")
        return
    
    print(f"🔧 Fixing PDF names based on actual content...")
    print(f"📂 Processing: {organized_dir}")
    
    total_files = 0
    fixed_files = 0
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
                # Determine correct system and title
                primary_system, article_title = process_file(file_path)
                
                # Create correct filename
                correct_filename = f"{primary_system.upper()} - {article_title}.pdf"
                correct_filename = re.sub(r'[<>:"/\\|?*]', '_', correct_filename)
                correct_filename = correct_filename.replace('  ', ' ')
                
                # Determine correct folder
                correct_folder_path = os.path.join(organized_dir, primary_system)
                os.makedirs(correct_folder_path, exist_ok=True)
                
                # Check if file needs to be moved or renamed
                current_system = folder_name
                needs_move = current_system != primary_system
                needs_rename = filename != correct_filename
                
                if needs_move or needs_rename:
                    # Create target path
                    target_path = os.path.join(correct_folder_path, correct_filename)
                    
                    # Handle duplicates
                    counter = 1
                    base_name = correct_filename.replace('.pdf', '')
                    while os.path.exists(target_path):
                        new_filename = f"{base_name} ({counter}).pdf"
                        target_path = os.path.join(correct_folder_path, new_filename)
                        counter += 1
                    
                    # Move/rename file
                    shutil.move(file_path, target_path)
                    
                    if needs_move:
                        print(f"   📦 {filename}")
                        print(f"      {current_system} → {primary_system}")
                        moved_files += 1
                    else:
                        print(f"   ✏️  {filename}")
                        print(f"      → {os.path.basename(target_path)}")
                    
                    fixed_files += 1
                
            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")
    
    print(f"\n✅ Content-based naming fix complete!")
    print(f"   📄 Total files processed: {total_files}")
    print(f"   🔧 Files fixed: {fixed_files}")
    print(f"   📦 Files moved to correct folders: {moved_files}")
    
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
    
    fix_content_based_naming(base_dir)