# Complete List of 17 Error Checks

This document lists all 17 error checks implemented in the Research Paper Error Checker, sequentially numbered from 1 to 17.

---

## Structure & Content Checks (1-5)

### ✅ Check #1: Abstract Section
**What it checks:** Verifies the paper contains an "Abstract" section heading.

**Why it matters:** IEEE papers must include an Abstract at the beginning summarizing the research.

**Example Error:**
- "No 'Abstract' section found."

---

### ✅ Check #2: Index Terms/Keywords
**What it checks:** Verifies the paper contains an "Index Terms" section.

**Why it matters:** IEEE requires Index Terms (keywords) following the Abstract for indexing and searchability.

**Example Error:**
- "No 'Index Terms' section found."

---

### ✅ Check #3: References Section
**What it checks:** Verifies the paper contains a "References" section.

**Why it matters:** All academic papers must properly cite sources in a References section.

**Example Error:**
- "No 'References' section found."

---

### ✅ Check #4: Roman Numeral Section Headings
**What it checks:** Flags section headings using Arabic numerals (1, 2, 3) instead of Roman numerals (I, II, III).

**Why it matters:** IEEE format requires uppercase Roman numerals for section headings.

**Examples:**
- ❌ "1. Introduction" → ✅ "I. INTRODUCTION"
- ❌ "2. Methodology" → ✅ "II. METHODOLOGY"

---

### ✅ Check #5: Introduction Section
**What it checks:** Verifies the paper contains "I. INTRODUCTION" section.

**Why it matters:** IEEE papers require a properly formatted introduction section.

**Examples:**
- ❌ "Introduction" → ✅ "I. INTRODUCTION"
- ❌ "1. INTRODUCTION" → ✅ "I. INTRODUCTION"

---

## Numbering Checks (6-8)

### ✅ Check #6: Figure Numbering
**What it checks:** Ensures figures follow IEEE conventions: "Fig. 1" or "Figure 1".

**Why it matters:** Consistent figure labeling improves readability and follows IEEE standards.

**Examples:**
- ❌ "FIGURE 1" (all-caps) → ✅ "Fig. 1" or "Figure 1"
- ❌ "fig 1" (missing period) → ✅ "Fig. 1"

---

### ✅ Check #7: Table Numbering
**What it checks:** Ensures tables use uppercase Roman numerals: "TABLE I", "TABLE II".

**Why it matters:** IEEE requires Roman numeral notation for tables, distinct from figures.

**Examples:**
- ❌ "TABLE 1" (Arabic) → ✅ "TABLE I"
- ❌ "Table I" (not uppercase) → ✅ "TABLE I"

---

### ✅ Check #8: Equation Numbering
**What it checks:** Verifies equations are numbered sequentially (1), (2), (3)...

**Why it matters:** Sequential numbering ensures proper cross-referencing and readability.

**Example Error:**
- "Equation (5) does not follow (3) sequentially."

---

## Typography & Formatting Checks (9-17)

### ✅ Check #9: Multiple Consecutive Spaces
**What it checks:** Flags 2+ consecutive spaces between words.

**Why it matters:** Reduces readability and reflects poor formatting quality.

**Examples:**
- ❌ "This  has  multiple   spaces"
- ✅ "This has single spaces"

---

### ✅ Check #10: Space Before Punctuation
**What it checks:** Flags unnecessary spaces before commas, periods, semicolons, or colons.

**Why it matters:** Violates standard grammar and IEEE formatting conventions.

**Examples:**
- ❌ "model , algorithm ."
- ✅ "model, algorithm."

---

### ✅ Check #11: Missing Space After Punctuation
**What it checks:** Flags missing spaces after commas, periods, or semicolons.

**Why it matters:** Impacts readability and makes the document look unprofessional.

**Examples:**
- ❌ "model,algorithm.Works"
- ✅ "model, algorithm. Works"

---

### ✅ Check #12: Repeated Words
**What it checks:** Detects the same word appearing consecutively.

**Why it matters:** Common proofreading error that reduces academic credibility.

**Examples:**
- ❌ "the the system"
- ❌ "is is working"
- ✅ "the system is working"

**Note:** Intentional repetitions like "very very" are allowed.

---

### ✅ Check #13: Multiple Punctuation Marks
**What it checks:** Flags repeated punctuation like "..", "!!", "??".

**Why it matters:** Informal and inappropriate for formal research writing.

**Examples:**
- ❌ "What is this??"
- ❌ "Really.."
- ✅ "What is this?"

**Note:** Ellipsis "..." is allowed as it may be intentional.

---

### ✅ Check #14: Trailing Whitespace
**What it checks:** Detects extra spaces or tabs at the end of lines.

**Why it matters:** Invisible formatting issue that affects document cleanliness and publishing quality.

**Example:**
- ❌ "This line has spaces    "
- ✅ "This line has no trailing spaces"

**Note:** PDF extraction often strips trailing spaces, so this check may rarely trigger.

---

### ✅ Check #15: Incorrect et al. Formatting
**What it checks:** Ensures proper "et al." formatting in citations.

**Why it matters:** Important citation convention in academic writing.

**Examples:**
- ❌ "Smith et al" (missing period)
- ❌ "Smith et. al." (period in wrong place)
- ✅ "Smith et al."

---

### ✅ Check #16: First-Person Pronouns
**What it checks:** Flags use of I, we, our, my, us in the main text.

**Why it matters:** IEEE-style research papers typically prefer formal, impersonal tone over first-person narration.

**Examples:**
- ❌ "We propose a new method"
- ❌ "Our results show"
- ✅ "A new method is proposed"
- ✅ "The results show"

**Note:** Acknowledgments sections are exempted from this check.

---

### ✅ Check #17: Reference List Numbering
**What it checks:** Ensures reference entries use IEEE bracketed format [1], [2], etc.

**Why it matters:** Maintains consistency with IEEE citation style throughout the paper.

**Examples:**
- ❌ "1. Smith, J. et al..." (period format)
- ❌ "(1) Smith, J. et al..." (parentheses format)
- ✅ "[1] Smith, J. et al..."

---

## Removed Checks

The following checks were **removed** as they are not currently implemented:

- ❌ In-text citation format detection (APA/MLA vs IEEE [n])
- ❌ En-dash for numeric ranges
- ❌ Unit spacing checks
- ❌ Citation-reference matching
- ❌ Uncited references detection
- ❌ Reference ordering
- ❌ DOI in references
- ❌ URL formatting
- ❌ Acronym definitions

These may be added in future versions if needed.

---

## Summary by Category

| Category | Count | Check Numbers |
|----------|-------|---------------|
| Structure & Content | 5 | 1-5 |
| Numbering (Figures/Tables/Equations) | 3 | 6-8 |
| Typography & Formatting | 9 | 9-17 |
| **Total** | **17** | **1-17** |

---

## Testing

To test all checks on a document:

```python
from pdf_processor import PDFErrorDetector

detector = PDFErrorDetector()
errors, doc, statistics = detector.detect_errors("your_paper.pdf")

print(f"Total errors found: {len(errors)}")
for error in errors:
    print(f"Check #{error.check_id}: {error.check_name}")
    print(f"  Page {error.page_num}: {error.description}")
```

---

## Web Application

The web app at `http://localhost:5001` automatically runs all 17 checks and displays:
- Total error count
- Error breakdown by type
- Page-by-page highlighting in the annotated PDF
- Document statistics (words, pages, figures, tables, images)

Upload your PDF and get instant feedback on all 17 formatting checks!
