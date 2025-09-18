import os
import re
import csv
import hashlib
from pathlib import Path
from typing import Optional, Dict

try:
    import pdfplumber  # type: ignore
except ImportError:  # graceful fallback later
    pdfplumber = None  # type: ignore

try:
    from PyPDF2 import PdfReader  # type: ignore
except ImportError:
    PdfReader = None  # type: ignore

SOURCE_DIR = Path("/Users/marius.cook/Downloads/PDF splitt 3")
BUILD_ROOT = Path("/Users/marius.cook/Desktop/scrape/clean_build_3")
OUTPUT_DIR = BUILD_ROOT / "alphabetical_all_pdfs"
SYSTEM_DIR = BUILD_ROOT / "organized_by_system"
MANIFEST_PATH = BUILD_ROOT / "manifest.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SYSTEM_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_KEYWORDS = {
    # keyword(lowercase) : Canonical System Name
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
    "teams": "Teams",
    "outlook": "Outlook",
    "sharepoint": "SharePoint",
    "onedrive": "OneDrive",
    "powerbi": "PowerBI",
    "sql": "SQL",
    "postgres": "Postgres",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
}

HEADER_MIN_LENGTH = 5

def file_hash(path: Path) -> str:
    h = hashlib.md5()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def extract_header(path: Path) -> Optional[str]:
    # pdfplumber first (better layout)
    if pdfplumber is not None:
        try:
            with pdfplumber.open(str(path)) as pdf:
                if pdf.pages:
                    text = pdf.pages[0].extract_text() or ""
                    for raw_line in text.splitlines():
                        line = clean_text(raw_line)
                        if len(line) >= HEADER_MIN_LENGTH and not re.match(r"^[\d\W_]+$", line):
                            return line
        except Exception:
            pass
    # PyPDF2 fallback
    if PdfReader is not None:
        try:
            reader = PdfReader(str(path))
            if reader.pages:
                text = reader.pages[0].extract_text() or ""
                for raw_line in text.splitlines():
                    line = clean_text(raw_line)
                    if len(line) >= HEADER_MIN_LENGTH and not re.match(r"^[\d\W_]+$", line):
                        return line
        except Exception:
            pass
    return None

def detect_system(header: Optional[str], blank_or_image: bool) -> str:
    if blank_or_image:
        return "Other_BlankOrImage"
    if not header:
        return "Other"
    lower = header.lower()
    for kw, system_name in SYSTEM_KEYWORDS.items():
        if kw in lower:
            return system_name
    # fallback: first word heuristic
    first = lower.split()[0]
    if first.isalpha() and len(first) > 1:
        return first.capitalize()
    return "Other"

def safe_filename(name: str) -> str:
    # Remove forbidden characters for macOS file systems
    name = name.replace('/', '-')
    name = re.sub(r'[\r\n\t]+', ' ', name)
    name = re.sub(r'[<>:"\\|?*]', '', name)
    name = clean_text(name)
    return name[:240]  # leave room for extension

def build():
    if not SOURCE_DIR.exists():
        print(f"Source dir missing: {SOURCE_DIR}")
        return
    all_pdfs = list(SOURCE_DIR.glob('*.pdf'))
    print(f"Discovered {len(all_pdfs)} PDFs in source.")

    # de-duplicate by content hash
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
    for idx, (h, pdf_path) in enumerate(hash_map.items(), 1):
        header = extract_header(pdf_path)
        blank_or_image = header is None
        system = detect_system(header, blank_or_image)
        header_text = header or "(No Header)"
        base_name = f"{system} - {header_text}".strip()
        base_name = safe_filename(base_name)
        final_name = base_name + '.pdf'
        # ensure uniqueness of filename
        counter = 2
        while final_name.lower() in seen_names:
            final_name = f"{base_name} ({counter}).pdf"
            counter += 1
        seen_names.add(final_name.lower())

        # copy into alphabetical directory (we just hardlink to save space if possible)
        dest_alpha = OUTPUT_DIR / final_name
        if dest_alpha.exists():
            # extremely unlikely due to uniqueness logic, but guard anyway
            final_name = f"{base_name} ({counter}).pdf"
            dest_alpha = OUTPUT_DIR / final_name
        try:
            os.link(pdf_path, dest_alpha)
        except OSError:
            # fallback copy
            data = pdf_path.read_bytes()
            dest_alpha.write_bytes(data)

        # system folder
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
            'blank_or_image_first_page': str(blank_or_image)
        })
        if idx % 100 == 0:
            print(f"Processed {idx}/{len(hash_map)} unique PDFs...")

    # write manifest
    with MANIFEST_PATH.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['original_path','content_hash','header','system','final_filename','blank_or_image_first_page'])
        writer.writeheader()
        writer.writerows(manifest_rows)

    print("Build complete.")
    print(f"Alphabetical dir: {len(list(OUTPUT_DIR.glob('*.pdf')))} files")
    print(f"System dirs total files: {len(list(SYSTEM_DIR.glob('**/*.pdf')))} (includes duplicates across system + alphabetical)")
    print(f"Manifest at: {MANIFEST_PATH}")

if __name__ == '__main__':
    build()
