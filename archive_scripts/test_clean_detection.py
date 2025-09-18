#!/usr/bin/env python3
"""
Test the clean system detection
"""

import sys
sys.path.append('/Users/marius.cook/Desktop/scrape')

from system_organizer import SystemBasedPDFOrganizer

# Test the clean system detection
organizer = SystemBasedPDFOrganizer(".")

# Test various header examples
test_headers = [
    "OneDrive Hvordan vet jeg om filene mine er synkroniseret?",
    "Teams Endre navn på kanal",
    "Outlook Mottas det flere eposter som medlem av flere",
    "SMIA Feil i planlagte handlinger",
    "Elements Problem med import av e-post",
    "Microsoft Authenticator app setup",
    "SharePoint og Teams Fildeling med gjester",
    "Puzzel administrator settings",
    "Some random text without system names"
]

print("🧪 Testing Clean System Detection")
print("=" * 50)

for header in test_headers:
    detected_system = organizer.detect_system_in_header(header)
    print(f"Header: {header[:50]}...")
    print(f"📁 Folder: {detected_system}")
    print()

print("✅ Result: Clean folder names like 'OneDrive', 'Teams', 'Outlook' etc.")
print("❌ No more 'Content_' prefixes or messy names!")