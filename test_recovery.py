#!/usr/bin/env python3
"""
Test the improved system detection (full page content + better cleaning)
"""

import sys
sys.path.append('/Users/marius.cook/Desktop/scrape')

from pathlib import Path
from system_organizer import SystemBasedPDFOrganizer

# Test on the files that were previously "Other"
other_folder = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system/Other")
organizer = SystemBasedPDFOrganizer(str(other_folder))

# Test specific files we analyzed earlier
test_files = [
    "side_487.pdf",    # Had KOSS in content
    "side_1566.pdf",   # Had SME (maybe no direct system match)
    "side_1510.pdf",   # Had SharePoint
    "side_1094.pdf",   # Had Windows
    "side_1421.pdf",   # Had SIAN
    "side_1388.pdf",   # Had SIAN and ESS
    "side_1871.pdf",   # Had Teams, SharePoint, Aurora
    "side_1963.pdf",   # Had tidBANK
    "side_1800.pdf",   # Had SOFIE
    "side_995.pdf",    # Had Outlook
]

print("🔬 Testing Improved Full-Page System Detection")
print("=" * 70)

recovery_count = 0
total_tested = 0

for filename in test_files:
    pdf_path = other_folder / filename
    if not pdf_path.exists():
        continue
    
    total_tested += 1
    print(f"\n📄 {filename}")
    
    # Extract full page content (new method)
    content = organizer.extract_pdf_header(pdf_path)
    
    # Detect system (improved method)
    detected_system = organizer.detect_system_in_header(content)
    
    # Show first part of cleaned content
    preview = content.replace('\n', ' ')[:100]
    print(f"   Content: {preview}...")
    print(f"   🎯 Detected: {detected_system}")
    
    if detected_system != "Other":
        recovery_count += 1
        print(f"   ✅ RECOVERED! (was 'Other', now '{detected_system}')")
    else:
        print(f"   ❌ Still 'Other'")

print(f"\n📊 Results:")
print(f"   Files tested: {total_tested}")
print(f"   Successfully recovered: {recovery_count}")
print(f"   Recovery rate: {recovery_count/total_tested*100:.1f}%")

if recovery_count > 0:
    print(f"\n🎉 SUCCESS! The improved detection can recover many 'Other' files!")
    print("   Ready to re-run organization with full page content scanning.")
else:
    print(f"\n❌ No improvement detected. Need to investigate further.")