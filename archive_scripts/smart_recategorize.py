#!/usr/bin/env python3
"""
Smart Recategorization Tool

This script analyzes the actual content/topic of each PDF file and moves it
to the correct system folder based on the MAIN topic, not just keyword presence.

For example:
- "Teams - SharePoint Endre visningsnavn" → SharePoint folder (it's about SharePoint)
- "Altinn - MVA tilgang testmiljø" → Altinn folder (it's about Altinn's MVA service)
- "Intranett - JIRA Service Desk" → Jira folder (it's about JIRA, accessed via intranet)
"""

import os
import shutil
from pathlib import Path
import re
from collections import defaultdict

def determine_primary_system(content: str) -> tuple:
    """
    Determine the primary system based on content analysis.
    Returns (primary_system, confidence_score)
    """
    
    content_upper = content.upper()
    
    # System detection with weighted scoring
    # Higher weight = more likely to be the primary topic
    system_weights = {
        # Microsoft Office Suite
        'TEAMS': {'keywords': ['TEAMS', 'TEAM ', 'TEAMSMØTE', 'KANAL', 'CHAT'], 'weight': 3},
        'SHAREPOINT': {'keywords': ['SHAREPOINT', 'SHAREPOINT-', 'SHAREPOINTOMRÅDE', 'DOKUMENTBIBLIOTEK'], 'weight': 3},
        'OUTLOOK': {'keywords': ['OUTLOOK', 'E-POST', 'EPOST', 'KALENDER', 'MØTE', 'INNBOKS'], 'weight': 3},
        'WORD': {'keywords': ['WORD', 'DOKUMENT', 'TEKSTBEHANDLING'], 'weight': 3},
        'EXCEL': {'keywords': ['EXCEL', 'REGNEARK', 'SPREADSHEET'], 'weight': 3},
        'POWERPOINT': {'keywords': ['POWERPOINT', 'PRESENTASJON'], 'weight': 3},
        'ONEDRIVE': {'keywords': ['ONEDRIVE', 'SKYDRIVE'], 'weight': 3},
        'ONENOTE': {'keywords': ['ONENOTE', 'NOTATBLOKK'], 'weight': 3},
        
        # Norwegian Government Systems
        'SIAN': {'keywords': ['SIAN', 'NAMSMYNDIGHETENE'], 'weight': 4},
        'SMIA': {'keywords': ['SMIA', 'SKATTEETATEN'], 'weight': 4},
        'KOSS': {'keywords': ['KOSS', 'KONTROLL'], 'weight': 4},
        'Elements': {'keywords': ['ELEMENTS', 'JOURNALPOST', 'ARKIVERING'], 'weight': 4},
        'Sofie': {'keywords': ['SOFIE', 'INNKREVING'], 'weight': 4},
        'ESS': {'keywords': ['ESS', 'ESS-PORTAL', 'SELVBETJENING', 'REISEREGNING'], 'weight': 4},
        'Tidbank': {'keywords': ['TIDBANK', 'TIDBANK', 'TIMEREGISTRERING', 'FRAVÆR'], 'weight': 4},
        
        # IT Tools
        'Jira': {'keywords': ['JIRA', 'ATLASSIAN', 'TICKET', 'SERVICE DESK'], 'weight': 3},
        'VDI': {'keywords': ['VDI', 'VMWARE', 'OMNISSA', 'HORIZON', 'CITRIX'], 'weight': 3},
        'Adobe': {'keywords': ['ADOBE', 'ACROBAT', 'PDF'], 'weight': 2},
        'Chrome': {'keywords': ['CHROME', 'GOOGLE CHROME'], 'weight': 2},
        'Edge': {'keywords': ['EDGE', 'MICROSOFT EDGE'], 'weight': 2},
        
        # Communication
        'Mobil': {'keywords': ['MOBIL', 'TELEFON', 'MOBILTELEFON'], 'weight': 3},
        'iPhone': {'keywords': ['IPHONE', 'IOS'], 'weight': 3},
        'Android': {'keywords': ['ANDROID', 'SAMSUNG'], 'weight': 3},
        
        # Other systems
        'MFA': {'keywords': ['MFA', 'MULTIFAKTOR', 'TOFAKTOR', 'AUTHENTICATOR'], 'weight': 4},
        'VPN': {'keywords': ['VPN', 'CHECK POINT'], 'weight': 3},
        'Windows': {'keywords': ['WINDOWS', 'PC ', 'DATAMASKIN'], 'weight': 2},
        'Mac': {'keywords': ['MAC', 'MACOS', 'APPLE'], 'weight': 2},
        
        # External services
        'Altinn': {'keywords': ['ALTINN'], 'weight': 3},
        'DVH': {'keywords': ['DVH', 'DATAVERKTØY'], 'weight': 3},
        
        # Low priority (often just context)
        'Intranett': {'keywords': ['INTRANETT', 'INTRANET'], 'weight': 1},  # Often just access method
        'Microsoft': {'keywords': ['MICROSOFT'], 'weight': 1},  # Too generic
    }
    
    scores = {}
    
    # Calculate scores for each system
    for system, config in system_weights.items():
        score = 0
        keyword_matches = 0
        
        for keyword in config['keywords']:
            if keyword in content_upper:
                keyword_matches += 1
                # Weight by importance and specificity
                score += config['weight']
                
                # Bonus for exact system name matches
                if keyword == system.upper():
                    score += 2
        
        if keyword_matches > 0:
            scores[system] = score
    
    if not scores:
        return None, 0
    
    # Find the highest scoring system
    primary_system = max(scores.keys(), key=lambda k: scores[k])
    confidence = scores[primary_system]
    
    return primary_system, confidence

