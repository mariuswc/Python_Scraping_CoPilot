#!/usr/bin/env python3
"""
Organize Sub-Applications within System Folders

This script creates sub-folders within each system folder to organize files
by their specific applications or features. For example:

Teams/
├── Calendar/
├── Chat/
├── Meetings/
├── Files/
└── General/

SharePoint/
├── Lists/
├── Libraries/
├── Permissions/
├── Sites/
└── General/
"""

import os
import shutil
from pathlib import Path
import re
from collections import defaultdict

def extract_topic_after_system(filename: str, system: str) -> str:
    """
    Extract the actual topic after the system name from filename.
    Examples:
    - "Altinn - Folkeregisterert.pdf" -> "Folkeregisterert"
    - "Teams - Calendar Meeting setup.pdf" -> "Calendar"
    - "SIAN - Tvang Utlegg procedure.pdf" -> "Tvang"
    
    Returns "MOVE_TO_OTHER_SYSTEM" if the topic is actually another system.
    """
    
    # List of systems that should NOT be sub-folders but separate systems
    independent_systems = {
        'MVA', 'DELINGSTJENESTER', 'FOLKEREGISTER', 'SKATTEKORT', 'SME', 'ESKATTEKORT',
        'SIAN', 'KOSS', 'ELEMENTS', 'SOFIE', 'ESS', 'SMIA', 'TIDBANK',
        'TEAMS', 'OUTLOOK', 'SHAREPOINT', 'ONEDRIVE', 'WORD', 'EXCEL', 'POWERPOINT',
        'JIRA', 'REMEDY', 'VPN', 'ADOBE', 'CHROME', 'EDGE', 'SAFARI',
        'CISCO', 'JABBER', 'JABRA', 'UNIFLOW', 'BITLOCKER', 'WINDOWS', 'MAC',
        'IPHONE', 'ANDROID', 'MOBIL', 'VDI', 'CITRIX', 'OMNISSA'
    }
    
    # Remove .pdf extension
    name_without_ext = filename
    if name_without_ext.lower().endswith('.pdf'):
        name_without_ext = name_without_ext[:-4]
    
    # Look for pattern: "System - Topic ..."
    # Try different variations of the system name
    system_variations = [
        system,
        system.upper(),
        system.lower(),
        system.title()
    ]
    
    for sys_var in system_variations:
        pattern = f"{sys_var} - "
        if pattern in name_without_ext:
            # Extract everything after "System - "
            after_dash = name_without_ext.split(pattern, 1)[1].strip()
            
            if after_dash:
                # Take the first word/concept as the sub-application
                # Split on common separators and take first meaningful part
                topic_parts = after_dash.split()
                if topic_parts:
                    first_topic = topic_parts[0]
                    
                    # Clean up the topic name
                    first_topic = first_topic.strip('.,;:!?()[]{}')
                    
                    if len(first_topic) > 2:  # Avoid single letters or very short words
                        # Check if this topic is actually an independent system
                        if first_topic.upper() in independent_systems:
                            return "MOVE_TO_OTHER_SYSTEM"
                        
                        return first_topic.title()
    
    return "General"

