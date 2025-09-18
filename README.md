# PDF System Organizer

Automatically organizes PDFs into folders by detecting system names (Teams, Outlook, SIAN, KOSS, etc.) in the content.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Organizer
```bash
python system_organizer.py
```

### 3. Fix Misclassified Files (Optional)
```bash
python reorganize_other_files.py
```

## What It Does

- Scans PDF content to detect system/application names
- Creates organized folders: `Teams/`, `Outlook/`, `SIAN/`, `KOSS/`, etc.
- Moves PDFs to appropriate system folders
- Achieves 83%+ accuracy

## Supported Systems

Microsoft: Teams, Outlook, SharePoint, OneDrive, Excel, Word, PowerPoint  
Norwegian Gov: SIAN, SMIA, KOSS, Elements, Sofie, ESS  
IT Tools: Jira, Remedy, VPN, Adobe, Cisco  
And 40+ more systems...

## File Structure

- `system_organizer.py` - Main organizer script
- `reorganize_other_files.py` - Fix misclassified files
- `requirements.txt` - Python dependencies