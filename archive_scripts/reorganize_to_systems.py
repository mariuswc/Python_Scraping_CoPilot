#!/usr/bin/env python3
"""
Reorganize PDFs from organized_by_content into clean system folders
"""

import os
import sys
import shutil
from pathlib import Path

# Add path for imports
sys.path.append('/Users/marius.cook/Desktop/scrape')
from system_organizer import SystemBasedPDFOrganizer

def reorganize_from_content():
    """Reorganize PDFs from content folders into clean system folders"""
    downloads_dir = Path.home() / "Downloads"
    content_dir = downloads_dir / "PDF splitt" / "organized_by_content"
    temp_dir = downloads_dir / "temp_for_system_org"
    
    print("🔄 Step 1: Collecting PDFs from organized_by_content folders...")
    
    # Create temp directory and collect all PDFs
    temp_dir.mkdir(exist_ok=True)
    
    pdf_count = 0
    if content_dir.exists():
        print(f"📁 Source: {content_dir}")
        
        # Collect all PDFs from all subfolders
        for subfolder in content_dir.iterdir():
            if subfolder.is_dir():
                pdf_files = list(subfolder.glob("*.pdf"))
                for pdf_file in pdf_files:
                    dest_file = temp_dir / pdf_file.name
                    if not dest_file.exists():  # Avoid duplicates
                        shutil.copy2(str(pdf_file), str(dest_file))
                        pdf_count += 1
                        
                if pdf_files:
                    print(f"   📂 {subfolder.name}: {len(pdf_files)} PDFs collected")
    
    print(f"✅ Collected {pdf_count} PDFs total")
    
    if pdf_count == 0:
        print("❌ No PDFs found to reorganize")
        return
    
    print(f"\n🔍 Step 2: Analyzing {pdf_count} PDFs for system categorization...")
    organizer = SystemBasedPDFOrganizer(str(temp_dir))
    organizer.scan_pdfs_and_categorize()
    
    print("\n📊 System Detection Results:")
    print("=" * 40)
    
    # Show preview
    sorted_systems = sorted(organizer.system_groups.items(), key=lambda x: len(x[1]), reverse=True)
    
    for system, filenames in sorted_systems[:15]:  # Show top 15
        print(f"📁 {system}: {len(filenames)} files")
    
    if len(sorted_systems) > 15:
        remaining_systems = len(sorted_systems) - 15
        remaining_files = sum(len(files) for _, files in sorted_systems[15:])
        print(f"   ... and {remaining_systems} more systems with {remaining_files} files")
    
    print(f"\n📁 Step 3: Creating clean system-based folders...")
    organizer.organize_files(dry_run=False)
    
    # Move the organized result to the main PDF splitt directory
    final_system_dir = downloads_dir / "PDF splitt" / "organized_by_system"
    temp_system_dir = temp_dir / "organized_by_system"
    
    if temp_system_dir.exists():
        if final_system_dir.exists():
            shutil.rmtree(final_system_dir)
        shutil.move(str(temp_system_dir), str(final_system_dir))
        print(f"📁 Moved to final location: {final_system_dir}")
    
    # Clean up temp directory
    try:
        shutil.rmtree(temp_dir)
        print("🗑️ Cleaned up temporary directory")
    except:
        print(f"Note: Please manually remove temp directory: {temp_dir}")
    
    print(f"\n🎉 SUCCESS! Clean system organization complete!")
    print(f"📁 Location: {final_system_dir}")
    
    # Show final results
    if final_system_dir.exists():
        system_folders = [f for f in final_system_dir.iterdir() if f.is_dir()]
        system_folders.sort(key=lambda x: len(list(x.glob("*.pdf"))), reverse=True)
        
        print(f"\n📊 Final Clean System Folders:")
        print("=" * 40)
        
        total_files = 0
        for folder in system_folders:
            pdf_files = list(folder.glob("*.pdf"))
            total_files += len(pdf_files)
            if len(pdf_files) > 0:
                print(f"📁 {folder.name}: {len(pdf_files)} files")
        
        print(f"\n✅ Perfect! {len([f for f in system_folders if len(list(f.glob('*.pdf'))) > 0])} clean system folders")
        print(f"📄 {total_files} PDFs organized by system name")
        print(f"\nYour PDFs are now organized exactly as requested:")
        print(f"   • OneDrive folder → All OneDrive PDFs")
        print(f"   • Teams folder → All Teams PDFs")
        print(f"   • Outlook folder → All Outlook PDFs")
        print(f"   • etc.")

if __name__ == "__main__":
    reorganize_from_content()