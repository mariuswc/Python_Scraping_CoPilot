#!/usr/bin/env python3
"""
Re-organize all files from 'Other' folder with improved system detection
This will move correctly detected files to their proper system folders
"""

import sys
import shutil
sys.path.append('/Users/marius.cook/Desktop/scrape')

from pathlib import Path
from system_organizer import SystemBasedPDFOrganizer

def reorganize_other_files():
    """Re-organize files from Other folder using improved detection"""
    
    # Paths
    organized_dir = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    other_folder = organized_dir / "Other"
    
    if not other_folder.exists():
        print("❌ Other folder not found!")
        return
    
    # Get all PDF files in Other folder
    pdf_files = list(other_folder.glob("*.pdf"))
    print(f"🔍 Found {len(pdf_files)} files in 'Other' folder to re-analyze")
    
    if len(pdf_files) == 0:
        print("✅ No files to reorganize!")
        return
    
    # Initialize organizer
    organizer = SystemBasedPDFOrganizer(str(other_folder))
    
    # Track what we find
    moved_files = {}  # system -> count
    still_other = 0
    
    print("\n📊 Re-analyzing files with improved detection...")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        if i % 200 == 0:
            print(f"   Progress: {i}/{len(pdf_files)}")
        
        # Extract full page content (improved method)
        content = organizer.extract_pdf_header(pdf_file)
        
        # Detect system (improved method)
        detected_system = organizer.detect_system_in_header(content)
        
        if detected_system != "Other":
            # Create target folder if it doesn't exist
            target_folder = organized_dir / detected_system
            target_folder.mkdir(exist_ok=True)
            
            # Move file to correct system folder
            target_file = target_folder / pdf_file.name
            
            try:
                shutil.move(str(pdf_file), str(target_file))
                
                # Track the move
                if detected_system not in moved_files:
                    moved_files[detected_system] = 0
                moved_files[detected_system] += 1
                
            except Exception as e:
                print(f"❌ Error moving {pdf_file.name}: {e}")
        else:
            still_other += 1
    
    # Report results
    print(f"\n📈 Re-organization Results:")
    print("=" * 50)
    
    total_moved = sum(moved_files.values())
    print(f"✅ Successfully moved: {total_moved} files")
    print(f"❌ Still in 'Other': {still_other} files")
    print(f"📊 Recovery rate: {total_moved/(total_moved + still_other)*100:.1f}%")
    
    if moved_files:
        print(f"\n📁 Files moved to system folders:")
        for system, count in sorted(moved_files.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {system}: +{count} files")
    
    print(f"\n🎯 Recommendation:")
    if total_moved > 0:
        print(f"   Great success! {total_moved} files recovered from 'Other'")
        if still_other > 0:
            print(f"   {still_other} files remain as 'Other' - these likely have no clear system names")
    else:
        print(f"   No files could be recovered. Manual review may be needed.")

if __name__ == "__main__":
    print("🔄 Re-organizing 'Other' files with improved system detection")
    print("=" * 60)
    
    response = input("This will move files from 'Other' to proper system folders. Continue? (y/n): ").strip().lower()
    
    if response == 'y':
        reorganize_other_files()
        print(f"\n✅ Re-organization complete!")
    else:
        print("❌ Re-organization cancelled.")