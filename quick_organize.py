#!/usr/bin/env python3
"""
Quick PDF Organizer for PDF splitt folder
Pre-configured to work with your Downloads/PDF splitt directory
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append('/Users/marius.cook/Desktop/scrape')
from pdf_organizer import PDFOrganizer

def quick_organize():
    """Quick organization with predefined settings"""
    print("🔄 Quick PDF Organizer for PDF splitt folder")
    print("=" * 50)
    
    # Pre-configured settings
    pdf_dir = Path.home() / "Downloads" / "PDF splitt"
    similarity_threshold = 75  # Slightly lower for better grouping
    
    print(f"📁 Source directory: {pdf_dir}")
    print(f"🎯 Similarity threshold: {similarity_threshold}%")
    
    if not pdf_dir.exists():
        print(f"❌ Error: Directory '{pdf_dir}' does not exist!")
        return
    
    # Initialize organizer
    organizer = PDFOrganizer(str(pdf_dir), similarity_threshold)
    
    # Count PDFs first
    pdf_files = list(pdf_dir.glob("*.pdf")) + list(pdf_dir.glob("*.PDF"))
    print(f"📊 Found {len(pdf_files)} PDF files to process")
    
    if len(pdf_files) == 0:
        print("❌ No PDF files found!")
        return
    
    # Ask for confirmation before processing
    print(f"\n⚠️  This will process {len(pdf_files)} PDF files.")
    print("This may take several minutes depending on file sizes.")
    
    choice = input("\nChoose an option:\n1. Full analysis (recommended)\n2. Quick sample (first 50 files)\n3. Cancel\nEnter choice (1/2/3): ").strip()
    
    if choice == "3":
        print("❌ Operation cancelled.")
        return
    elif choice == "2":
        print("🔬 Processing sample of 50 files...")
        # Temporarily limit to first 50 files for quick test
        sample_files = pdf_files[:50]
        organizer.pdf_headers = {}
        
        for i, pdf_file in enumerate(sample_files, 1):
            print(f"  Processing {i}/50: {pdf_file.name}")
            header = organizer.extract_pdf_header(pdf_file)
            organizer.pdf_headers[pdf_file.name] = header
    else:
        print("🔄 Processing all files...")
        headers = organizer.scan_pdfs()
        if not headers:
            return
    
    # Group by headers
    print("\n🔍 Grouping PDFs by similar headers...")
    groups = organizer.group_by_headers()
    
    # Show preview
    print("\n" + organizer.generate_report())
    
    # Ask for final confirmation
    print(f"\n📋 Summary:")
    print(f"   • {len(organizer.pdf_headers)} files processed")
    print(f"   • {len(groups)} groups created")
    print(f"   • Files will be moved to: {pdf_dir}/organized_by_headers/")
    
    response = input("\n🚀 Proceed with organizing? (y/n/d for dry-run): ").strip().lower()
    
    if response == 'y':
        organizer.create_folders_and_organize(dry_run=False)
        print("\n✅ Organization complete!")
        print(f"📁 Check the results in: {pdf_dir}/organized_by_headers/")
    elif response == 'd':
        organizer.create_folders_and_organize(dry_run=True)
        print("\n👀 Dry run complete! No files were moved.")
    else:
        print("❌ Organization cancelled.")

if __name__ == "__main__":
    quick_organize()