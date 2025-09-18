#!/usr/bin/env python3
"""
Enhanced analysis - check deeper into PDF content, not just headers
"""

import sys
import random
sys.path.append('/Users/marius.cook/Desktop/scrape')

from pathlib import Path
import PyPDF2
import pdfplumber
import re

def extract_full_first_page(pdf_path):
    """Extract the full first page content, not just header"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if pdf.pages:
                first_page = pdf.pages[0]
                return first_page.extract_text() or ""
    except:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if pdf_reader.pages:
                    return pdf_reader.pages[0].extract_text() or ""
        except:
            pass
    return ""

def find_system_keywords_anywhere(text, target_systems):
    """Find any system keywords anywhere in the text"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_systems = []
    
    for system in target_systems:
        if system.lower() in text_lower:
            found_systems.append(system)
    
    return found_systems

# Systems to look for
target_systems = [
    "OneDrive", "Teams", "Outlook", "SharePoint", "Excel", "Word", "PowerPoint",
    "SMIA", "Elements", "KOSS", "DVH", "Puzzel", "Tidbank", "Intranett",
    "Jabra", "VDI", "Remedy", "Jira", "Unit4", "Phonero", "Sofie", "Sian",
    "Webex", "Adobe", "Planner", "Forms", "Mural", "Uniflow", "Bitlocker",
    "Microsoft", "Windows", "Apple", "Mac", "iPhone", "Android", "Mobil",
    "Altinn", "Skatteetaten", "Matomo", "Balsamiq", "Jabber", "OneNote",
    "Loop", "Copilot", "Authenticator", "Edge", "Chrome", "Firefox",
    "Cisco", "Calendly", "Aurora", "Ventus", "OBI", "Calabrio", "Mattermost",
    "Læringsportalen", "Audit", "Begrepskatalogen", "Lexaurus", "Teamkatalogen",
    "Argus", "ESS", "Autohotkey", "Pixview", "Databricks"
]

# Check sample files from Other folder
other_folder = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system/Other")
pdf_files = list(other_folder.glob("*.pdf"))

print(f"🔍 Deep Analysis of {len(pdf_files)} files in 'Other' folder")
print("=" * 80)

# Sample more files to get better picture
sample_files = random.sample(pdf_files, min(20, len(pdf_files)))

recoverable_count = 0
system_found_in_content = {}

for i, pdf_file in enumerate(sample_files, 1):
    print(f"\n{i}. File: {pdf_file.name}")
    
    # Get full first page content
    full_content = extract_full_first_page(pdf_file)
    
    if len(full_content.strip()) < 10:
        print("   ❌ Very little content found")
        continue
    
    # Show first part of content
    preview = full_content.replace('\n', ' ')[:150]
    print(f"   Content: {preview}...")
    
    # Look for system keywords anywhere in the content
    found_systems = find_system_keywords_anywhere(full_content, target_systems)
    
    if found_systems:
        recoverable_count += 1
        print(f"   🎯 Found systems: {', '.join(found_systems)}")
        
        for system in found_systems:
            if system not in system_found_in_content:
                system_found_in_content[system] = 0
            system_found_in_content[system] += 1
    else:
        print("   ❌ No system keywords found")

print(f"\n📊 Summary:")
print(f"   Analyzed: {len(sample_files)} files")
print(f"   Recoverable: {recoverable_count} files ({recoverable_count/len(sample_files)*100:.1f}%)")
print(f"   Systems found in content: {system_found_in_content}")

if recoverable_count > 0:
    print(f"\n💡 Solution: Need to scan FULL PAGE content, not just headers!")
    print("   Many PDFs have system names deeper in the content.")