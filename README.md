# PDF Organization Project

**Automatically organize thousands of PDF files by extracting their headers and sorting them alphabetically.**

Transform messy PDF collections like `side_1234.pdf` into organized files like `Teams - How to share screen.pdf`, `Outlook - Email setup guide.pdf`, etc.

## 🚀 Quick Start

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Set Your PDF Source Folder
Edit `simple_alphabetical_organizer.py` and change this line:
```python
source_dir = Path("/Users/marius.cook/Downloads/PDF splitt 3")
```
to your PDF folder:
```python
source_dir = Path("/path/to/your/pdf/folder")
```

### 3. Run the Organizer
```bash
python simple_alphabetical_organizer.py
```

**That's it!** Your PDFs are now organized in `alphabetical_articles/` folder.

## 📊 What You Get

- **1,977+ organized files** with names like "System - Article Title.pdf"
- **Alphabetical sorting** by filename (Adobe, Altinn, Teams, etc.)
- **Automatic cleanup** of weird formats into separate folder
- **97.7% success rate** for header extraction

## 🛠️ Configuration

### Change Output Folder
In `simple_alphabetical_organizer.py`:
```python
output_dir = Path("/your/desired/output/folder")
```

### Add New System Names
In `simple_alphabetical_organizer.py`, add to the `system_mapping` dictionary:
```python
system_mapping = {
    'YOURAPP': 'YourApp',
    'CUSTOMSYSTEM': 'CustomSystem',
    # ... existing mappings
}
```

### Adjust Header Detection
Modify `skip_patterns` in `find_header_in_text()` to skip unwanted text:
```python
skip_patterns = [
    r'^(Your unwanted pattern)',
    # ... existing patterns
]
```

## 🧹 Clean Up Weird Files

Some files might have non-standard naming. Use the cleanup tool:

```bash
# Preview what will be moved
python cleanup_weird_files.py analyze

# Move weird files to separate folder
python cleanup_weird_files.py move
```

### Configure Cleanup Rules
In `cleanup_weird_files.py`, modify the `valid_systems` set:
```python
valid_systems = {
    'yourapp', 'customsystem',  # Add your systems here
    # ... existing systems
}
```

Add words that should be considered "weird" (non-system):
```python
non_system_words = {
    'when', 'how', 'why',  # Add words that aren't system names
    # ... existing words
}
```

## 📁 Project Structure

```
├── alphabetical_articles/          # 📤 Final organized PDFs (alphabetical)
│   ├── Adobe - *.pdf               # Files sorted alphabetically
│   ├── Altinn - *.pdf
│   ├── Teams - *.pdf
│   └── _weird_format_files/        # 🗂️ Non-standard files
├── simple_alphabetical_organizer.py # 🎯 Main script
├── cleanup_weird_files.py          # 🧹 Cleanup utility
└── README.md                       # 📖 This file
```

## 🔧 Advanced Usage

### Test Header Extraction
```bash
python simple_alphabetical_organizer.py test
```

### Analyze Files Before Processing
```bash
python cleanup_weird_files.py analyze
```

### Custom PDF Processing
The header extraction works by:
1. **Extract text** from first page using pdfplumber → PyPDF2 fallback
2. **Find header** by skipping metadata and taking first meaningful line
3. **Identify system** from first word of header
4. **Create filename** as "System - Article Title.pdf"

## 🎯 Example Results

**Before:**
```
side_1234.pdf
side_5678.pdf
side_9012.pdf
```

**After (alphabetically sorted):**
```
Adobe - Convert PDF to Word document.pdf
Outlook - Configure email forwarding rules.pdf
Teams - How to share screen in meetings.pdf
```

## 🚨 Troubleshooting

### No Headers Extracted
- Your PDFs might be image-only scans
- Consider adding OCR support with `pytesseract`

### Wrong System Detection
- Add your system keywords to `system_mapping`
- Check `skip_patterns` for text being ignored

### Files in Wrong Category
- Review and adjust the `valid_systems` list
- Use `cleanup_weird_files.py analyze` to preview changes

## 📝 Requirements

- Python 3.7+
- PyPDF2 (PDF text extraction)
- pdfplumber (Better PDF parsing)

## 🤝 Contributing

1. Fork the repository
2. Make your changes
3. Test with your PDF collection
4. Submit a pull request

Perfect for organizing documentation, manuals, tutorials, or any large PDF collection into a clean alphabetical list!

