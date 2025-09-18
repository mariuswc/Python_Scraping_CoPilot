#!/usr/bin/env python3
"""
Remove duplicate files from the alphabetical folder based on:
1. Exact filename matches
2. Similar content (same PDF header)
"""

import os
import hashlib
import PyPDF2
import pdfplumber
import re
from collections import defaultdict

def get_file_hash(file_path):
    """Get MD5 hash of file content."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def extract_pdf_header(pdf_path):
    """Extract the header from a PDF file."""
    try:
        # Try pdfplumber first
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                text = pdf.pages[0].extract_text()
                if text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    for line in lines[:15]:
                        if len(line) > 5 and not line.isdigit() and not re.match(r'^[\d\.\s]+$', line):
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
                        return line
    except:
        pass
    
    return None

def normalize_filename(filename):
    """Normalize filename for comparison (remove numbers, extensions, etc.)."""
    # Remove .pdf extension
    name = filename.lower()
    if name.endswith('.pdf'):
        name = name[:-4]
    
    # Remove duplicate indicators like (1), (2), etc.
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def remove_duplicates_from_alphabetical(base_path):
    """Remove duplicate files from alphabetical folder."""
    alphabetical_folder = os.path.join(base_path, "alphabetical_all_pdfs")
    
    if not os.path.exists(alphabetical_folder):
        print("❌ Alphabetical folder not found!")
        return
    
    print("🔍 Analyzing duplicates in alphabetical folder...")
    
    files = [f for f in os.listdir(alphabetical_folder) if f.endswith('.pdf')]
    print(f"📄 Found {len(files)} PDF files to analyze")
    
    # Group files by various criteria
    files_by_hash = defaultdict(list)
    files_by_header = defaultdict(list)
    files_by_normalized_name = defaultdict(list)
    
    processed = 0
    for filename in files:
        file_path = os.path.join(alphabetical_folder, filename)
        processed += 1
        
        if processed % 100 == 0:
            print(f"   Processed {processed}/{len(files)} files...")
        
        # Group by file hash (exact duplicates)
        file_hash = get_file_hash(file_path)
        if file_hash:
            files_by_hash[file_hash].append((filename, file_path))
        
        # Group by PDF header (same content, different names)
        header = extract_pdf_header(file_path)
        if header:
            files_by_header[header].append((filename, file_path))
        
        # Group by normalized filename
        normalized = normalize_filename(filename)
        files_by_normalized_name[normalized].append((filename, file_path))
    
    print(f"\n📊 Duplicate analysis:")
    
    # Find exact duplicates (same file hash)
    exact_duplicates = {h: files for h, files in files_by_hash.items() if len(files) > 1}
    print(f"   Exact duplicates (same content): {len(exact_duplicates)} groups")
    
    # Find content duplicates (same header)
    content_duplicates = {h: files for h, files in files_by_header.items() if len(files) > 1}
    print(f"   Content duplicates (same header): {len(content_duplicates)} groups")
    
    # Find name duplicates
    name_duplicates = {n: files for n, files in files_by_normalized_name.items() if len(files) > 1}
    print(f"   Name duplicates (similar names): {len(name_duplicates)} groups")
    
    files_to_remove = set()
    
    # Remove exact duplicates (keep the first one)
    for file_hash, duplicate_files in exact_duplicates.items():
        # Keep the first file, mark others for removal
        for filename, file_path in duplicate_files[1:]:
            files_to_remove.add(file_path)
            print(f"🗑️  Exact duplicate: {filename}")
    
    # Remove content duplicates that aren't already marked
    for header, duplicate_files in content_duplicates.items():
        # Sort by filename to have consistent behavior
        duplicate_files.sort()
        # Keep the first file, mark others for removal (if not already marked)
        for filename, file_path in duplicate_files[1:]:
            if file_path not in files_to_remove:
                files_to_remove.add(file_path)
                print(f"🔄 Content duplicate: {filename}")
    
    print(f"\n📋 Summary:")
    print(f"   Total files: {len(files)}")
    print(f"   Files to remove: {len(files_to_remove)}")
    print(f"   Files remaining: {len(files) - len(files_to_remove)}")
    
    if files_to_remove:
        print(f"\nRemoving {len(files_to_remove)} duplicate files...")
        removed_count = 0
        for file_path in files_to_remove:
            try:
                os.remove(file_path)
                removed_count += 1
            except Exception as e:
                filename = os.path.basename(file_path)
                print(f"❌ Error removing {filename}: {e}")
        
        print(f"✅ Removed {removed_count} duplicate files!")
        print(f"📄 Alphabetical folder now has {len(files) - removed_count} unique files")
    else:
        print("✅ No duplicates found!")

def show_duplicate_examples(base_path, limit=10):
    """Show examples of duplicates found."""
    alphabetical_folder = os.path.join(base_path, "alphabetical_all_pdfs")
    
    if not os.path.exists(alphabetical_folder):
        return
    
    files = [f for f in os.listdir(alphabetical_folder) if f.endswith('.pdf')]
    files_by_normalized_name = defaultdict(list)
    
    for filename in files:
        normalized = normalize_filename(filename)
        files_by_normalized_name[normalized].append(filename)
    
    name_duplicates = {n: files for n, files in files_by_normalized_name.items() if len(files) > 1}
    
    print(f"\n📋 Examples of duplicate groups (showing first {limit}):")
    for i, (normalized, duplicate_files) in enumerate(list(name_duplicates.items())[:limit]):
        print(f"\n{i+1}. Group '{normalized}':")
        for filename in sorted(duplicate_files):
            print(f"   - {filename}")

def main():
    """Main execution function."""
    base_path = input("Enter the base path (e.g., /Users/marius.cook/Downloads/PDF splitt 2): ").strip()
    
    if not os.path.exists(base_path):
        print("❌ Path does not exist!")
        return
    
    # Show examples first
    show_duplicate_examples(base_path, 5)
    
    # Remove duplicates
    remove_duplicates_from_alphabetical(base_path)

if __name__ == "__main__":
    main()