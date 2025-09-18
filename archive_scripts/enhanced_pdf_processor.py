import os
import re
import csv
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Tuple

try:
    import pdfplumber  # type: ignore
except ImportError:
    pdfplumber = None  # type: ignore

try:
    from PyPDF2 import PdfReader  # type: ignore
except ImportError:
    PdfReader = None  # type: ignore

SOURCE_DIR = Path("/Users/marius.cook/Downloads/PDF splitt 3")
BUILD_ROOT = Path("/Users/marius.cook/Desktop/scrape/enhanced_build")
OUTPUT_DIR = BUILD_ROOT / "alphabetical_all_pdfs"
SYSTEM_DIR = BUILD_ROOT / "organized_by_system"
MANIFEST_PATH = BUILD_ROOT / "manifest.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SYSTEM_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_KEYWORDS = {
    # keyword(lowercase) : Canonical System Name
    "mfa": "MFA",
    "teams": "Teams", 
    "microsoft teams": "Teams",
    "aurora": "Aurora",
    "vis": "VIS",
    "smia": "SMIA",
    "koss": "KOSS",
    "citrix": "Citrix",
    "altinn": "Altinn",
    "delingstjenester": "Delingstjenester",
    "tilgangsportalen": "Tilgangsportalen",
    "valutaregister": "Valutaregister",
    "pc": "PC",
    "mac": "Mac",
    "oracle": "Oracle",
    "sap": "SAP",
    "jira": "Jira",
    "confluence": "Confluence",
    "outlook": "Outlook",
    "sharepoint": "SharePoint",
    "onedrive": "OneDrive",
    "powerbi": "PowerBI",
    "sql": "SQL",
    "postgres": "Postgres",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "azure": "Azure",
    "office 365": "Office365",
    "o365": "Office365",
    "exchange": "Exchange",
    "active directory": "ActiveDirectory",
    "ad": "ActiveDirectory",
    "windows": "Windows",
}

HEADER_MIN_LENGTH = 3

def file_hash(path: Path) -> str:
    h = hashlib.md5()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def extract_text_comprehensive(path: Path) -> Tuple[Optional[str], List[str]]:
    """Extract text from PDF with comprehensive approach.
    Returns: (best_header, all_text_lines)
    """
    all_lines = []
    best_header = None
    
    # Try pdfplumber first (better for formatted text and bold detection)
    if pdfplumber is not None:
        try:
            with pdfplumber.open(str(path)) as pdf:
                # Check first 3 pages for text
                for page_num in range(min(3, len(pdf.pages))):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    if text:
                        lines = [clean_text(line) for line in text.splitlines() if clean_text(line)]
                        all_lines.extend(lines)
                        
                        # Try to detect bold text using character objects
                        try:
                            chars = page.chars
                            bold_texts = []
                            for char in chars:
                                if char.get('fontname', '').lower().find('bold') != -1:
                                    bold_texts.append(char.get('text', ''))
                            
                            if bold_texts:
                                bold_line = clean_text(''.join(bold_texts))
                                if len(bold_line) >= HEADER_MIN_LENGTH and not best_header:
                                    best_header = bold_line
                        except:
                            pass
                        
                        # If no bold detected, use first substantial line
                        if not best_header:
                            for line in lines:
                                if len(line) >= HEADER_MIN_LENGTH and not re.match(r"^[\d\W_]+$", line):
                                    best_header = line
                                    break
                        
                        # Stop after finding text on first page with content
                        if lines:
                            break
        except Exception as e:
            print(f"pdfplumber error for {path}: {e}")
    
    # Fallback to PyPDF2 if pdfplumber failed
    if not all_lines and PdfReader is not None:
        try:
            reader = PdfReader(str(path))
            # Check first 3 pages
            for page_num in range(min(3, len(reader.pages))):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text:
                    lines = [clean_text(line) for line in text.splitlines() if clean_text(line)]
                    all_lines.extend(lines)
                    
                    if not best_header:
                        for line in lines:
                            if len(line) >= HEADER_MIN_LENGTH and not re.match(r"^[\d\W_]+$", line):
                                best_header = line
                                break
                    
                    if lines:
                        break
        except Exception as e:
            print(f"PyPDF2 error for {path}: {e}")
    
    return best_header, all_lines

