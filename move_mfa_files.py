#!/usr/bin/env python3
"""
Move MFA-related files from Microsoft folder to dedicated MFA folder
"""

import sys
import shutil
from pathlib import Path
sys.path.append('/Users/marius.cook/Desktop/scrape')

from system_organizer import SystemBasedPDFOrganizer

def move_mfa_files():
    """Move MFA files from Microsoft folder to MFA folder"""
    
    # Paths
    organized_dir = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    microsoft_folder = organized_dir / "Microsoft"
    mfa_folder = organized_dir / "MFA"
    
    if not microsoft_folder.exists():
        print("❌ Microsoft folder not found!")
        return
    
    # Create MFA folder if it doesn't exist
    mfa_folder.mkdir(exist_ok=True)
    
    # Get all PDF files in Microsoft folder
    pdf_files = list(microsoft_folder.glob("*.pdf"))
    print(f"🔍 Found {len(pdf_files)} files in Microsoft folder to check for MFA content")
    
    if len(pdf_files) == 0:
        print("✅ No files to check!")
        return
    
    # Initialize organizer
    organizer = SystemBasedPDFOrganizer(str(microsoft_folder))
    
    # MFA keywords to look for in content
    mfa_keywords = [
        "mfa", "multi-factor authentication", "multifactor authentication", 
        "multi factor authentication", "two-factor authentication", "2fa", 
        "totp", "authenticator app", "authentication app", "verify identity",
        "verification code", "security code", "authentication method",
        "second factor", "additional verification", "sign-in verification"
    ]
    
    moved_count = 0
    checked_count = 0
    
    print("\n📊 Checking files for MFA content...")
    
    for pdf_file in pdf_files:
        checked_count += 1
        if checked_count % 10 == 0:
            print(f"   Progress: {checked_count}/{len(pdf_files)}")
        
        # Extract full page content
        content = organizer.extract_pdf_header(pdf_file)
        content_lower = content.lower()
        
        # Check if any MFA keywords are found
        mfa_found = False
        found_keywords = []
        
        for keyword in mfa_keywords:
            if keyword in content_lower:
                mfa_found = True
                found_keywords.append(keyword)
        
        if mfa_found:
            # Move file to MFA folder
            target_file = mfa_folder / pdf_file.name
            
            try:
                shutil.move(str(pdf_file), str(target_file))
                moved_count += 1
                print(f"   ✅ Moved {pdf_file.name} (found: {', '.join(found_keywords[:2])})")
                
            except Exception as e:
                print(f"   ❌ Error moving {pdf_file.name}: {e}")
    
    # Report results
    print(f"\n📈 MFA File Movement Results:")
    print("=" * 50)
    print(f"✅ Files moved to MFA folder: {moved_count}")
    print(f"📊 Files checked: {checked_count}")
    print(f"📁 MFA folder now has: {len(list(mfa_folder.glob('*.pdf')))} files")
    print(f"📁 Microsoft folder now has: {len(list(microsoft_folder.glob('*.pdf')))} files")
    
    if moved_count > 0:
        print(f"\n🎯 Success! {moved_count} MFA-related files moved to dedicated MFA folder")
    else:
        print(f"\n❌ No MFA files found in Microsoft folder")

if __name__ == "__main__":
    print("🔄 Moving MFA files from Microsoft folder to MFA folder")
    print("=" * 60)
    
    response = input("This will move MFA-related files from Microsoft to MFA folder. Continue? (y/n): ").strip().lower()
    
    if response == 'y':
        move_mfa_files()
        print(f"\n✅ MFA file movement complete!")
    else:
        print("❌ Movement cancelled.")