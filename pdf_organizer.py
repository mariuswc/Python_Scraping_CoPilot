#!/usr/bin/env python3
"""
PDF Organizer by Headers
Automatically organizes PDF files into folders based on their header content.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import PyPDF2
import pdfplumber
from fuzzywuzzy import fuzz
import re

class PDFOrganizer:
    def __init__(self, source_directory: str, similarity_threshold: int = 80):
        """
        Initialize PDF Organizer
        
        Args:
            source_directory: Directory containing PDF files to organize
            similarity_threshold: Threshold for fuzzy matching (0-100, higher = more strict)
        """
        self.source_directory = Path(source_directory)
        self.similarity_threshold = similarity_threshold
        self.pdf_headers = {}  # Will store filename -> header mapping
        self.header_groups = {}  # Will store header -> list of files mapping
        
    def extract_pdf_header(self, pdf_path: Path, max_lines: int = 5) -> str:
        """
        Extract header text from PDF (first few lines or top section)
        
        Args:
            pdf_path: Path to PDF file
            max_lines: Maximum number of lines to consider as header
            
        Returns:
            Extracted header text (cleaned)
        """
        header_text = ""
        
        try:
            # Try with pdfplumber first (better text extraction)
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
        
        # Remove special characters that might cause folder name issues
        text = re.sub(r'[<>:"/\\|?*]', '_', text)
        
        # Limit length
        if len(text) > 100:
            text = text[:100] + "..."
            
        return text.strip()
    
    def find_similar_headers(self, new_header: str, existing_headers: List[str]) -> Optional[str]:
        """
        Find if new header is similar to any existing headers
        
        Args:
            new_header: Header to compare
            existing_headers: List of existing headers
            
        Returns:
            Most similar existing header if similarity > threshold, None otherwise
        """
        best_match = None
        best_score = 0
        
        for existing_header in existing_headers:
            # Try different fuzzy matching approaches
            scores = [
                fuzz.ratio(new_header.lower(), existing_header.lower()),
                fuzz.partial_ratio(new_header.lower(), existing_header.lower()),
                fuzz.token_sort_ratio(new_header.lower(), existing_header.lower()),
                fuzz.token_set_ratio(new_header.lower(), existing_header.lower())
            ]
            
            max_score = max(scores)
            
            if max_score > best_score and max_score >= self.similarity_threshold:
                best_score = max_score
                best_match = existing_header
                
        return best_match
    
    def scan_pdfs(self) -> Dict[str, str]:
        """
        Scan all PDFs in source directory and extract headers
        
        Returns:
            Dictionary mapping filename to header
        """
        print(f"Scanning PDFs in: {self.source_directory}")
        
        pdf_files = list(self.source_directory.glob("*.pdf")) + list(self.source_directory.glob("*.PDF"))
        
        if not pdf_files:
            print("No PDF files found in the directory!")
            return {}
            
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            header = self.extract_pdf_header(pdf_file)
            self.pdf_headers[pdf_file.name] = header
            print(f"  Header: {header}")
            
        return self.pdf_headers
    
    def group_by_headers(self) -> Dict[str, List[str]]:
        """
        Group PDF files by similar headers
        
        Returns:
            Dictionary mapping representative header to list of filenames
        """
        print("\nGrouping PDFs by similar headers...")
        
        for filename, header in self.pdf_headers.items():
            # Check if this header is similar to any existing group
            similar_header = self.find_similar_headers(header, list(self.header_groups.keys()))
            
            if similar_header:
                # Add to existing group
                self.header_groups[similar_header].append(filename)
                print(f"  Added '{filename}' to group '{similar_header[:50]}...'")
            else:
                # Create new group
                self.header_groups[header] = [filename]
                print(f"  Created new group '{header[:50]}...' with '{filename}'")
                
        return self.header_groups
    
    def create_folders_and_organize(self, dry_run: bool = False) -> None:
        """
        Create folders based on header groups and move PDFs
        
        Args:
            dry_run: If True, only show what would be done without actually moving files
        """
        print(f"\n{'DRY RUN: ' if dry_run else ''}Organizing PDFs into folders...")
        
        organized_dir = self.source_directory / "organized_by_headers"
        
        if not dry_run:
            organized_dir.mkdir(exist_ok=True)
        
        for header, filenames in self.header_groups.items():
            # Create safe folder name
            folder_name = self._clean_header_text(header)
            if len(folder_name) > 50:
                folder_name = folder_name[:50] + "..."
                
            folder_path = organized_dir / folder_name
            
            print(f"\n{'Would create' if dry_run else 'Creating'} folder: '{folder_name}'")
            print(f"  Files ({len(filenames)}): {', '.join(filenames)}")
            
            if not dry_run:
                folder_path.mkdir(exist_ok=True)
                
                for filename in filenames:
                    source_file = self.source_directory / filename
                    dest_file = folder_path / filename
                    
                    if source_file.exists():
                        shutil.move(str(source_file), str(dest_file))
                        print(f"    Moved: {filename}")
                    else:
                        print(f"    WARNING: {filename} not found!")
    
    def generate_report(self) -> str:
        """Generate a summary report of the organization"""
        report = []
        report.append("PDF Organization Report")
        report.append("=" * 50)
        report.append(f"Source Directory: {self.source_directory}")
        report.append(f"Total PDFs: {len(self.pdf_headers)}")
        report.append(f"Number of Groups: {len(self.header_groups)}")
        report.append(f"Similarity Threshold: {self.similarity_threshold}%")
        report.append("")
        
        for i, (header, filenames) in enumerate(self.header_groups.items(), 1):
            report.append(f"Group {i}: {header[:80]}...")
            report.append(f"  Files ({len(filenames)}): {', '.join(filenames)}")
            report.append("")
            
        return "\n".join(report)


def main():
    """Main function with user interaction"""
    print("PDF Organizer by Headers")
    print("=" * 40)
    
    # Default to the PDF splitt folder in Downloads
    downloads_dir = Path.home() / "Downloads"
    default_pdf_dir = downloads_dir / "PDF splitt"
    
    print(f"Default directory: {default_pdf_dir}")
    
    # Get source directory
    source_dir = input(f"Enter the directory path containing PDF files (or press Enter for '{default_pdf_dir}'): ").strip()
    if not source_dir:
        source_dir = str(default_pdf_dir)
        
    if not os.path.exists(source_dir):
        print(f"Error: Directory '{source_dir}' does not exist!")
        return
    
    # Get similarity threshold
    threshold_input = input("Enter similarity threshold (0-100, default 80): ").strip()
    try:
        threshold = int(threshold_input) if threshold_input else 80
        threshold = max(0, min(100, threshold))  # Clamp between 0-100
    except ValueError:
        threshold = 80
        print("Invalid threshold, using default (80)")
    
    # Initialize organizer
    organizer = PDFOrganizer(source_dir, threshold)
    
    # Scan PDFs
    headers = organizer.scan_pdfs()
    if not headers:
        return
    
    # Group by headers
    groups = organizer.group_by_headers()
    
    # Show preview
    print("\n" + organizer.generate_report())
    
    # Ask for confirmation
    response = input("\nProceed with organizing? (y/n/d for dry-run): ").strip().lower()
    
    if response == 'y':
        organizer.create_folders_and_organize(dry_run=False)
        print("\nOrganization complete!")
    elif response == 'd':
        organizer.create_folders_and_organize(dry_run=True)
        print("\nDry run complete!")
    else:
        print("Organization cancelled.")


if __name__ == "__main__":
    main()