def determine_sub_application(filename: str, system: str) -> str:
    """
    Determine the sub-application/feature based on filename content after system name.
    For files like "Altinn - Folkeregisterert.pdf", extract "Folkeregisterert".
    """
    
    # First try to extract the actual topic after system name
    actual_topic = extract_topic_after_system(filename, system)
    if actual_topic and actual_topic != "General":
        return actual_topic
    
    # Fallback to keyword-based detection for files without clear structure
    content_upper = filename.upper()
    
    # System-specific sub-application mapping
    sub_app_mapping = {
        'TEAMS': {
            'CALENDAR': ['KALENDER', 'CALENDAR', 'MØTE', 'MEETING', 'APPOINTMENT'],
            'CHAT': ['CHAT', 'SAMTALE', 'MESSAGE', 'MELDING'],
            'CHANNELS': ['KANAL', 'CHANNEL'],
            'FILES': ['FIL', 'FILE', 'DOKUMENT', 'DOCUMENT'],
            'MEETINGS': ['MØTE', 'MEETING', 'CONFERENCE', 'VIDEO'],
            'BREAKOUT': ['BREAKOUT', 'GRUPPEROM'],
            'RECORDING': ['OPPTAK', 'RECORDING', 'TRANSKRIPSJON'],
            'NOTIFICATIONS': ['VARSEL', 'NOTIFICATION', 'VARSLING'],
            'SETTINGS': ['INNSTILLING', 'SETTING', 'CONFIG'],
        },
        
        'SHAREPOINT': {
            'LISTS': ['LIST', 'LISTE'],
            'LIBRARIES': ['LIBRARY', 'BIBLIOTEK', 'DOCUMENT LIBRARY'],
            'PERMISSIONS': ['TILGANG', 'PERMISSION', 'ACCESS', 'SECURITY'],
            'SITES': ['SITE', 'OMRÅDE', 'WORKSPACE'],
            'SYNC': ['SYNK', 'SYNC', 'SYNCHRON'],
            'VERSIONS': ['VERSJON', 'VERSION', 'BACKUP', 'RESTORE'],
            'WORKFLOWS': ['WORKFLOW', 'APPROVAL', 'GODKJENN'],
        },
        
        'OUTLOOK': {
            'CALENDAR': ['KALENDER', 'CALENDAR', 'MØTE', 'MEETING', 'APPOINTMENT'],
            'EMAIL': ['EPOST', 'EMAIL', 'MAIL', 'MESSAGE'],
            'CONTACTS': ['KONTAKT', 'CONTACT', 'ADDRESS'],
            'RULES': ['REGEL', 'RULE', 'FILTER'],
            'SHARED': ['DELT', 'SHARED', 'FELLESPOSTKASSE'],
            'ARCHIVE': ['ARKIV', 'ARCHIVE'],
            'SEARCH': ['SØK', 'SEARCH', 'FIND'],
            'SIGNATURES': ['SIGNATUR', 'SIGNATURE'],
        },
        
        'WORD': {
            'FORMATTING': ['FORMAT', 'STIL', 'STYLE', 'FONT'],
            'TEMPLATES': ['MAL', 'TEMPLATE'],
            'COLLABORATION': ['SAMARBEID', 'COLLABORAT', 'TRACK CHANGES', 'COMMENT'],
            'TABLES': ['TABELL', 'TABLE'],
            'IMAGES': ['BILDE', 'IMAGE', 'PICTURE'],
            'HEADERS': ['TOPPTEKST', 'HEADER', 'FOOTER', 'BUNNTEKST'],
            'PRINTING': ['PRINT', 'UTSKRIFT'],
        },
        
        'EXCEL': {
            'FORMULAS': ['FORMEL', 'FORMULA', 'FUNCTION'],
            'CHARTS': ['DIAGRAM', 'CHART', 'GRAPH'],
            'PIVOT': ['PIVOT', 'PIVOTTABELL'],
            'MACROS': ['MAKRO', 'MACRO', 'VBA'],
            'FORMATTING': ['FORMAT', 'CONDITIONAL'],
            'DATA': ['DATA', 'IMPORT', 'EXPORT'],
            'PROTECTION': ['PASSORD', 'PASSWORD', 'PROTECT'],
        },
        
        'SIAN': {
            'GJELD': ['GJELD', 'DEBT', 'GJELDSORDNING'],
            'TVANG': ['TVANG', 'UTLEGG', 'ENFORCEMENT'],
            'FORLIK': ['FORLIK', 'SETTLEMENT', 'MEDIATION'],
            'BREVPRODUKSJON': ['BREV', 'LETTER', 'DOCUMENT'],
            'TREKKMODUL': ['TREKK', 'DEDUCTION', 'PAYROLL'],
            'MASSEPRODUKSJON': ['MASSEPRODUKSJON', 'BATCH', 'BULK'],
            'RAPPORTER': ['RAPPORT', 'REPORT'],
        },
        
        'KOSS': {
            'KONTROLL': ['KONTROLL', 'CONTROL', 'AUDIT'],
            'VEDTAK': ['VEDTAK', 'DECISION', 'RULING'],
            'VARSEL': ['VARSEL', 'WARNING', 'NOTICE'],
            'RAPPORT': ['RAPPORT', 'REPORT'],
            'MVA': ['MVA', 'VAT'],
            'TILLEGGSSKATT': ['TILLEGGSSKATT', 'PENALTY'],
            'FØLGESAK': ['FØLGESAK', 'FOLLOW-UP'],
        },
        
        'SMIA': {
            'SKATTEMELDING': ['SKATTEMELDING', 'TAX RETURN'],
            'SKATTEOPPGJØR': ['SKATTEOPPGJØR', 'TAX SETTLEMENT'],
            'KONTROLL': ['KONTROLL', 'AUDIT'],
            'ENDRING': ['ENDRING', 'CHANGE', 'AMENDMENT'],
            'KLAGE': ['KLAGE', 'COMPLAINT', 'APPEAL'],
        },
        
        'TIDBANK': {
            'REGISTRERING': ['REGISTRER', 'REGISTER', 'TIME'],
            'FRAVÆR': ['FRAVÆR', 'ABSENCE', 'SICK'],
            'FERIE': ['FERIE', 'VACATION', 'HOLIDAY'],
            'OVERTID': ['OVERTID', 'OVERTIME'],
            'RAPPORTER': ['RAPPORT', 'REPORT'],
            'GODKJENNING': ['GODKJENN', 'APPROVAL'],
        },
        
        'VDI': {
            'CITRIX': ['CITRIX', 'WORKSPACE'],
            'OMNISSA': ['OMNISSA', 'HORIZON', 'VMWARE'],
            'UTSKRIFT': ['PRINT', 'UTSKRIFT', 'SIKKERPRINT'],
            'FILOVERFØRING': ['FIL', 'FILE', 'TRANSFER', 'OVERFØRING'],
            'TILGANG': ['TILGANG', 'ACCESS', 'LOGIN'],
        },
        
        'ONEDRIVE': {
            'SYNC': ['SYNK', 'SYNC', 'SYNCHRON'],
            'SHARING': ['DEL', 'SHARE', 'SHARING'],
            'BACKUP': ['BACKUP', 'RESTORE', 'GJENOPPRETT'],
            'STORAGE': ['LAGRING', 'STORAGE', 'SPACE'],
            'MOBILE': ['MOBIL', 'MOBILE', 'PHONE'],
        },
        
        'ELEMENTS': {
            'JOURNALPOST': ['JOURNAL', 'JOURNALPOST'],
            'ARKIVERING': ['ARKIV', 'ARCHIVE'],
            'SØKING': ['SØK', 'SEARCH'],
            'TILGANG': ['TILGANG', 'ACCESS', 'PERMISSIONS'],
            'GODKJENNING': ['GODKJENN', 'APPROVAL'],
        },
        
        'MOBIL': {
            'INSTALLASJON': ['INSTALL', 'INSTALLER', 'SETUP'],
            'UTLAND': ['UTLAND', 'ROAMING', 'ABROAD'],
            'REPARASJON': ['REPARER', 'REPAIR', 'FIX'],
            'ABONNEMENT': ['ABONNEMENT', 'SUBSCRIPTION', 'PLAN'],
            'SIKKERHET': ['SIKKERHET', 'SECURITY', 'LOCK'],
        },
    }
    
    # Get sub-applications for this system
    if system.upper() not in sub_app_mapping:
        return 'General'
    
    sub_apps = sub_app_mapping[system.upper()]
    
    # Score each sub-application
    scores = {}
    for sub_app, keywords in sub_apps.items():
        score = 0
        for keyword in keywords:
            if keyword in content_upper:
                score += len(keyword)  # Longer matches get higher scores
        
        if score > 0:
            scores[sub_app] = score
    
    # Return the highest scoring sub-application
    if scores:
        return max(scores.keys(), key=lambda k: scores[k])
    
    return 'General'

