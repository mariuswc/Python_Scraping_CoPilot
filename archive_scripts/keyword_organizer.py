#!/usr/bin/env python3
"""
Keyword-based PDF Organizer
Organizes PDFs into folders based on keywords found in their headers
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
import PyPDF2
import pdfplumber
import re

class KeywordPDFOrganizer:
    def __init__(self, source_directory: str):
        """
        Initialize Keyword-based PDF Organizer
        
        Args:
            source_directory: Directory containing PDF files to organize
        """
        self.source_directory = Path(source_directory)
        self.pdf_headers = {}  # Will store filename -> header mapping
        self.keyword_groups = {}  # Will store keyword -> list of files mapping
        self.keywords = set()  # Will store all discovered keywords
        
    def extract_pdf_header(self, pdf_path: Path, max_lines: int = 3) -> str:
        """Extract header text from PDF"""
        header_text = ""
        
        try:
            # Try with pdfplumber first
            with pdfplumber.open(pdf_path) as pdf:
                if pdf.pages:
                    first_page = pdf.pages[0]
                    
                    # Get text from top portion of the page
                    page_height = first_page.height
                    header_area = first_page.within_bbox((0, page_height * 0.8, first_page.width, page_height))
                    text = header_area.extract_text()
                    
                    if text:
                        lines = text.strip().split('\n')[:max_lines]
                        header_text = ' '.join(lines).strip()
                        
        except Exception as e:
            print(f"pdfplumber failed for {pdf_path.name}, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    if pdf_reader.pages:
                        first_page = pdf_reader.pages[0]
                        text = first_page.extract_text()
                        
                        if text:
                            lines = text.strip().split('\n')[:max_lines]
                            header_text = ' '.join(lines).strip()
                            
            except Exception as e2:
                print(f"PyPDF2 also failed for {pdf_path.name}: {e2}")
                header_text = f"FAILED_TO_READ_{pdf_path.stem}"
        
        # Clean up the header text
        header_text = self._clean_header_text(header_text)
        
        return header_text or f"EMPTY_HEADER_{pdf_path.stem}"
    
    def _clean_header_text(self, text: str) -> str:
        """Clean and normalize header text"""
        if not text:
            return ""
            
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_keywords_from_header(self, header: str) -> List[str]:
        """
        Extract meaningful keywords from header text
        
        Args:
            header: Header text to analyze
            
        Returns:
            List of keywords found in the header
        """
        # Convert to lowercase for analysis
        header_lower = header.lower()
        
        # Common words to ignore
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
            'her', 'its', 'our', 'their', 'from', 'up', 'about', 'into', 'over', 'after'
        }
        
        # Split into words and clean
        words = re.findall(r'\b[a-zA-Z]+\b', header_lower)
        
        # Filter out stop words and short words
        keywords = []
        for word in words:
            if len(word) >= 3 and word not in stop_words:
                keywords.append(word)
                
        return keywords
    
    def scan_pdfs_for_keywords(self) -> Dict[str, str]:
        """Scan all PDFs and extract headers and keywords"""
        print(f"Scanning PDFs in: {self.source_directory}")
        
        pdf_files = list(self.source_directory.glob("*.pdf")) + list(self.source_directory.glob("*.PDF"))
        
        if not pdf_files:
            print("No PDF files found in the directory!")
            return {}
            
        print(f"Found {len(pdf_files)} PDF files")
        
        # Process files
        for i, pdf_file in enumerate(pdf_files, 1):
            if i % 100 == 0:  # Progress indicator for large collections
                print(f"Processing file {i}/{len(pdf_files)}...")
            
            header = self.extract_pdf_header(pdf_file)
            self.pdf_headers[pdf_file.name] = header
            
            # Extract keywords from this header
            keywords = self.extract_keywords_from_header(header)
            self.keywords.update(keywords)
            
        print(f"Extraction complete! Found {len(self.keywords)} unique keywords.")
        return self.pdf_headers
    
    def group_by_keywords(self, selected_keywords: List[str] = None) -> Dict[str, List[str]]:
        """
        Group PDF files by keywords found in their headers
        
        Args:
            selected_keywords: List of specific keywords to use. If None, uses most common keywords.
        """
        if selected_keywords is None:
            # Show most common keywords and let user choose
            keyword_counts = {}
            for filename, header in self.pdf_headers.items():
                keywords = self.extract_keywords_from_header(header)
                for keyword in keywords:
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Sort by frequency
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
            
            print(f"\nMost common keywords found:")
            for i, (keyword, count) in enumerate(sorted_keywords[:20], 1):
                print(f"{i:2d}. '{keyword}' ({count} files)")
            
            return keyword_counts
        
        # Group files by selected keywords
        self.keyword_groups = {}
        unmatched_files = []
        
        for filename, header in self.pdf_headers.items():
            header_lower = header.lower()
            matched = False
            
            for keyword in selected_keywords:
                if keyword.lower() in header_lower:
                    if keyword not in self.keyword_groups:
                        self.keyword_groups[keyword] = []
                    self.keyword_groups[keyword].append(filename)
                    matched = True
                    break  # Only assign to first matching keyword
            
            if not matched:
                unmatched_files.append(filename)
        
        # Add unmatched files to a separate group
        if unmatched_files:
            self.keyword_groups['_unmatched'] = unmatched_files
            
        return self.keyword_groups
    
    def create_folders_and_organize(self, dry_run: bool = False) -> None:
        """Create folders based on keywords and move PDFs"""
        print(f"\n{'DRY RUN: ' if dry_run else ''}Organizing PDFs into keyword-based folders...")
        
        organized_dir = self.source_directory / "organized_by_keywords"
        
        if not dry_run:
            organized_dir.mkdir(exist_ok=True)
        
        for keyword, filenames in self.keyword_groups.items():
            # Create safe folder name
            folder_name = keyword.replace('/', '_').replace('\\', '_')
            if keyword == '_unmatched':
                folder_name = 'unmatched_files'
                
            folder_path = organized_dir / folder_name
            
            print(f"\n{'Would create' if dry_run else 'Creating'} folder: '{folder_name}'")
            print(f"  Files ({len(filenames)}): {len(filenames)} files")
            if len(filenames) <= 10:
                print(f"    {', '.join(filenames)}")
            else:
                print(f"    {', '.join(filenames[:5])} ... and {len(filenames)-5} more")
            
            if not dry_run:
                folder_path.mkdir(exist_ok=True)
                
                for filename in filenames:
                    source_file = self.source_directory / filename
                    dest_file = folder_path / filename
                    
                    if source_file.exists():
                        shutil.move(str(source_file), str(dest_file))
                    else:
                        print(f"    WARNING: {filename} not found!")

def main():
    """Main function for keyword-based organization"""
    print("PDF Keyword Organizer")
    print("=" * 40)
    
    # Default to the PDF splitt folder in Downloads
    downloads_dir = Path.home() / "Downloads"
    default_pdf_dir = downloads_dir / "PDF splitt"
    
    print(f"Default directory: {default_pdf_dir}")
    
    # Get source directory
    source_dir = input(f"Enter directory path (or press Enter for '{default_pdf_dir}'): ").strip()
    if not source_dir:
        source_dir = str(default_pdf_dir)
        
    if not os.path.exists(source_dir):
        print(f"Error: Directory '{source_dir}' does not exist!")
        return
    
    # Initialize organizer
    organizer = KeywordPDFOrganizer(source_dir)
    
    # Scan PDFs and extract keywords
    headers = organizer.scan_pdfs_for_keywords()
    if not headers:
        return
    
    # Show keyword frequency analysis
    keyword_counts = organizer.group_by_keywords()
    
    # Let user select keywords
    print(f"\nEnter keywords you want to use for organizing (comma-separated):")
    print("Example: teams, invoice, report, contract")
    keyword_input = input("Keywords: ").strip()
    
    if not keyword_input:
        print("No keywords specified. Using top 10 most common keywords...")
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        selected_keywords = [kw for kw, count in sorted_keywords[:10]]
    else:
        selected_keywords = [kw.strip() for kw in keyword_input.split(',')]
    
    print(f"\nUsing keywords: {', '.join(selected_keywords)}")
    
    # Group files by selected keywords
    groups = organizer.group_by_keywords(selected_keywords)
    
    # Show preview
    print(f"\nGrouping Results:")
    print(f"Total files: {len(headers)}")
    for keyword, files in groups.items():
        print(f"  '{keyword}': {len(files)} files")
    
    # Ask for confirmation
    response = input("\nProceed with organizing? (y/n/d for dry-run): ").strip().lower()
    
    if response == 'y':
        organizer.create_folders_and_organize(dry_run=False)
        print(f"\n✅ Organization complete!")
        print(f"📁 Check results in: {Path(source_dir)/'organized_by_keywords'}")
    elif response == 'd':
        organizer.create_folders_and_organize(dry_run=True)
        print("\n👀 Dry run complete!")
    else:
        print("❌ Organization cancelled.")

if __name__ == "__main__":
    main()