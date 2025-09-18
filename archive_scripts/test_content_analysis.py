#!/usr/bin/env python3
"""
Improved Content-Based PDF Analysis
===================================

This script uses improved algorithms to better determine what a PDF is actually about:
1. Analyzes the PRIMARY PROBLEM/ISSUE described
2. Looks at the title and first paragraph context
3. Uses weighted scoring based on problem context
4. Distinguishes between the main issue and supporting systems
"""

import os
import re
import shutil
from pathlib import Path
import PyPDF2
import pdfplumber
from typing import Dict, List, Tuple, Optional

def extract_pdf_content(file_path: str, max_pages: int = 2) -> str:
    """Extract text content from PDF file."""
    content = ""
    
    try:
        # Try pdfplumber first
        with pdfplumber.open(file_path) as pdf:
            for page_num in range(min(max_pages, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text()
                if text:
                    content += text + "\n"
    except:
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(min(max_pages, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
        except Exception as e:
            print(f"    Error reading {file_path}: {e}")
    
    return content

def analyze_primary_issue(content: str, filename: str) -> str:
    """
    Determine what the PRIMARY issue/problem is about using context analysis.
    """
    
    # Split content into sections
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Get title and first few lines (usually contain the main problem)
    title = lines[0] if lines else ""
    first_paragraph = ' '.join(lines[:5]) if len(lines) >= 5 else content[:500]
    
    print(f"  📄 Title: {title}")
    print(f"  📝 First lines: {first_paragraph[:100]}...")
    
    # Improved system patterns with context awareness
    system_analysis = {
        'OneDrive': {
            'primary_patterns': [
                r'OneDrive.*(?:ikke|feil|problem|sync|synkroniser)',
                r'(?:ikke|feil|problem).*OneDrive',
                r'OneDrive.*(?:fil|mappe|lagring)',
                r'(?:sync|synkroniser).*OneDrive'
            ],
            'title_weight': 10,
            'problem_weight': 8
        },
        'Citrix': {
            'primary_patterns': [
                r'Citrix.*(?:starter ikke|feil|problem|app|workspace)',
                r'(?:ikke|feil|problem).*Citrix(?!\s+til)',
                r'Citrix.*(?:workspace|applikasjon|program)',
                r'(?:app|program).*Citrix'
            ],
            'title_weight': 10,
            'problem_weight': 8
        },
        'Teams': {
            'primary_patterns': [
                r'Teams.*(?:møte|chat|video|lyd|ikke)',
                r'(?:møte|chat|video|lyd).*Teams',
                r'Teams.*(?:fungerer ikke|problem|feil)',
                r'Microsoft\s+Teams'
            ],
            'title_weight': 10,
            'problem_weight': 8
        },
        'Outlook': {
            'primary_patterns': [
                r'Outlook.*(?:epost|email|kalender|ikke)',
                r'(?:epost|email|kalender).*Outlook',
                r'Outlook.*(?:fungerer ikke|problem|feil)',
                r'(?:ikke|feil).*Outlook'
            ],
            'title_weight': 10,
            'problem_weight': 8
        },
        'SMIA': {
            'primary_patterns': [
                r'SMIA.*(?:skattemelding|oppgjør|ikke|feil)',
                r'(?:skattemelding|oppgjør).*SMIA',
                r'SMIA.*(?:behandling|fastsetting)',
                r'(?:ikke|feil).*SMIA'
            ],
            'title_weight': 10,
            'problem_weight': 8
        },
        'Skatteplikt': {
            'primary_patterns': [
                r'(?:skatteplikt|skattekort|D-nummer).*(?:ikke|feil|problem)',
                r'(?:ikke|feil|problem).*(?:skatteplikt|skattekort)',
                r'(?:opprette|endre).*(?:skatteplikt|skattekort)',
                r'begrenset\s+skattepliktig'
            ],
            'title_weight': 10,
            'problem_weight': 8
        },
        'MFA': {
            'primary_patterns': [
                r'MFA.*(?:ikke|feil|problem|authenticator)',
                r'(?:authenticator|tofaktor).*(?:ikke|feil|problem)',
                r'(?:ikke|feil).*(?:MFA|authenticator)',
                r'Multi-factor.*authentication'
            ],
            'title_weight': 10,
            'problem_weight': 8
        }
    }
    
    # Calculate scores for each system
    system_scores = {}
    
    for system, config in system_analysis.items():
        score = 0
        
        # Check title for primary patterns (highest weight)
        for pattern in config['primary_patterns']:
            if re.search(pattern, title, re.IGNORECASE):
                score += config['title_weight']
                print(f"    🎯 {system} title match: +{config['title_weight']}")
        
        # Check first paragraph for primary patterns
        for pattern in config['primary_patterns']:
            matches = len(re.findall(pattern, first_paragraph, re.IGNORECASE))
            if matches > 0:
                score += matches * config['problem_weight']
                print(f"    🎯 {system} problem match: +{matches * config['problem_weight']}")
        
        # General content mentions (lower weight)
        general_mentions = len(re.findall(system, content, re.IGNORECASE))
        if general_mentions > 0:
            score += general_mentions * 1
            print(f"    📊 {system} general mentions: {general_mentions} (+{general_mentions})")
        
        if score > 0:
            system_scores[system] = score
    
    if not system_scores:
        return 'Other'
    
    # Get the system with highest score
    primary_system = max(system_scores.items(), key=lambda x: x[1])[0]
    
    print(f"    🏆 Primary system: {primary_system} (score: {system_scores[primary_system]})")
    if len(system_scores) > 1:
        sorted_scores = sorted(system_scores.items(), key=lambda x: x[1], reverse=True)
        print(f"    📊 All scores: {sorted_scores}")
    
    return primary_system

def test_specific_file(file_path: str):
    """Test the analysis on a specific file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    filename = os.path.basename(file_path)
    print(f"\n🔍 Analyzing: {filename}")
    
    content = extract_pdf_content(file_path)
    if not content:
        print("  ❌ No content extracted")
        return
    
    primary_system = analyze_primary_issue(content, filename)
    print(f"  ✅ Should be in: {primary_system} folder")

if __name__ == "__main__":
    # Test on the problematic OneDrive file
    test_file = "/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system/Citrix/CITRIX - OneDrive Citrix ikke synkronisert med OneDrive utenfor.pdf"
    test_specific_file(test_file)
    
    # Test on a few more files
    test_files = [
        "/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system/Citrix/CITRIX - Figma Tilgang.pdf",
        "/Users/marius.cook/Downloads/PDF splitt 2/organized_by_system/Citrix/CITRIX - Citrix Workspace Resett Citrix.pdf"
    ]
    
    for test_file in test_files:
        test_specific_file(test_file)