def organize_system_folder(system_folder: Path):
    """Organize files within a system folder into sub-application folders."""
    
    system_name = system_folder.name
    pdf_files = list(system_folder.glob("*.pdf"))
    
    if not pdf_files:
        return 0, 0
    
    print(f"\n📁 Organizing {system_name}/ ({len(pdf_files)} files)")
    
    # Group files by sub-application
    sub_app_groups = defaultdict(list)
    files_needing_system_move = []
    
    for pdf_file in pdf_files:
        sub_app = determine_sub_application(pdf_file.name, system_name)
        if sub_app == "MOVE_TO_OTHER_SYSTEM":
            files_needing_system_move.append(pdf_file)
        else:
            sub_app_groups[sub_app].append(pdf_file)
    
    # Warn about files that should be moved to other systems
    if files_needing_system_move:
        print(f"   ⚠️  Found {len(files_needing_system_move)} files that should be moved to other systems:")
        for file in files_needing_system_move[:3]:  # Show first 3 examples
            topic = extract_topic_after_system(file.name, system_name)
            print(f"      📄 {file.name[:60]}... (should be in separate system folder)")
        if len(files_needing_system_move) > 3:
            print(f"      📄 ... and {len(files_needing_system_move) - 3} more files")
        print(f"   💡 Run smart_recategorize.py to fix these system assignments")
    
    # Only create sub-folders if we have multiple categories OR clear extracted topics
    extracted_topics = []
    for pdf_file in pdf_files:
        topic = extract_topic_after_system(pdf_file.name, system_name)
        if topic != "General":
            extracted_topics.append(topic)
    
    has_extracted_topics = len(extracted_topics) > 0
    has_multiple_categories = len(sub_app_groups) > 1
    
    if not has_extracted_topics and (not has_multiple_categories or len(pdf_files) < 10):
        print(f"   ⏭️  Skipping (too few files or categories for sub-organization)")
        return 0, 0
    
    moved_files = 0
    created_folders = 0
    
    # Create sub-folders and move files
    for sub_app, files in sub_app_groups.items():
        # Create sub-folder for extracted topics (even single files) or groups with 3+ files
        should_create_folder = (
            len(files) >= 3 or  # Groups with 3+ files
            (len(files) >= 1 and sub_app != "General" and 
             any(extract_topic_after_system(f.name, system_name) == sub_app for f in files))  # Extracted topics
        )
        
        if should_create_folder:
            sub_folder = system_folder / sub_app
            sub_folder.mkdir(exist_ok=True)
            
            if not any(sub_folder.iterdir()):  # Only count as created if it's new
                created_folders += 1
            
            print(f"   📂 {sub_app}/ ({len(files)} files)")
            
            for file in files:
                try:
                    dest_path = sub_folder / file.name
                    
                    # Handle duplicates
                    counter = 1
                    original_dest = dest_path
                    while dest_path.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_path = sub_folder / f"{stem} ({counter}){suffix}"
                        counter += 1
                    
                    shutil.move(str(file), str(dest_path))
                    moved_files += 1
                    
                except Exception as e:
                    print(f"      ❌ Failed to move {file.name}: {e}")
        else:
            print(f"   📄 {sub_app}: {len(files)} files (keeping in main folder)")
    
    return moved_files, created_folders

