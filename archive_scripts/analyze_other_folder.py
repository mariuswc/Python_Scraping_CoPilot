#!/usr/bin/env python3
"""
Analyze what's in the "Other" folder to understand why system detection failed
"""

import sys
import random
sys.path.append('/Users/marius.cook/Desktop/scrape')

from pathlib import Path
from system_organizer import SystemBasedPDFOrganizer

# Check a sample of files from the Other folder
other_folder = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system/Other")
organizer = SystemBasedPDFOrganizer(str(other_folder))

# Get a random sample of files
pdf_files = list(other_folder.glob("*.pdf"))
print(f"Total files in Other folder: {len(pdf_files)}")

# Sample 10 random files
sample_files = random.sample(pdf_files, min(10, len(pdf_files)))

print("\n🔍 Analyzing sample files from 'Other' folder:")
print("=" * 80)

for i, pdf_file in enumerate(sample_files, 1):
    print(f"\n{i}. File: {pdf_file.name}")
    
    # Extract header
    header = organizer.extract_pdf_header(pdf_file, max_lines=10)
    print(f"   Raw Header: {header[:200]}...")
    
    # Clean header
    cleaned_header = organizer._clean_header_text(header)
    print(f"   Cleaned Header: {cleaned_header[:200]}...")
    
    # Try to detect system
    detected_system = organizer.detect_system_in_header(cleaned_header)
    print(f"   🎯 Detected System: {detected_system}")
    
    print("-" * 80)