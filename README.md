# PDF System Organizer

Automatically organizes PDFs into folders by detecting system names (Teams, Outlook, SIAN, KOSS, etc.) in the content.

## 🚀 **One Command Does It All**

**Just run the main script to analyze and categorize ALL your PDFs automatically:**

```bash
python system_organizer.py
```

This single command will:
- 📁 **Scan all PDFs** in your source folder
- 📖 **Read PDF content** to detect system names (Teams, Outlook, SIAN, etc.)
- 📂 **Create system folders** automatically (Teams/, Outlook/, SIAN/, etc.)
- 📄 **Move PDFs** to appropriate folders based on content analysis
- 📊 **Show results** with statistics (typically 83%+ accuracy)

**That's it!** Your PDFs will be organized into 50+ system-specific folders.

## 📂 **Folder Setup - Works on Windows & Mac**

The script will ask you for your PDF folder path when you run it.

**Examples of folder paths:**
- **Windows**: `C:\Users\YourName\Documents\PDFs`
- **Mac**: `/Users/YourName/Documents/PDFs`
- **Tip**: You can drag and drop the folder into the terminal

**Output**: The script creates an `organized_by_system/` folder in your source directory.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Main Organizer (Does Everything!)
```bash
python system_organizer.py
```
**This automatically analyzes and categorizes ALL your PDFs!** ✨

---

## 🔧 **Optional Enhancements** (Run After Main Script)

### 3. Fix Misclassified Files (Optional)
```bash
python reorganize_other_files.py
```

### 4. Rename Files with Descriptive Titles (Optional)
```bash
python rename_pdfs_with_headers.py
```

### 5. Smart Recategorization (Recommended - Improves Accuracy to 98%+)
```bash
python smart_recategorize.py
```

### 6. Fix Cross-System Files (Optional)
```bash
python fix_cross_system_files.py
```

### 7. Flatten System Folders (Optional)
```bash
python flatten_system_folders.py
```

### 8. Create Alphabetical Copy (Optional)
```bash
python create_alphabetical_copy.py
```

---

## 💡 **Summary**

**For most users:** Just run `python system_organizer.py` and you're done!

**For perfect results:** Also run `python smart_recategorize.py` afterward (recommended).

**All other scripts are optional enhancements.**

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