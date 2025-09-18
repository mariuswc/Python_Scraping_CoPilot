#!/usr/bin/env python3
"""
Quick System Organizer - Complete the system-based organization
"""

import os
import sys
import shutil
from pathlib import Path

# Add path for imports
sys.path.append('/Users/marius.cook/Desktop/scrape')
from system_organizer import SystemBasedPDFOrganizer

def complete_system_organization():
    """Complete the system organization task"""
    downloads_dir = Path.home() / "Downloads"
    content_dir = downloads_dir / "PDF splitt" / "organized_by_content"
    temp_dir = downloads_dir / "temp_collected_pdfs"
    
    print("🔄 Step 1: Collecting all PDFs from content folders...")
    
    # Create temp directory and collect all PDFs
    temp_dir.mkdir(exist_ok=True)
    
    pdf_count = 0
    if content_dir.exists():
        for subfolder in content_dir.iterdir():
            if subfolder.is_dir():
                for pdf_file in subfolder.glob("*.pdf"):
                    dest_file = temp_dir / pdf_file.name
                    if not dest_file.exists():  # Avoid duplicates
                        shutil.copy2(str(pdf_file), str(dest_file))
                        pdf_count += 1
    
    print(f"✅ Collected {pdf_count} PDFs")
    
    if pdf_count == 0:
        print("❌ No PDFs found to organize")
        return
    
    # Run the system organization
    print("🔍 Step 2: Analyzing PDFs for system categorization...")
    organizer = SystemBasedPDFOrganizer(str(temp_dir))
    organizer.scan_pdfs_and_categorize()
    
    print("📁 Step 3: Creating system-based folders...")
    organizer.organize_files(dry_run=False)
    
    print("✅ System organization complete!")
    print(f"📁 Results available at: {temp_dir}/organized_by_system")
    
    # Show final results
    result_dir = temp_dir / "organized_by_system"
    if result_dir.exists():
        system_folders = [f for f in result_dir.iterdir() if f.is_dir()]
        system_folders.sort(key=lambda x: len(list(x.glob("*.pdf"))), reverse=True)
        
        print(f"\n📊 Final System Organization:")
        print("=" * 40)
        
        total_files = 0
        for folder in system_folders[:15]:  # Show top 15
            pdf_files = list(folder.glob("*.pdf"))
            total_files += len(pdf_files)
            print(f"📁 {folder.name}: {len(pdf_files)} files")
        
        if len(system_folders) > 15:
            remaining_files = sum(len(list(f.glob("*.pdf"))) for f in system_folders[15:])
            total_files += remaining_files
            print(f"   ... and {len(system_folders)-15} more folders with {remaining_files} files")
        
        print(f"\n📋 Summary:")
        print(f"   • {len(system_folders)} system folders created")
        print(f"   • {total_files} PDF files organized by system name")
        print(f"   • Perfect! Each system has its own clean folder")

if __name__ == "__main__":
    complete_system_organization()