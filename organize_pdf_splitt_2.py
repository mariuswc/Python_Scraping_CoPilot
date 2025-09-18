#!/usr/bin/env python3
"""
System organizer for PDF splitt 2 folder
"""

import sys
sys.path.append('/Users/marius.cook/Desktop/scrape')

from system_organizer import SystemBasedPDFOrganizer
from pathlib import Path

def organize_pdf_splitt_2():
    """Organize PDFs from PDF splitt 2 folder into clean system folders"""
    downloads_dir = Path.home() / "Downloads"
    pdf_splitt_2_dir = downloads_dir / "PDF splitt 2"
    
    print("🔍 System-based PDF Organizer for PDF splitt 2")
    print("=" * 50)
    
    if not pdf_splitt_2_dir.exists():
        print(f"❌ Directory not found: {pdf_splitt_2_dir}")
        return
    
    # Check for PDFs
    pdf_files = list(pdf_splitt_2_dir.glob("*.pdf")) + list(pdf_splitt_2_dir.glob("*.PDF"))
    print(f"📁 Source: {pdf_splitt_2_dir}")
    print(f"📄 Found: {len(pdf_files)} PDF files")
    
    if len(pdf_files) == 0:
        print("❌ No PDF files found!")
        return
    
    # Initialize organizer
    organizer = SystemBasedPDFOrganizer(str(pdf_splitt_2_dir))
    
    # Scan and categorize
    print(f"\n🔍 Analyzing {len(pdf_files)} PDFs for system detection...")
    headers = organizer.scan_pdfs_and_categorize()
    
    if not headers:
        return
    
    # Show preview
    print(f"\n📊 System Detection Results:")
    print("=" * 40)
    
    sorted_systems = sorted(organizer.system_groups.items(), key=lambda x: len(x[1]), reverse=True)
    
    for system, filenames in sorted_systems:
        print(f"📁 {system}: {len(filenames)} files")
        
        # Show example files for top systems
        if len(filenames) <= 3:
            for filename in filenames:
                header = organizer.pdf_headers.get(filename, "")
                print(f"   • {filename}")
                print(f"     Header: {header[:60]}...")
        else:
            for filename in filenames[:2]:
                header = organizer.pdf_headers.get(filename, "")
                print(f"   • {filename}")
                print(f"     Header: {header[:60]}...")
            print(f"   • ... and {len(filenames)-2} more files")
        print()
    
    # Ask for confirmation
    print(f"🎯 This will create clean system folders like:")
    print(f"   📁 OneDrive → All OneDrive PDFs")
    print(f"   📁 Teams → All Teams PDFs")
    print(f"   📁 Outlook → All Outlook PDFs")
    print(f"   📁 etc.")
    
    response = input(f"\nProceed with organizing {len(pdf_files)} PDFs? (y/n/d for dry-run): ").strip().lower()
    
    if response == 'y':
        print("\n📁 Creating clean system-based organization...")
        organizer.organize_files(dry_run=False)
        
        # Show final results
        organized_dir = pdf_splitt_2_dir / "organized_by_system"
        if organized_dir.exists():
            system_folders = [f for f in organized_dir.iterdir() if f.is_dir()]
            system_folders.sort(key=lambda x: len(list(x.glob("*.pdf"))), reverse=True)
            
            print(f"\n🎉 SUCCESS! Clean system organization complete!")
            print(f"📁 Location: {organized_dir}")
            print(f"\n📊 Final Clean System Folders:")
            print("=" * 40)
            
            total_files = 0
            for folder in system_folders:
                pdf_files = list(folder.glob("*.pdf"))
                total_files += len(pdf_files)
                if len(pdf_files) > 0:
                    print(f"📁 {folder.name}: {len(pdf_files)} files")
            
            print(f"\n✅ Perfect! {len([f for f in system_folders if len(list(f.glob('*.pdf'))) > 0])} clean system folders created")
            print(f"📄 {total_files} PDFs organized by system name")
            print(f"\nExactly what you wanted:")
            print(f"   • Clean folder names (OneDrive, Teams, Outlook, etc.)")
            print(f"   • Each system has its own folder")
            print(f"   • All PDFs with that system in header → respective folder")
            
    elif response == 'd':
        print("\n👀 Running dry-run preview...")
        organizer.organize_files(dry_run=True)
    else:
        print("❌ Organization cancelled.")

if __name__ == "__main__":
    organize_pdf_splitt_2()