def detect_system(header: Optional[str], all_text: List[str]) -> str:
    """Detect system from header and full text content."""
    if not header and not all_text:
        return "Other_BlankOrImage"
    
    # Combine header and first few lines for system detection
    search_text = ""
    if header:
        search_text += header + " "
    search_text += " ".join(all_text[:10])  # First 10 lines
    search_text = search_text.lower()
    
    # Check for system keywords
    for kw, system_name in SYSTEM_KEYWORDS.items():
        if kw in search_text:
            return system_name
    
    # Fallback: first word heuristic from header
    if header:
        first_word = header.lower().split()[0]
        if first_word.isalpha() and len(first_word) > 1:
            return first_word.capitalize()
    
    return "Other"

def safe_filename(name: str) -> str:
    """Clean filename for filesystem compatibility."""
    name = name.replace('/', '-')
    name = re.sub(r'[\r\n\t]+', ' ', name)
    name = re.sub(r'[<>:"\\|?*]', '', name)
    name = clean_text(name)
    return name[:240]  # leave room for extension

def test_sample_pdfs(count: int = 5):
    """Test extraction on a few sample PDFs."""
    if not SOURCE_DIR.exists():
        print(f"Source dir missing: {SOURCE_DIR}")
        return
    
    all_pdfs = list(SOURCE_DIR.glob('*.pdf'))[:count]
    print(f"Testing text extraction on {len(all_pdfs)} sample PDFs:\n")
    
    for pdf_path in all_pdfs:
        print(f"File: {pdf_path.name}")
        header, all_lines = extract_text_comprehensive(pdf_path)
        system = detect_system(header, all_lines)
        
        print(f"  Header: {header or '(No Header)'}")
        print(f"  System: {system}")
        print(f"  Total lines extracted: {len(all_lines)}")
        if all_lines:
            print(f"  First few lines: {all_lines[:3]}")
        print("-" * 50)

def build():
    """Main processing function."""
    if not SOURCE_DIR.exists():
        print(f"Source dir missing: {SOURCE_DIR}")
        return
    
    all_pdfs = list(SOURCE_DIR.glob('*.pdf'))
    print(f"Discovered {len(all_pdfs)} PDFs in source.")

    # De-duplicate by content hash
    hash_map: Dict[str, Path] = {}
    duplicates = 0
    for p in all_pdfs:
        h = file_hash(p)
        if h not in hash_map:
            hash_map[h] = p
        else:
            duplicates += 1
    print(f"Unique by hash: {len(hash_map)} (removed {duplicates} duplicate file instances)")

    manifest_rows = []
    seen_names = set()
    system_counts = {}
    
    for idx, (h, pdf_path) in enumerate(hash_map.items(), 1):
        header, all_lines = extract_text_comprehensive(pdf_path)
        system = detect_system(header, all_lines)
        system_counts[system] = system_counts.get(system, 0) + 1
        
        header_text = header or "(No Header)"
        blank_or_image = header is None and not all_lines
        
        # Create filename: System - Header
        base_name = f"{system} - {header_text}".strip()
        base_name = safe_filename(base_name)
        final_name = base_name + '.pdf'
        
        # Ensure uniqueness
        counter = 2
        while final_name.lower() in seen_names:
            final_name = f"{base_name} ({counter}).pdf"
            counter += 1
        seen_names.add(final_name.lower())

        # Copy to alphabetical directory
        dest_alpha = OUTPUT_DIR / final_name
        try:
            os.link(pdf_path, dest_alpha)
        except OSError:
            dest_alpha.write_bytes(pdf_path.read_bytes())

        # Copy to system folder
        sys_folder = SYSTEM_DIR / system
        sys_folder.mkdir(parents=True, exist_ok=True)
        dest_sys = sys_folder / final_name
        if not dest_sys.exists():
            try:
                os.link(pdf_path, dest_sys)
            except OSError:
                dest_sys.write_bytes(pdf_path.read_bytes())

        manifest_rows.append({
            'original_path': str(pdf_path),
            'content_hash': h,
            'header': header_text,
            'system': system,
            'final_filename': final_name,
            'blank_or_image_first_page': str(blank_or_image),
            'total_text_lines': len(all_lines)
        })
        
        if idx % 100 == 0:
            print(f"Processed {idx}/{len(hash_map)} unique PDFs...")

    # Write manifest
    with MANIFEST_PATH.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'original_path', 'content_hash', 'header', 'system', 
            'final_filename', 'blank_or_image_first_page', 'total_text_lines'
        ])
        writer.writeheader()
        writer.writerows(manifest_rows)

    print("\nBuild complete!")
    print(f"Alphabetical dir: {len(list(OUTPUT_DIR.glob('*.pdf')))} files")
    print(f"Manifest at: {MANIFEST_PATH}")
    print("\nSystem distribution:")
    for system, count in sorted(system_counts.items()):
        print(f"  {system}: {count} files")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_sample_pdfs()
    else:
        build()