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

### 4. Rename Files with Descriptive Titles
```bash
python rename_pdfs_with_headers.py
```

### 5. Smart Recategorization (Recommended)
```bash
python smart_recategorize.py
```

### 6. Fix Cross-System Files
```bash
python fix_cross_system_files.py
```

### 7. Flatten System Folders
```bash
python flatten_system_folders.py
```

### 8. Create Alphabetical Copy (Optional)
```bash
python create_alphabetical_copy.py
```

## What It Does

- Scans PDF content to detect system/application names
- Creates organized folders: `Teams/`, `Outlook/`, `SIAN/`, `KOSS/`, etc.
- Moves PDFs to appropriate system folders
- Renames files with descriptive article titles
- Smart recategorization fixes misplaced files (98%+ accuracy)
- Fixes cross-system categorization issues (moves files from access-portal folders to independent system folders)
- Flattens folder structure (eliminates sub-folders within system folders)
- Creates alphabetical copy in single folder
- Achieves 83%+ initial accuracy, 98%+ after smart recategorization

## Supported Systems

Microsoft: Teams, Outlook, SharePoint, OneDrive, Excel, Word, PowerPoint  
Norwegian Gov: SIAN, SMIA, KOSS, Elements, Sofie, ESS  
IT Tools: Jira, Remedy, VPN, Adobe, Cisco, MFA  
And 40+ more systems...

## File Structure

- `system_organizer.py` - Main organizer script
- `reorganize_other_files.py` - Fix misclassified files
- `rename_pdfs_with_headers.py` - Rename files with article titles
- `smart_recategorize.py` - Fix misplaced files based on primary topic
- `fix_cross_system_files.py` - Move files from access-portal folders to independent system folders
- `flatten_system_folders.py` - Eliminate sub-folder structure within system folders
- `create_alphabetical_copy.py` - Create single alphabetical folder
- `requirements.txt` - Python dependencies

## Output Structure

After running the scripts, you'll have a completely flat organization:

```
PDF splitt 2/
├── organized_by_system/          # PDFs organized by system (FLAT structure)
│   ├── Teams/                    # 81 files (all in main folder)
│   │   ├── TEAMS - Teams Endre lydinnstillinger...pdf
│   │   ├── TEAMS - Teams kamera fungerer ikke...pdf
│   │   └── ... (all files directly in Teams folder)
│   ├── Outlook/                  # 155 files (all in main folder)
│   │   ├── OUTLOOK - Calendar Outlook...pdf
│   │   ├── OUTLOOK - Email setup...pdf
│   │   └── ... (all files directly in Outlook folder)
│   ├── SIAN/                     # 164 files (all in main folder)
│   │   ├── SIAN - SIAN brev ikke sendt...pdf
│   │   ├── SIAN - SIAN Rutine feilet...pdf
│   │   └── ... (all files directly in SIAN folder)
│   └── ... (58 total system folders, all flat)
└── alphabetical_all_pdfs/        # All PDFs in one folder (A-Z)
    ├── Adobe - Citrix Endre...pdf
    ├── Apple - Calendar Outlook...pdf
    └── ... (2142 files alphabetically)
```

**Key Features:**
- ✅ **Flat Structure**: No sub-folders within system folders
- ✅ **58 System Folders**: Each containing related PDFs directly
- ✅ **2142 Total Files**: All properly categorized and named
- ✅ **Independent Systems**: MVA, Delingstjenester, etc. have their own folders (not under access portals)