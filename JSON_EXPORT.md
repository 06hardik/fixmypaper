# 📥 Automatic JSON Export Feature

## Overview

Every time a user uploads a PDF, the system automatically saves a JSON file containing all the raw extracted data from the PDF. This JSON is saved to your local disk in the `processed/` folder.

---

## 📂 File Location

**Format:** `{job_id}_extracted_data.json`

**Example:** 
```
processed/abc-123-xyz_extracted_data.json
processed/def-456-uvw_extracted_data.json
```

**Location:** `/Users/rishabhkumarjain/research-paper-checker/processed/`

---

## 📊 JSON Structure

### Complete Data Export

```json
{
  "full_text": "Complete text extracted from entire PDF...",
  "total_characters": 45678,
  "page_texts": [
    "Text from page 1...",
    "Text from page 2...",
    "Text from page 3..."
  ],
  "total_pages": 12,
  "line_count": 234,
  "lines": [
    {
      "text": "This is the first line of text",
      "page_num": 0,
      "bbox": {
        "x0": 72.0,
        "y0": 100.5,
        "x1": 523.2,
        "y1": 115.3
      }
    },
    {
      "text": "This is another line with citation [1]",
      "page_num": 0,
      "bbox": {
        "x0": 72.0,
        "y0": 120.0,
        "x1": 450.5,
        "y1": 135.0
      }
    }
  ]
}
```

---

## 🔍 What Each Field Contains

### 1. **`full_text`** (string)
- Complete concatenated text from entire PDF
- Includes all pages joined together
- Used for document-level pattern matching
- Example: "Title\nAbstract\nIntroduction\n..."

### 2. **`total_characters`** (integer)
- Total character count in the document
- Includes spaces, punctuation, everything
- Example: 45678

### 3. **`page_texts`** (array of strings)
- Text from each page separately
- Index matches page number (0-indexed)
- Useful for page-level analysis
- Example: `["Page 1 text...", "Page 2 text..."]`

### 4. **`total_pages`** (integer)
- Number of pages in the PDF
- Example: 12

### 5. **`line_count`** (integer)
- Total number of text lines extracted
- Each line is a separate text block from PDF
- Example: 234

### 6. **`lines`** (array of objects)
- Every line extracted with position data
- **Most important for error detection!**

#### Line Object Structure:
```json
{
  "text": "The actual text content of this line",
  "page_num": 0,  // 0-indexed page number
  "bbox": {
    "x0": 72.0,   // Left edge (points)
    "y0": 100.5,  // Top edge (points)
    "x1": 523.2,  // Right edge (points)
    "y1": 115.3   // Bottom edge (points)
  }
}
```

**Bounding Box (bbox):**
- Coordinates in PDF points (1 point = 1/72 inch)
- Origin (0,0) is bottom-left of page
- Used to place error highlights in correct position

---

## 🔄 Data Flow

```
User uploads PDF
    ↓
PyMuPDF extracts text
    ↓
Text organized into lines with positions
    ↓
JSON created with all extracted data
    ↓
JSON saved to processed/{job_id}_extracted_data.json
    ↓
Data passed to error detection
    ↓
Errors found and highlighted
```

---

## 💡 Use Cases for Exported JSON

### 1. **Training Machine Learning Models**
```python
import json
import glob

# Load all extracted JSONs
for json_file in glob.glob('processed/*_extracted_data.json'):
    with open(json_file) as f:
        data = json.load(f)
        # Train model on data['full_text']
```

### 2. **Analyzing Error Patterns**
```python
# Analyze what text triggers certain errors
with open('processed/abc-123_extracted_data.json') as f:
    data = json.load(f)
    
for line in data['lines']:
    if 'Figure' in line['text']:
        print(f"Figure found on page {line['page_num']}")
```

### 3. **Building Custom Checks**
```python
# Create your own error detection rules
import re

with open('processed/abc-123_extracted_data.json') as f:
    data = json.load(f)

# Check for custom patterns
for line in data['lines']:
    if re.search(r'CUSTOM_PATTERN', line['text']):
        print(f"Custom issue found: {line['text']}")
```

### 4. **Text Analytics**
```python
from collections import Counter

with open('processed/abc-123_extracted_data.json') as f:
    data = json.load(f)

# Word frequency analysis
words = data['full_text'].lower().split()
freq = Counter(words)
print(f"Most common words: {freq.most_common(10)}")
```

### 5. **Debugging Error Detection**
```python
# When an error is reported, trace back to original text
with open('processed/abc-123_extracted_data.json') as f:
    data = json.load(f)

# Find specific line
target_page = 5
for line in data['lines']:
    if line['page_num'] == target_page:
        print(f"Line: {line['text']}")
        print(f"Position: {line['bbox']}")
```

---