def analyze_filename_for_primary_system(filename: str) -> tuple:
    """
    Analyze a filename to determine what system it's primarily about.
    Returns (primary_system, confidence)
    """
    
    # Remove .pdf and folder prefix
    clean_name = filename.replace('.pdf', '')
    
    # If there's a prefix, analyze the content after the prefix
    if ' - ' in clean_name:
        parts = clean_name.split(' - ', 1)
        if len(parts) > 1:
            # Analyze the main content (after the prefix)
            main_content = parts[1]
            primary_system, confidence = determine_primary_system(main_content)
            
            # If no clear primary system from content, check if prefix is meaningful
            if not primary_system or confidence < 3:
                prefix_system, prefix_confidence = determine_primary_system(parts[0])
                if prefix_confidence > confidence:
                    return prefix_system, prefix_confidence
            
            return primary_system, confidence
    else:
        # No prefix, analyze entire filename
        return determine_primary_system(clean_name)

def scan_all_folders_for_misplaced_files():
    """Scan all folders and identify files that should be moved."""
    
    organized_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    
    if not organized_path.exists():
        print(f"❌ Error: Organized folder not found at {organized_path}")
        return {}
    
    moves_needed = defaultdict(list)  # target_folder -> [(source_file, source_folder, confidence)]
    total_misplaced = 0
    
    print("🔍 Analyzing all folders for misplaced files...")
    print("=" * 70)
    
    for folder in organized_path.iterdir():
        if not folder.is_dir():
            continue
        
        folder_name = folder.name
        pdf_files = list(folder.glob("*.pdf"))
        
        print(f"\n📁 {folder_name}/ ({len(pdf_files)} files)")
        
        misplaced_in_folder = 0
        
        for pdf_file in pdf_files:
            primary_system, confidence = analyze_filename_for_primary_system(pdf_file.name)
            
            # Only consider it misplaced if:
            # 1. We found a primary system
            # 2. It's different from current folder
            # 3. Confidence is high enough (≥3)
            if (primary_system and 
                primary_system != folder_name and 
                confidence >= 3):
                
                moves_needed[primary_system].append((pdf_file, folder_name, confidence))
                misplaced_in_folder += 1
                total_misplaced += 1
                
                print(f"   🔄 {pdf_file.name}")
                print(f"      → Should be in {primary_system}/ (confidence: {confidence})")
        
        if misplaced_in_folder == 0:
            print(f"   ✅ All files correctly placed")
        else:
            print(f"   ⚠️  {misplaced_in_folder} files should be moved")
    
    print(f"\n📊 Analysis Summary:")
    print(f"   🔄 Total misplaced files: {total_misplaced}")
    print(f"   📂 Target folders affected: {len(moves_needed)}")
    
    return dict(moves_needed)

def execute_smart_recategorization():
    """Execute the smart recategorization process."""
    
    # Analyze current state
    moves_needed = scan_all_folders_for_misplaced_files()
    
    if not moves_needed:
        print(f"\n🎉 All files are correctly categorized!")
        return True
    
    # Show summary of moves
    print(f"\n📋 Proposed moves:")
    for target_folder, file_moves in moves_needed.items():
        print(f"   📂 → {target_folder}/ ({len(file_moves)} files)")
    
    # Ask for confirmation
    response = input(f"\n❓ Proceed with recategorization? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("❌ Operation cancelled.")
        return False
    
    # Execute moves
    organized_path = Path("/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system")
    
    print(f"\n🔄 Executing recategorization...")
    
    moved_count = 0
    errors = []
    
    for target_system, file_moves in moves_needed.items():
        target_folder = organized_path / target_system
        target_folder.mkdir(exist_ok=True)
        
        print(f"\n📂 Moving to {target_system}/:")
        
        for source_file, source_folder, confidence in file_moves:
            try:
                # Create new filename with correct prefix
                old_name = source_file.name
                
                # Remove old prefix if exists and add correct one
                if ' - ' in old_name:
                    content_part = old_name.split(' - ', 1)[1]
                else:
                    content_part = old_name
                
                # Create new name with correct prefix
                new_name = f"{target_system} - {content_part}"
                dest_path = target_folder / new_name
                
                # Handle duplicates
                counter = 1
                original_dest = dest_path
                while dest_path.exists():
                    stem = original_dest.stem
                    suffix = original_dest.suffix
                    dest_path = target_folder / f"{stem} ({counter}){suffix}"
                    counter += 1
                
                # Move file
                shutil.move(str(source_file), str(dest_path))
                moved_count += 1
                
                print(f"   ✅ {old_name}")
                print(f"      → {dest_path.name}")
                
            except Exception as e:
                error_msg = f"Failed to move {source_file.name}: {str(e)}"
                errors.append(error_msg)
                print(f"   ❌ {error_msg}")
    
    print(f"\n✅ Smart recategorization complete!")
    print(f"📊 Results:")
    print(f"   ✅ Successfully moved: {moved_count} files")
    print(f"   ❌ Errors: {len(errors)}")
    
    return True

if __name__ == "__main__":
    print("🧠 Smart PDF Recategorization Tool")
    print("=" * 50)
    print("This tool analyzes the PRIMARY topic of each file and moves")
    print("files to their correct system folders.\n")
    
    success = execute_smart_recategorization()
    
    if success:
        print("\n🎯 Recommendation: Run create_alphabetical_copy.py again to update!")