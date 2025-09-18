#!/usr/bin/env python3
"""
System-based PDF Organizer
Organizes PDFs into folders by system/application name found in headers
Example: All PDFs with "OneDrive" in header go to "OneDrive" folder
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
import PyPDF2
import pdfplumber
import re

class SystemBasedPDFOrganizer:
    def __init__(self, source_directory: str):
        """Initialize System-based PDF Organizer"""
        self.source_directory = Path(source_directory)
        self.pdf_headers = {}  # filename -> header mapping
        self.system_groups = {}  # system -> list of files mapping
        
        # Define the systems/applications to look for
        self.target_systems = [
            "OneDrive", "Teams", "Outlook", "SharePoint", "Excel", "Word", "PowerPoint",
            "SMIA", "Elements", "KOSS", "DVH", "Puzzel", "Tidbank", "Intranett",
            "Jabra", "VDI", "Remedy", "Jira", "Unit4", "Phonero", "Sofie", "Sian",
            "Webex", "Adobe", "Planner", "Forms", "Mural", "Uniflow", "Bitlocker",
            "Microsoft", "Windows", "Apple", "Mac", "iPhone", "Android", "Mobil",
            "Altinn", "Skatteetaten", "Matomo", "Balsamiq", "Jabber", "OneNote",
            "Loop", "Copilot", "Authenticator", "Edge", "Chrome", "Firefox",
            "Cisco", "Calendly", "Aurora", "Ventus", "OBI", "Calabrio", "Mattermost",
            "Læringsportalen", "Audit", "Begrepskatalogen", "Lexaurus", "Teamkatalogen",
            "Argus", "ESS", "Remedy", "Autohotkey", "Pixview", "Databricks", "VPN", "MFA"
        ]
        
    def extract_pdf_header(self, pdf_path: Path, max_lines: int = 5) -> str:
        """Extract FULL first page content from PDF, not just header area"""
        content_text = ""
        
        try:
            # Try pdfplumber first - get FULL page content
            with pdfplumber.open(pdf_path) as pdf:
                if pdf.pages:
                    first_page = pdf.pages[0]
                    text = first_page.extract_text()
                    
                    if text:
                        content_text = text.strip()
                        
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    if pdf_reader.pages:
                        first_page = pdf_reader.pages[0]
                        text = first_page.extract_text()
                        
                        if text:
                            content_text = text.strip()
                            
            except Exception as e2:
                print(f"Failed to read {pdf_path.name}: {e2}")
                content_text = ""
        
        # Clean up the content text - remove support text
        content_text = self._clean_header_text(content_text)
        
        return content_text.strip()
    
    def _clean_header_text(self, text: str) -> str:
        """Clean content text by removing support boilerplate"""
        if not text:
            return ""
        
        # Remove common support text patterns
        patterns_to_remove = [
            r"Teksten under er for brukerstøtte.*?:",
            r"Brukerstøttes fremgangsmåte for å løse saken.*?:",
            r"Nøkkelord:.*?(?=\s[A-Z])",  # Remove keyword sections
            r"Har du en tilbakemelding.*?",
            r"Se også.*?:",
            r"NB[!:].*?(?=\s[A-Z])",
            r"^\d+\.\s*",  # Remove leading numbers
            r"side_\d+\.pdf",  # Remove filename references
            r"Sist oppdatert:\s*\d{2}\.\d{2}\.\d{4}",  # Remove date stamps
            r"Problem eller behov\s*",  # Remove section headers
            r"System/program/tjeneste\s*",  # Remove section headers
            r"Løsning/fremgangsmåte\s*",  # Remove section headers
            r"Trenger du fortsatt hjelp\?.*?",  # Remove help text
            r"Meld inn sak til oss.*?",  # Remove contact instructions
        ]
        
        cleaned_text = text
        for pattern in patterns_to_remove:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
    def detect_system_in_header(self, header: str) -> str:
        """
        Detect which system/application is mentioned in the header
        Returns the clean system name or 'Other' if no system is detected
        """
        if not header:
            return "Other"
        
        header_lower = header.lower()
        
        # Check for each target system (case insensitive) - return exact system name
        for system in self.target_systems:
            if system.lower() in header_lower:
                return system  # Return the exact system name from target_systems
        
        # Check for common variations - return clean names
        system_variations = {
            "one drive": "OneDrive",
            "onedrive": "OneDrive",
            "micro soft": "Microsoft",
            "microsoft": "Microsoft",
            "power point": "PowerPoint",
            "powerpoint": "PowerPoint", 
            "share point": "SharePoint",
            "sharepoint": "SharePoint",
            "out look": "Outlook",
            "outlook": "Outlook",
            "teams møte": "Teams",
            "teams-møte": "Teams",
            "teams": "Teams",
            "microsoft authenticator": "Authenticator",
            "authenticator": "Authenticator",
            "microsoft edge": "Edge",
            "edge": "Edge",
            "office 365": "Microsoft",
            "microsoft 365": "Microsoft",
            "m365": "Microsoft",
            "o365": "Microsoft",
            "excel": "Excel",
            "word": "Word",
            "smia": "SMIA",
            "elements": "Elements",
            "koss": "KOSS",
            "dvh": "DVH",
            "puzzel": "Puzzel",
            "tidbank": "Tidbank",
            "tid bank": "Tidbank",
            "intranett": "Intranett",
            "jira": "Jira",
            "remedy": "Remedy",
            "phonero": "Phonero",
            "sofie": "Sofie",
            "sian": "Sian",
            "cisco": "Cisco",
            "jabber": "Jabber",
            "cisco jabber": "Cisco",
            "calendly": "Calendly",
            "aurora": "Aurora",
            "ventus": "Ventus",
            "obi": "OBI",
            "calabrio": "Calabrio",
            "mattermost": "Mattermost",
            "læringsportalen": "Læringsportalen",
            "audit": "Audit",
            "begrepskatalogen": "Begrepskatalogen",
            "lexaurus": "Lexaurus",
            "teamkatalogen": "Teamkatalogen",
            "argus": "Argus",
            "ess": "ESS",
            "autohotkey": "Autohotkey",
            "pixview": "Pixview",
            "databricks": "Databricks",
            "skjermingsregisteret": "SharePoint",
            "firmaportal": "Skatteetaten",
            "informasjonsklassifisering": "Microsoft",
            "checkpoint": "VPN",
            "vpn": "VPN",
            "mfa": "MFA",
            "multi-factor authentication": "MFA",
            "multifactor authentication": "MFA",
            "multi factor authentication": "MFA",
            "two-factor authentication": "MFA",
            "2fa": "MFA",
            "totp": "MFA",
            "authenticator app": "MFA"
        }
        
        for variation, clean_system_name in system_variations.items():
            if variation in header_lower:
                return clean_system_name  # Return clean system name
        
        return "Other"
    
    def scan_pdfs_and_categorize(self) -> Dict[str, str]:
        """Scan all PDFs and categorize by system"""
        print(f"Scanning PDFs in: {self.source_directory}")
        
        pdf_files = list(self.source_directory.glob("*.pdf")) + list(self.source_directory.glob("*.PDF"))
        
        if not pdf_files:
            print("No PDF files found!")
            return {}
        
        print(f"Found {len(pdf_files)} PDF files to categorize")
        
        # Process files
        for i, pdf_file in enumerate(pdf_files, 1):
            if i % 100 == 0:
                print(f"Processing {i}/{len(pdf_files)}...")
            
            header = self.extract_pdf_header(pdf_file)
            system = self.detect_system_in_header(header)
            
            self.pdf_headers[pdf_file.name] = header
            
            # Group by system
            if system not in self.system_groups:
                self.system_groups[system] = []
            self.system_groups[system].append(pdf_file.name)
        
        return self.pdf_headers
    
    def show_categorization_preview(self) -> None:
        """Show preview of how files will be categorized"""
        print(f"\n📊 Categorization Preview:")
        print("=" * 50)
        
        # Sort systems by number of files (largest first)
        sorted_systems = sorted(self.system_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        for system, filenames in sorted_systems:
            print(f"📁 {system}: {len(filenames)} files")
            
            # Show a few example files and their headers
            if len(filenames) <= 3:
                for filename in filenames:
                    header = self.pdf_headers.get(filename, "")
                    print(f"   • {filename}")
                    print(f"     Header: {header[:80]}...")
            else:
                for filename in filenames[:2]:
                    header = self.pdf_headers.get(filename, "")
                    print(f"   • {filename}")
                    print(f"     Header: {header[:80]}...")
                print(f"   • ... and {len(filenames)-2} more files")
            print()
    
    def organize_files(self, dry_run: bool = False) -> None:
        """Organize files into system-based folders"""
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing PDFs by system...")
        
        organized_dir = self.source_directory / "organized_by_system"
        
        if not dry_run:
            organized_dir.mkdir(exist_ok=True)
        
        for system, filenames in self.system_groups.items():
            if len(filenames) == 0:
                continue
                
            folder_path = organized_dir / system
            
            print(f"\n{'Would create' if dry_run else 'Creating'} folder: {system}")
            print(f"  Moving {len(filenames)} files")
            
            if not dry_run:
                folder_path.mkdir(exist_ok=True)
                
                for filename in filenames:
                    source_file = self.source_directory / filename
                    dest_file = folder_path / filename
                    
                    if source_file.exists():
                        shutil.move(str(source_file), str(dest_file))
                    else:
                        print(f"    WARNING: {filename} not found!")
        
        if not dry_run:
            print(f"\n✅ Organization complete!")
            print(f"📁 Files organized in: {organized_dir}")
        else:
            print(f"\n👀 Dry run complete!")

def main():
    """Main function"""
    print("System-based PDF Organizer")
    print("=" * 40)
    print("Organizes PDFs by system/application name (OneDrive, Teams, Outlook, etc.)")
    
    # Default to PDF splitt folder
    downloads_dir = Path.home() / "Downloads"
    
    # Check if files are in organized_by_content folder
    content_organized_dir = downloads_dir / "PDF splitt" / "organized_by_content"
    original_dir = downloads_dir / "PDF splitt"
    
    if content_organized_dir.exists():
        print(f"\n📁 Found previously organized content in: {content_organized_dir}")
        choice = input("Reorganize from:\n1. Original PDF splitt folder\n2. Previously organized content folders\nChoose (1/2): ").strip()
        
        if choice == "2":
            source_dir = content_organized_dir
            print(f"📂 Using: {source_dir}")
            
            # We need to collect all PDFs from all subfolders
            print("Collecting PDFs from all content folders...")
            temp_dir = downloads_dir / "temp_collected_pdfs"
            temp_dir.mkdir(exist_ok=True)
            
            # Move all PDFs to temp directory first
            for subfolder in content_organized_dir.iterdir():
                if subfolder.is_dir():
                    for pdf_file in subfolder.glob("*.pdf"):
                        shutil.move(str(pdf_file), str(temp_dir / pdf_file.name))
            
            source_dir = temp_dir
        else:
            source_dir = original_dir
    else:
        source_dir = original_dir
    
    print(f"📁 Source directory: {source_dir}")
    
    if not source_dir.exists():
        print(f"❌ Error: Directory '{source_dir}' does not exist!")
        return
    
    # Initialize organizer
    organizer = SystemBasedPDFOrganizer(str(source_dir))
    
    # Scan and categorize
    print("\n🔍 Scanning PDFs and detecting systems...")
    headers = organizer.scan_pdfs_and_categorize()
    
    if not headers:
        return
    
    # Show preview
    organizer.show_categorization_preview()
    
    # Ask for confirmation
    response = input("\nProceed with system-based organization? (y/n/d for dry-run): ").strip().lower()
    
    if response == 'y':
        organizer.organize_files(dry_run=False)
    elif response == 'd':
        organizer.organize_files(dry_run=True)
    else:
        print("❌ Organization cancelled.")
    
    # Clean up temp directory if it was created
    temp_dir = downloads_dir / "temp_collected_pdfs"
    if temp_dir.exists() and choice == "2":
        try:
            shutil.rmtree(temp_dir)
        except:
            print(f"Note: Please manually remove temp directory: {temp_dir}")

if __name__ == "__main__":
    main()