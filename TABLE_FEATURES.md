# Table Extraction and Analysis Features

## Overview

Added Camelot-based table extraction to accurately detect and analyze tables in research papers.

---

## New Features

### 1. **Accurate Table Count** ✅
- **What it does:** Uses Camelot library to extract and count actual tables in the PDF
- **How it works:** 
  - Tries `lattice` method first (for bordered tables)
  - Falls back to `stream` method if needed (for borderless tables)
  - Stores accurate count in `self.total_tables_count`
- **Used in:** Statistics display (`total_tables` field)

### 2. **Check #18: Units in Table Headers** ✅
- **What it checks:** Verifies that all column headers in tables have units specified
- **Why it matters:** IEEE and scientific standards require units to be clearly specified for all measured quantities
- **How it works:**
  - Extracts headers from each table
  - Checks for common unit patterns:
    - Direct units: `m`, `cm`, `kg`, `Hz`, `V`, `%`, `°C`, etc.
    - Units in brackets: `[m]`, `[kg]`, `[Hz]`
    - Units in parentheses: `(m)`, `(kg)`, `(Hz)`
  - Skips non-numeric columns (Name, Description, Type, etc.)
  - Reports tables with missing units

**Example Issues Detected:**
- ❌ Column: "Length" (missing unit) → Should be "Length (m)" or "Length [mm]"
- ❌ Column: "Voltage" → Should be "Voltage (V)"
- ❌ Column: "Temperature" → Should be "Temperature (°C)"
- ✅ Column: "Speed (m/s)" → Correct
- ✅ Column: "Mass [kg]" → Correct

---

## Implementation Details

### Dependencies Added
```txt
camelot-py[cv]>=0.11.0
opencv-python>=4.8.0
pandas>=3.0.0
numpy>=2.4.0
```

### Code Changes

#### 1. `pdf_processor.py` - New Method
```python
def _extract_tables(self, pdf_path: str):
    """Extract tables using Camelot and analyze them."""
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    if tables.n == 0:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
    
    self.total_tables_count = tables.n
    self.extracted_tables = [...]  # Store table data
```

#### 2. Updated Statistics
```python
def _collect_statistics(self, doc: fitz.Document) -> Dict:
    return {
        "total_tables": self.total_tables_count,  # Now uses Camelot count
        # ... other stats
    }
```

#### 3. New Check Method
```python
def _check_table_units(self) -> List[ErrorInstance]:
    """Check if all column headers have units specified."""
    # Analyzes extracted tables
    # Reports missing units per table
```

---

## Supported Unit Patterns

### Distance/Length
- `m`, `cm`, `mm`, `μm`, `km`

### Mass/Weight
- `kg`, `g`, `mg`, `μg`

### Time
- `s`, `ms`, `μs`, `min`, `h`

### Frequency
- `Hz`, `kHz`, `MHz`, `GHz`

### Electrical
- `V`, `mV`, `A`, `mA`, `W`, `mW`, `kW`, `MW`

### Temperature
- `°C`, `°F`, `K`

### Pressure
- `Pa`, `kPa`, `MPa`, `GPa`

### Other
- `%`, `rpm`, `mol`, `L`, `mL`

---

## Usage

The features are automatically enabled. When you upload a PDF:

1. **Camelot extracts all tables** from the document
2. **Accurate table count** is displayed in statistics
3. **Check #18 runs** on all extracted tables
4. **Errors are reported** for tables with headers missing units

---

## Example Error Report

```
Check #18: Missing Units in Table Headers
Description: Table 2 (page 5) has column headers without units: 
             Column 2: 'Voltage', Column 3: 'Current', Column 4: 'Power'
Error Type: table_units
```

---

## Performance Notes

- Camelot table extraction adds ~2-5 seconds to processing time
- More accurate than regex-based table counting
- Works with both bordered and borderless tables
- Extracts actual table structure (rows, columns, cells)

---

## Current Check List (12 Total)

**Structure & Content (5):**
1. Abstract Section
2. Index Terms
3. References Section
4. Roman Numeral Headings
5. Introduction Section

**Numbering (3):**
6. Figure Numbering
7. Table Numbering
8. Equation Numbering

**Table Analysis (1):**
18. **Units in Table Headers** ⭐ NEW

**Typography (3):**
12. Repeated Words
15. et al. Formatting
16. First-Person Pronouns
17. Reference List Numbering

---

## Testing

Upload a PDF with tables and the system will:
- ✅ Extract all tables accurately
- ✅ Show correct table count in statistics
- ✅ Check column headers for units
- ✅ Report tables with missing units

---

## Future Enhancements

Possible future additions:
- Check table captions follow IEEE format
- Verify table numbering is sequential
- Check table citations in text
- Validate table formatting consistency
