#!/usr/bin/env python3
"""
Deep PDF Content Analyzer
Analyzes the actual content inside PDFs to find meaningful headers and text patterns
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
import PyPDF2
import pdfplumber
import re
from collections import Counter

class DeepPDFAnalyzer:
    def __init__(self, source_directory: str):
        """Initialize Deep PDF Analyzer"""
        self.source_directory = Path(source_directory)
        self.pdf_content = {}  # filename -> full content mapping
        self.pdf_headers = {}  # filename -> detected header mapping
        
    def extract_full_pdf_content(self, pdf_path: Path) -> str:
        """Extract all text content from PDF for analysis"""
        full_text = ""
        
        try:
            # Try pdfplumber first (better text extraction)
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    if page_num >= 3:  # Only analyze first 3 pages for performance
                        break
                    
                    text = page.extract_text()
                    if text:
                        full_text += f"\n--- PAGE {page_num + 1} ---\n" + text
                        
        except Exception as e:
            print(f"pdfplumber failed for {pdf_path.name}, trying PyPDF2: {e}")
            
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages):
                        if page_num >= 3:  # Only analyze first 3 pages
                            break
                        
                        text = page.extract_text()
                        if text:
                            full_text += f"\n--- PAGE {page_num + 1} ---\n" + text
                            
            except Exception as e2:
                print(f"Both PDF readers failed for {pdf_path.name}: {e2}")
                return f"FAILED_TO_READ_{pdf_path.stem}"
        
        return full_text.strip()
    
    def detect_header_patterns(self, content: str, filename: str) -> str:
        """
        Analyze PDF content to detect likely headers using multiple strategies
        """
        if not content or content.startswith("FAILED_TO_READ"):
            return content
        
        lines = content.split('\n')
        
        # Strategy 1: Look for title-like patterns (ALL CAPS, centered, etc.)
        title_candidates = []
        
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            line = line.strip()
            if not line or line.startswith('---'):
                continue
                
            # Check for title patterns
            if len(line) > 5 and len(line) < 100:
                # ALL CAPS titles
                if line.isupper() and len(line.split()) > 1:
                    title_candidates.append((line, 10, f"ALL_CAPS_TITLE_LINE_{i}"))
                
                # Lines with important keywords
                important_keywords = ['report', 'analysis', 'summary', 'document', 'memo', 'letter', 
                                    'invoice', 'contract', 'agreement', 'policy', 'procedure',
                                    'manual', 'guide', 'handbook', 'specification', 'plan',
                                    'proposal', 'presentation', 'meeting', 'minutes', 'agenda',
                                    'teams', 'microsoft', 'outlook', 'email', 'message']
                
                line_lower = line.lower()
                for keyword in important_keywords:
                    if keyword in line_lower:
                        title_candidates.append((line, 8, f"KEYWORD_{keyword.upper()}_LINE_{i}"))
                
                # Lines that look like titles (Title Case, reasonable length)
                if line.istitle() and 3 <= len(line.split()) <= 10:
                    title_candidates.append((line, 6, f"TITLE_CASE_LINE_{i}"))
        
        # Strategy 2: Look for email headers, document metadata
        metadata_patterns = [
            (r'From:\s*(.+)', 'EMAIL_FROM'),
            (r'To:\s*(.+)', 'EMAIL_TO'),
            (r'Subject:\s*(.+)', 'EMAIL_SUBJECT'),
            (r'Date:\s*(.+)', 'EMAIL_DATE'),
            (r'Title:\s*(.+)', 'DOC_TITLE'),
            (r'Author:\s*(.+)', 'DOC_AUTHOR'),
            (r'Document:\s*(.+)', 'DOC_NAME'),
        ]
        
        for line in lines[:30]:  # Check first 30 lines for metadata
            for pattern, category in metadata_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if len(value) > 3:
                        title_candidates.append((value, 9, f"{category}"))
        
        # Strategy 3: Look for repeated patterns that might indicate document type
        word_freq = Counter()
        for line in lines[:50]:  # Analyze first 50 lines
            words = re.findall(r'\b[A-Za-z]{3,}\b', line.lower())
            word_freq.update(words)
        
        # Find most common meaningful words
        common_words = word_freq.most_common(10)
        significant_words = []
        for word, count in common_words:
            if count >= 2 and word not in ['the', 'and', 'for', 'are', 'this', 'that', 'with', 'from']:
                significant_words.append(word)
        
        if significant_words:
            title_candidates.append((f"Content: {', '.join(significant_words[:5])}", 4, "CONTENT_KEYWORDS"))
        
        # Strategy 4: Extract first meaningful sentence
        sentences = re.split(r'[.!?]+', content)
        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if 10 < len(sentence) < 200 and not sentence.isdigit():
                title_candidates.append((sentence, 3, "FIRST_SENTENCE"))
                break
        
        # Select best candidate
        if title_candidates:
            # Sort by score (higher is better)
            title_candidates.sort(key=lambda x: x[1], reverse=True)
            best_title = title_candidates[0][0]
            
            # Clean up the title
            best_title = re.sub(r'\s+', ' ', best_title).strip()
            if len(best_title) > 100:
                best_title = best_title[:100] + "..."
                
            return best_title
        
        # Fallback: use filename pattern or first few words
        return f"Content from {filename}"
    
    def analyze_sample_pdfs(self, sample_size: int = 50) -> Dict[str, str]:
        """Analyze a sample of PDFs to understand content patterns"""
        print(f"Analyzing {sample_size} sample PDFs for content patterns...")
        
        pdf_files = list(self.source_directory.glob("*.pdf")) + list(self.source_directory.glob("*.PDF"))
        
        if not pdf_files:
            print("No PDF files found!")
            return {}
        
        # Take a sample
        import random
        sample_files = random.sample(pdf_files, min(sample_size, len(pdf_files)))
        
        sample_analysis = {}
        
        for i, pdf_file in enumerate(sample_files, 1):
            print(f"  Analyzing {i}/{len(sample_files)}: {pdf_file.name}")
            
            content = self.extract_full_pdf_content(pdf_file)
            header = self.detect_header_patterns(content, pdf_file.name)
            
            sample_analysis[pdf_file.name] = header
            
            # Show progress
            if len(content) > 100:
                preview = content[:200] + "..."
            else:
                preview = content
                
            print(f"    Content preview: {preview}")
            print(f"    Detected header: {header}")
            print()
        
        return sample_analysis
    
    def scan_all_pdfs(self) -> Dict[str, str]:
        """Scan all PDFs and extract meaningful headers"""
        print(f"Scanning all PDFs in: {self.source_directory}")
        
        pdf_files = list(self.source_directory.glob("*.pdf")) + list(self.source_directory.glob("*.PDF"))
        
        if not pdf_files:
            print("No PDF files found!")
            return {}
        
        print(f"Found {len(pdf_files)} PDF files to analyze")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            if i % 100 == 0:
                print(f"Processing {i}/{len(pdf_files)}...")
            
            content = self.extract_full_pdf_content(pdf_file)
            header = self.detect_header_patterns(content, pdf_file.name)
            self.pdf_headers[pdf_file.name] = header
        
        return self.pdf_headers
    
    def group_by_detected_headers(self) -> Dict[str, List[str]]:
        """Group PDFs by their detected headers using fuzzy matching"""
        from fuzzywuzzy import fuzz
        
        header_groups = {}
        
        for filename, header in self.pdf_headers.items():
            # Find similar existing headers
            best_match = None
            best_score = 0
            
            for existing_header in header_groups.keys():
                score = fuzz.token_set_ratio(header.lower(), existing_header.lower())
                if score > best_score and score >= 70:  # 70% similarity threshold
                    best_score = score
                    best_match = existing_header
            
            if best_match:
                header_groups[best_match].append(filename)
            else:
                header_groups[header] = [filename]
        
        return header_groups
    
    def generate_report(self, groups: Dict[str, List[str]]) -> str:
        """Generate analysis report"""
        report = []
        report.append("Deep PDF Content Analysis Report")
        report.append("=" * 50)
        report.append(f"Source Directory: {self.source_directory}")
        report.append(f"Total PDFs Analyzed: {len(self.pdf_headers)}")
        report.append(f"Number of Groups: {len(groups)}")
        report.append("")
        
        # Sort groups by size
        sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        for i, (header, filenames) in enumerate(sorted_groups[:20], 1):  # Show top 20 groups
            report.append(f"Group {i}: {header[:80]}...")
            report.append(f"  Files ({len(filenames)}): {len(filenames)} files")
            if len(filenames) <= 5:
                report.append(f"    {', '.join(filenames)}")
            else:
                report.append(f"    {', '.join(filenames[:3])} ... and {len(filenames)-3} more")
            report.append("")
        
        return "\n".join(report)

def main():
    """Main function"""
    print("Deep PDF Content Analyzer")
    print("=" * 40)
    
    # Default to PDF splitt folder
    downloads_dir = Path.home() / "Downloads"
    default_pdf_dir = downloads_dir / "PDF splitt"
    
    print(f"Default directory: {default_pdf_dir}")
    
    # Initialize analyzer
    analyzer = DeepPDFAnalyzer(str(default_pdf_dir))
    
    # First, analyze a sample to show what we can find
    print("\n🔍 Step 1: Analyzing sample PDFs to understand content...")
    sample_analysis = analyzer.analyze_sample_pdfs(10)  # Start with 10 files
    
    if sample_analysis:
        print(f"\n📊 Sample Results:")
        for filename, header in sample_analysis.items():
            print(f"  {filename} -> {header}")
    
    # Ask if user wants to continue with full analysis
    response = input(f"\nContinue with full analysis of all {len(list(default_pdf_dir.glob('*.pdf')))} PDFs? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n🔄 Step 2: Analyzing all PDFs...")
        all_headers = analyzer.scan_all_pdfs()
        
        print("\n🗂️ Step 3: Grouping by content similarity...")
        groups = analyzer.group_by_detected_headers()
        
        print("\n" + analyzer.generate_report(groups))
        
        # Ask about organizing
        organize_response = input("\nOrganize files into folders based on detected content? (y/n/d for dry-run): ").strip().lower()
        
        if organize_response in ['y', 'd']:
            dry_run = organize_response == 'd'
            
            organized_dir = default_pdf_dir / "organized_by_content"
            if not dry_run:
                organized_dir.mkdir(exist_ok=True)
            
            for header, filenames in groups.items():
                # Create safe folder name
                folder_name = re.sub(r'[<>:"/\\|?*]', '_', header)
                if len(folder_name) > 50:
                    folder_name = folder_name[:50] + "..."
                
                folder_path = organized_dir / folder_name
                
                print(f"\n{'[DRY RUN] ' if dry_run else ''}Creating folder: {folder_name}")
                print(f"  Moving {len(filenames)} files")
                
                if not dry_run:
                    folder_path.mkdir(exist_ok=True)
                    for filename in filenames:
                        source_file = default_pdf_dir / filename
                        dest_file = folder_path / filename
                        if source_file.exists():
                            shutil.move(str(source_file), str(dest_file))
            
            if not dry_run:
                print(f"\n✅ Organization complete! Check: {organized_dir}")
            else:
                print(f"\n👀 Dry run complete!")
    else:
        print("Analysis cancelled.")

if __name__ == "__main__":
    main()