## 📈 Example JSON File

**File:** `processed/abc123_extracted_data.json`

```json
{
  "full_text": "Research Paper Title\n\nAbstract\n\nThis paper presents...\n\n1. Introduction\n\nThe field of machine learning has seen...",
  "total_characters": 5432,
  "page_texts": [
    "Research Paper Title\n\nAbstract\n\nThis paper presents...",
    "1. Introduction\n\nThe field of machine learning...",
    "2. Related Work\n\nPrevious studies have shown..."
  ],
  "total_pages": 3,
  "line_count": 45,
  "lines": [
    {
      "text": "Research Paper Title",
      "page_num": 0,
      "bbox": {
        "x0": 150.0,
        "y0": 700.0,
        "x1": 450.0,
        "y1": 725.0
      }
    },
    {
      "text": "This paper presents a novel approach to error detection,[1] which improves accuracy.",
      "page_num": 0,
      "bbox": {
        "x0": 72.0,
        "y0": 650.0,
        "x1": 523.0,
        "y1": 665.0
      }
    },
    {
      "text": "The temperature range was 20-30 degrees Celsius.",
      "page_num": 1,
      "bbox": {
        "x0": 72.0,
        "y0": 500.0,
        "x1": 400.0,
        "y1": 515.0
      }
    }
  ]
}
```

---

## 🔧 Technical Implementation

### In `pdf_processor.py`:

```python
def export_extracted_data(self) -> Dict:
    """Export all extracted raw data from the PDF."""
    return {
        'full_text': self.full_text,
        'total_characters': len(self.full_text),
        'page_texts': self.page_texts,
        'total_pages': len(self.page_texts),
        'line_count': len(self.line_info),
        'lines': [
            {
                'text': line_text,
                'page_num': page_num,
                'bbox': {
                    'x0': bbox[0],
                    'y0': bbox[1],
                    'x1': bbox[2],
                    'y1': bbox[3]
                }
            }
            for line_text, bbox, page_num in self.line_info
        ]
    }
```

### In `app.py`:

```python
# Process PDF
errors, annotated_path, statistics, extracted_data = process_pdf(input_path, output_path)

# Save extracted data as JSON
json_filename = f"{job_id}_extracted_data.json"
json_path = os.path.join('processed', json_filename)

import json
with open(json_path, 'w', encoding='utf-8') as json_file:
    json.dump(extracted_data, json_file, indent=2, ensure_ascii=False)

print(f"Extracted data saved to: {json_path}")
```

---

## 📊 File Size Expectations

| PDF Pages | PDF Size | JSON Size (Approximate) |
|-----------|----------|-------------------------|
| 1 page | 100 KB | 5-10 KB |
| 5 pages | 500 KB | 25-50 KB |
| 10 pages | 1 MB | 50-100 KB |
| 20 pages | 2 MB | 100-200 KB |
| 50 pages | 5 MB | 250-500 KB |

**Note:** JSON files are much smaller than PDFs because they contain only text, not images.

---

## 🗑️ Cleanup

JSON files are stored locally and accumulate over time. To clean up old files:

```bash
# Delete JSON files older than 7 days
find processed/ -name "*_extracted_data.json" -mtime +7 -delete

# Delete all JSON files
rm processed/*_extracted_data.json
```

Or add automatic cleanup in `app.py`:

```python
import time
from datetime import datetime, timedelta

def cleanup_old_files():
    """Delete files older than 24 hours."""
    cutoff = time.time() - (24 * 3600)  # 24 hours
    
    for folder in ['processed']:
        for filename in os.listdir(folder):
            if filename.endswith('_extracted_data.json'):
                filepath = os.path.join(folder, filename)
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    print(f"Cleaned up: {filepath}")
```

---

## ✅ Verification

After uploading a PDF, check:

```bash
# List all extracted JSON files
ls -lh processed/*_extracted_data.json

# View a JSON file
cat processed/abc-123_extracted_data.json | head -50

# Count lines in a JSON file
wc -l processed/abc-123_extracted_data.json

# Pretty print JSON
python -m json.tool processed/abc-123_extracted_data.json
```

---

## 🎯 Summary

- ✅ **Automatic:** JSON saved on every PDF upload
- ✅ **No user interaction:** Happens in background
- ✅ **Complete data:** Full text + line-by-line with positions
- ✅ **Local storage:** Saved to `processed/` folder
- ✅ **Machine-readable:** Ready for ML/analysis
- ✅ **Human-readable:** Indented JSON format

**Files created:**
- `processed/{job_id}_extracted_data.json` ← Raw extracted data
- `processed/{job_id}_annotated_{filename}.pdf` ← Annotated PDF
- `uploads/{job_id}_{filename}.pdf` ← Original PDF

All three files share the same `job_id` for easy correlation!