def organize_all_sub_applications():
    """Organize sub-applications within all system folders."""
    
    organized_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    
    if not organized_path.exists():
        print(f"❌ Error: Organized folder not found at {organized_path}")
        return False
    
    print("📁 Organizing Sub-Applications within System Folders")
    print("=" * 60)
    
    total_moved = 0
    total_folders_created = 0
    processed_systems = 0
    
    # Process each system folder
    for system_folder in organized_path.iterdir():
        if not system_folder.is_dir():
            continue
        
        moved, created = organize_system_folder(system_folder)
        total_moved += moved
        total_folders_created += created
        
        if moved > 0:
            processed_systems += 1
    
    print(f"\n✅ Sub-application organization complete!")
    print(f"📊 Results:")
    print(f"   📂 Systems with sub-folders created: {processed_systems}")
    print(f"   📁 Total sub-folders created: {total_folders_created}")
    print(f"   📄 Total files moved: {total_moved}")
    
    if processed_systems > 0:
        print(f"\n🎯 Your system folders now have better internal organization!")
        print(f"💡 Large folders like Teams, Outlook, and SharePoint are now easier to navigate.")
    else:
        print(f"\n💡 No sub-organization needed - your folders are already well-sized!")
    
    return True

if __name__ == "__main__":
    print("📁 Sub-Application Organizer")
    print("=" * 50)
    print("This tool creates sub-folders within system folders")
    print("to organize files by specific features/applications.\n")
    
    success = organize_all_sub_applications()
    
    if success:
        print("\n🎯 Recommendation: Run create_alphabetical_copy.py again to update!")
    else:
        print("\n❌ Failed to organize sub-applications")