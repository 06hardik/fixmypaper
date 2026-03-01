"""
PDF Processor for detecting and annotating IEEE formatting compliance issues.
Checks IEEE-specific structural and formatting requirements in academic papers.

Key design principle:
    Every check emits one ErrorInstance PER OCCURRENCE of the problematic text,
    so every instance gets its own highlight annotation in the output PDF.
"""
import re
import fitz  # PyMuPDF
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ErrorInstance:
    """Represents a single detected formatting issue in the PDF."""
    check_id: int
    check_name: str
    description: str
    page_num: int
    text: str
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    error_type: str


class PDFErrorDetector:
    """Detects IEEE formatting compliance issues in research papers."""

    def __init__(self):
        self.full_text = ""
        self.page_texts = []
        self.line_info = []   # List of (line_text, bbox, page_num)
        self.line_offsets = []

    # =========================================================================
    # TEXT EXTRACTION
    # =========================================================================

    def _extract_all_text(self, doc: fitz.Document):
        """Extract all text from document, building line_info and full_text."""
        current_offset = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            self.page_texts.append(page.get_text())

            page_spans = []
            for block in page.get_text("dict").get("blocks", []):
                if block.get("type") == 0:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span.get("text", "").strip():
                                page_spans.append({
                                    "text": span["text"],
                                    "bbox": span["bbox"],
                                    "page_num": page_num,
                                })

            for line_spans in self._group_spans_by_line(page_spans):
                line_text = "".join(s["text"] for s in line_spans).strip()
                if not line_text:
                    continue

                x0 = min(s["bbox"][0] for s in line_spans)
                y0 = min(s["bbox"][1] for s in line_spans)
                x1 = max(s["bbox"][2] for s in line_spans)
                y1 = max(s["bbox"][3] for s in line_spans)

                self.line_info.append((line_text, (x0, y0, x1, y1), page_num))
                self.line_offsets.append(current_offset)
                self.full_text += line_text + "\n"
                current_offset += len(line_text) + 1

    def _group_spans_by_line(self, spans: list, tolerance: int = 3) -> list:
        """Group spans sharing the same vertical position into lines."""
        if not spans:
            return []

        spans_sorted = sorted(
            spans,
            key=lambda s: (round(s["bbox"][1] / tolerance), s["bbox"][0])
        )

        lines, current_line = [], [spans_sorted[0]]
        current_y = round(spans_sorted[0]["bbox"][1] / tolerance) * tolerance

        for span in spans_sorted[1:]:
            span_y = round(span["bbox"][1] / tolerance) * tolerance
            if abs(span_y - current_y) <= tolerance:
                current_line.append(span)
            else:
                lines.append(current_line)
                current_line = [span]
                current_y = span_y

        if current_line:
            lines.append(current_line)

        return lines

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def _collect_statistics(self, doc: fitz.Document) -> Dict:
        """Collect basic document statistics."""
        figure_nums = {
            int(m.group(1))
            for m in re.finditer(r'(?:Figure|Fig\.?)\s+(\d+)', self.full_text, re.IGNORECASE)
        }
        table_nums = {
            m.group(1)
            for m in re.finditer(r'TABLE\s+([IVXLCDM]+)', self.full_text)
        }
        total_images = sum(len(doc[p].get_images(full=True)) for p in range(len(doc)))

        return {
            "total_words":   len(self.full_text.split()),
            "total_pages":   len(doc),
            "total_figures": len(figure_nums),
            "total_tables":  len(table_nums),
            "total_images":  total_images,
        }

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def detect_errors(self, pdf_path: str) -> Tuple[List[ErrorInstance], fitz.Document, Dict]:
        """Open PDF, extract text, run all checks, return errors + doc + stats."""
        doc = fitz.open(pdf_path)
        self._extract_all_text(doc)
        statistics = self._collect_statistics(doc)
        errors = self._run_document_checks(doc)
        return errors, doc, statistics

    def export_extracted_data(self) -> Dict:
        """Export raw extracted data for external analysis."""
        return {
            "full_text":        self.full_text,
            "total_characters": len(self.full_text),
            "page_texts":       self.page_texts,
            "total_pages":      len(self.page_texts),
            "line_count":       len(self.line_info),
            "lines": [
                {
                    "text":     text,
                    "page_num": page_num,
                    "bbox":     {"x0": bbox[0], "y0": bbox[1], "x1": bbox[2], "y1": bbox[3]},
                }
                for text, bbox, page_num in self.line_info
            ],
        }

    # =========================================================================
    # ORCHESTRATOR
    # =========================================================================

    def _run_document_checks(self, doc: fitz.Document) -> List[ErrorInstance]:
        """Run all 17 compliance and formatting checks."""
        errors = []
        
        # Structure & Content Checks (1-5)
        errors.extend(self._check_abstract_exists())           # Check #1: Abstract section
        errors.extend(self._check_index_terms_exists())        # Check #2: Index terms/keywords
        errors.extend(self._check_references_section_exists()) # Check #3: References section
        errors.extend(self._check_roman_numeral_headings())    # Check #4: Section numbering (Roman numerals)
        errors.extend(self._check_introduction_exists())       # Check #5: Introduction section
        
        # Numbering Checks (6-8)
        errors.extend(self._check_figure_numbering())          # Check #6: Figure numbering
        errors.extend(self._check_table_numbering())           # Check #7: Table numbering
        errors.extend(self._check_equation_numbering())        # Check #8: Equation numbering
        
        # Typography & Formatting Checks (9-17)
        errors.extend(self._check_repeated_words())            # Check #12: Repeated words
        errors.extend(self._check_et_al_formatting())          # Check #15: Incorrect et al. format
        errors.extend(self._check_first_person_pronouns())     # Check #16: First-person pronouns
        errors.extend(self._check_references_numbered())       # Check #17: Reference list numbering
        
        return errors

    # =========================================================================
    # CORE HELPER — emits one ErrorInstance per regex match per line
    # =========================================================================

    def _find_all_occurrences(
        self,
        pattern: re.Pattern,
        check_id: int,
        check_name: str,
        error_type: str,
        description_fn,                             # callable(match, line_text) -> str
        line_filter=None,                           # optional callable(line_text) -> bool
        start_after_keyword: Optional[str] = None, # scan only after a line matching this regex
        stop_at_keyword: Optional[str] = None,     # stop scanning when this regex is seen
    ) -> List[ErrorInstance]:
        """
        Scan every line in the document and emit one ErrorInstance for every
        regex match found.  This guarantees ALL occurrences are highlighted.

        Args:
            pattern:             Compiled regex to search within each line.
            check_id:            IEEE check number.
            check_name:          Human-readable check name.
            error_type:          String key used for colour-coding.
            description_fn:      Callable(match, line_text) -> description string.
            line_filter:         Optional callable; if False the line is skipped.
            start_after_keyword: If given, only start scanning after a line
                                 matching this regex pattern string.
            stop_at_keyword:     If given, stop scanning when a line matches
                                 this regex pattern string.

        Returns:
            List of ErrorInstance, one per regex match.
        """
        errors = []
        active = (start_after_keyword is None)  # start immediately if no gating keyword

        for line_text, line_bbox, page_num in self.line_info:

            # --- section gating ---
            if not active:
                if re.search(start_after_keyword, line_text, re.IGNORECASE):
                    active = True
                continue  # keep iterating until section starts

            if stop_at_keyword and re.search(stop_at_keyword, line_text, re.IGNORECASE):
                break

            # --- optional line-level filter ---
            if line_filter and not line_filter(line_text):
                continue

            # --- emit one ErrorInstance per match ---
            for match in pattern.finditer(line_text):
                errors.append(ErrorInstance(
                    check_id=check_id,
                    check_name=check_name,
                    description=description_fn(match, line_text),
                    page_num=page_num,
                    text=match.group(),
                    bbox=self._calculate_match_bbox(line_text, match, line_bbox),
                    error_type=error_type,
                ))

        return errors

    # =========================================================================
    # CHECK #1 — ABSTRACT EXISTS
    # =========================================================================

    def _check_abstract_exists(self) -> List[ErrorInstance]:
        """
        Verify the paper contains an 'Abstract' section heading.
        Document-level presence check — one error reported if entirely absent.
        """
        if re.search(r'\bAbstract\b', self.full_text, re.IGNORECASE):
            return []

        first_text, first_bbox, first_page = self.line_info[0] if self.line_info else ("", (0, 0, 200, 20), 0)
        return [ErrorInstance(
            check_id=1,
            check_name="Abstract Missing",
            description="No 'Abstract' section found. IEEE papers must include an Abstract at the beginning.",
            page_num=first_page,
            text="[Abstract section not found]",
            bbox=first_bbox,
            error_type="missing_abstract",
        )]

    # =========================================================================
    # CHECK #2 — INDEX TERMS EXISTS
    # =========================================================================

    def _check_index_terms_exists(self) -> List[ErrorInstance]:
        """
        Verify the paper contains an 'Index Terms' section.
        Document-level presence check — one error reported if entirely absent.
        """
        if re.search(r'Index\s+Terms', self.full_text, re.IGNORECASE):
            return []

        first_text, first_bbox, first_page = self.line_info[0] if self.line_info else ("", (0, 0, 200, 20), 0)
        return [ErrorInstance(
            check_id=2,
            check_name="Index Terms Missing",
            description="No 'Index Terms' section found. IEEE papers require Index Terms following the Abstract.",
            page_num=first_page,
            text="[Index Terms section not found]",
            bbox=first_bbox,
            error_type="missing_index_terms",
        )]

    # =========================================================================
    # CHECK #3 — REFERENCES SECTION EXISTS
    # =========================================================================

    def _check_references_section_exists(self) -> List[ErrorInstance]:
        """
        Verify the paper contains a 'References' section.
        Document-level presence check — one error reported if entirely absent.
        """
        if re.search(r'\bReferences\b', self.full_text, re.IGNORECASE):
            return []

        last_text, last_bbox, last_page = self.line_info[-1] if self.line_info else ("", (0, 0, 200, 20), 0)
        return [ErrorInstance(
            check_id=3,
            check_name="References Section Missing",
            description="No 'References' section found. IEEE papers must include a References section at the end.",
            page_num=last_page,
            text="[References section not found]",
            bbox=last_bbox,
            error_type="missing_references",
        )]

    # =========================================================================
    # CHECK #4 — ROMAN NUMERAL SECTION HEADINGS
    # =========================================================================

    def _check_roman_numeral_headings(self) -> List[ErrorInstance]:
        """
        Flag every section heading that uses Arabic numerals instead of Roman numerals.
        e.g. '1. Introduction' should be 'I. INTRODUCTION'.
        Every such heading line gets its own ErrorInstance.
        """
        arabic_heading = re.compile(r'^(\d+)\.\s+([A-Z][a-zA-Z\s]{2,50})$')

        errors = []
        for line_text, line_bbox, page_num in self.line_info:
            stripped = line_text.strip()
            m = arabic_heading.match(stripped)
            if m and 2 <= len(stripped.split()) <= 8:
                errors.append(ErrorInstance(
                    check_id=4,
                    check_name="Non-Roman Numeral Section Heading",
                    description=(
                        f"Section heading '{stripped}' uses Arabic numeral '{m.group(1)}'. "
                        "IEEE format requires Roman numerals in uppercase (e.g., 'I. INTRODUCTION')."
                    ),
                    page_num=page_num,
                    text=stripped,
                    bbox=line_bbox,
                    error_type="non_roman_heading",
                ))

        return errors

    # =========================================================================
    # CHECK #4 — INTRODUCTION SECTION EXISTS
    # =========================================================================

    def _check_introduction_exists(self) -> List[ErrorInstance]:
        """
        Verify the paper contains 'I. INTRODUCTION'.
        If a generic 'Introduction' heading exists but is mis-formatted,
        highlight every occurrence of it (one ErrorInstance each).
        """
        if re.search(r'\bI\.\s+INTRODUCTION\b', self.full_text):
            return []

        has_generic = bool(re.search(r'\bIntroduction\b', self.full_text, re.IGNORECASE))

        if has_generic:
            # Highlight every mis-formatted 'Introduction' occurrence
            return self._find_all_occurrences(
                pattern=re.compile(r'\bIntroduction\b', re.IGNORECASE),
                check_id=5,
                check_name="Introduction Section Misformatted",
                error_type="missing_introduction",
                description_fn=lambda m, line: (
                    f"'Introduction' found but not in IEEE format. "
                    "It should be labelled 'I. INTRODUCTION' — Roman numeral, fully uppercase."
                ),
            )

        # Truly absent — report once on the first line
        first_text, first_bbox, first_page = self.line_info[0] if self.line_info else ("", (0, 0, 200, 20), 0)
        return [ErrorInstance(
            check_id=5,
            check_name="Introduction Section Missing",
            description="No 'I. INTRODUCTION' section found. IEEE papers require an introduction labelled 'I. INTRODUCTION'.",
            page_num=first_page,
            text="[I. INTRODUCTION not found]",
            bbox=first_bbox,
            error_type="missing_introduction",
        )]

    # =========================================================================
    # CHECK #6 — IN-TEXT CITATION FORMAT [n]
    # =========================================================================

    def _check_intext_citation_format(self) -> List[ErrorInstance]:
        """
        Flag every in-text citation that is NOT in IEEE's [n] format.
        Catches APA (Author, Year) and MLA (Author Page) styles.
        Every occurrence is highlighted individually.
        """
        errors = []

        # APA: (Author, 2020) or (Author et al., 2020)
        errors.extend(self._find_all_occurrences(
            pattern=re.compile(r'\([A-Za-z]+(?:\s+et\s+al\.?)?,\s*\d{4}\)'),
            check_id=6,
            check_name="Non-IEEE Citation Format (APA Style)",
            error_type="non_ieee_citation",
            description_fn=lambda m, line: (
                f"Citation '{m.group()}' uses APA format. "
                "IEEE requires bracketed numeric citations like [1]."
            ),
        ))

        # MLA: (Author 42)
        errors.extend(self._find_all_occurrences(
            pattern=re.compile(r'\([A-Za-z]+\s+\d+\)'),
            check_id=6,
            check_name="Non-IEEE Citation Format (MLA Style)",
            error_type="non_ieee_citation",
            description_fn=lambda m, line: (
                f"Citation '{m.group()}' uses MLA format. "
                "IEEE requires bracketed numeric citations like [1]."
            ),
        ))

        return errors

    # =========================================================================
    # CHECK #17 — REFERENCES NUMBERED [n]
    # =========================================================================

    def _check_references_numbered(self) -> List[ErrorInstance]:
        """
        Inside the References section, flag every entry that does NOT start
        with the IEEE bracketed format [n].
        Flags '1. ...' and '(1) ...' styles — one ErrorInstance per entry.
        """
        non_ieee_ref = re.compile(r'^(\d+)\.\s+\S|^\((\d+)\)\s+[A-Z]')

        errors = []
        in_references = False

        for line_text, line_bbox, page_num in self.line_info:
            if re.search(r'\b(References|REFERENCES)\b', line_text):
                in_references = True
                continue

            if not in_references:
                continue

            stripped = line_text.strip()
            m = non_ieee_ref.match(stripped)
            if m:
                num = m.group(1) or m.group(2)
                errors.append(ErrorInstance(
                    check_id=17,
                    check_name="Reference Not in IEEE Bracketed Format",
                    description=(
                        f"Reference entry starts with '{num}.' or '({num})' instead of '[{num}]'. "
                        "IEEE requires references formatted as [1] Author, Title..."
                    ),
                    page_num=page_num,
                    text=stripped[:70],
                    bbox=line_bbox,
                    error_type="non_ieee_reference_format",
                ))

        return errors

    # =========================================================================
    # CHECK #6 — FIGURE NUMBERING
    # =========================================================================

    def _check_figure_numbering(self) -> List[ErrorInstance]:
        """
        Flag every figure label that violates IEEE conventions.
        Valid:   'Fig. 1', 'Figure 2'
        Invalid: 'FIGURE 1' (all-caps word), 'fig 1' (abbreviation without period)
        One ErrorInstance is emitted per violating occurrence anywhere in the document.
        """
        errors = []

        # 'FIGURE N' — all-caps label
        errors.extend(self._find_all_occurrences(
            pattern=re.compile(r'\bFIGURE\s+\d+\b'),
            check_id=6,
            check_name="Figure Label All-Caps (Use 'Fig.' or 'Figure')",
            error_type="invalid_figure_label",
            description_fn=lambda m, line: (
                f"'{m.group()}' uses all-caps 'FIGURE'. "
                "IEEE convention is 'Fig. N' or 'Figure N'."
            ),
        ))

        # 'fig N' — lowercase abbreviation without period
        # Skip lines that already have the valid 'Fig. N' form
        errors.extend(self._find_all_occurrences(
            pattern=re.compile(r'\bfig\s+\d+\b', re.IGNORECASE),
            check_id=6,
            check_name="Figure Abbreviation Missing Period (Use 'Fig.')",
            error_type="invalid_figure_label",
            description_fn=lambda m, line: (
                f"'{m.group()}' is missing the period after 'Fig'. "
                "IEEE convention is 'Fig. N' (with period)."
            ),
            line_filter=lambda t: not re.search(r'\bFig\.\s*\d+\b', t),
        ))

        return errors

    # =========================================================================
    # CHECK #7 — TABLE NUMBERING
    # =========================================================================

    def _check_table_numbering(self) -> List[ErrorInstance]:
        """
        Flag every table label that does not follow IEEE Roman-numeral uppercase style.
        Valid:   'TABLE I', 'TABLE II'
        Invalid: 'TABLE 1' (Arabic numeral), 'Table I' / 'Table 1' (not all-caps)
        One ErrorInstance per violating occurrence anywhere in the document.
        """
        errors = []

        # 'TABLE 1' — Arabic numeral
        errors.extend(self._find_all_occurrences(
            pattern=re.compile(r'\bTABLE\s+\d+\b'),
            check_id=7,
            check_name="Table Uses Arabic Numeral (Use Roman Numeral)",
            error_type="invalid_table_numbering",
            description_fn=lambda m, line: (
                f"'{m.group()}' uses an Arabic numeral. "
                "IEEE requires Roman numerals in uppercase, e.g., 'TABLE I', 'TABLE II'."
            ),
        ))

        # 'Table I', 'Table 1', 'table ...' — label not fully uppercase
        errors.extend(self._find_all_occurrences(
            pattern=re.compile(r'\b[Tt]able\s+[\dIVXLCDMivxlcdm]+\b'),
            check_id=7,
            check_name="Table Label Not in Uppercase (Use 'TABLE')",
            error_type="invalid_table_numbering",
            description_fn=lambda m, line: (
                f"'{m.group()}' is not fully uppercase. "
                "IEEE format requires 'TABLE' in all-caps, e.g., 'TABLE I'."
            ),
            # Skip already-valid 'TABLE [Roman]' occurrences
            line_filter=lambda t: not re.search(r'\bTABLE\s+[IVXLCDM]+\b', t),
        ))

        return errors

    # =========================================================================
    # CHECK #8 — EQUATION NUMBERING
    # =========================================================================

    def _check_equation_numbering(self) -> List[ErrorInstance]:
        """
        For every line identified as a likely equation:
          • Bare number at end without parens → flag that line (one ErrorInstance).
          • Valid (n) label → collect for sequential-order check.
        After scanning, flag the first out-of-sequence equation number.
        """
        errors = []
        eq_numbers: List[int] = []
        eq_locations: Dict[int, Tuple] = {}

        for line_text, line_bbox, page_num in self.line_info:
            if not self._is_likely_equation(line_text):
                continue

            valid_match = re.search(r'\((\d+)\)\s*$', line_text)
            if valid_match:
                eq_num = int(valid_match.group(1))
                eq_numbers.append(eq_num)
                if eq_num not in eq_locations:
                    eq_locations[eq_num] = (line_text, line_bbox, page_num)
            else:
                # Bare number at end of line — flag this specific occurrence
                bare = re.search(r'(?<!\()\b(\d+)\b\s*$', line_text)
                if bare:
                    errors.append(ErrorInstance(
                        check_id=8,
                        check_name="Equation Number Not in Parentheses",
                        description=(
                            f"Equation number '{bare.group(1)}' is not wrapped in parentheses. "
                            "IEEE format requires (1), (2), etc."
                        ),
                        page_num=page_num,
                        text=line_text.strip()[-70:] if len(line_text.strip()) > 70 else line_text.strip(),
                        bbox=line_bbox,
                        error_type="equation_numbering",
                    ))

        # Sequential-order check — flag every out-of-order equation
        if len(eq_numbers) >= 2:
            unique = sorted(set(eq_numbers))
            for i in range(len(unique) - 1):
                if unique[i + 1] != unique[i] + 1:
                    out_num = unique[i + 1]
                    if out_num in eq_locations:
                        line_text, line_bbox, page_num = eq_locations[out_num]
                        errors.append(ErrorInstance(
                            check_id=8,
                            check_name="Non-Sequential Equation Numbering",
                            description=(
                                f"Equation ({out_num}) does not follow ({unique[i]}) sequentially. "
                                "IEEE equations must be numbered consecutively."
                            ),
                            page_num=page_num,
                            text=f"({out_num})",
                            bbox=line_bbox,
                            error_type="equation_numbering",
                        ))

        return errors

    # =========================================================================
    # TYPOGRAPHY & FORMATTING CHECKS
    # =========================================================================

    # =========================================================================
    # TYPOGRAPHY & FORMATTING CHECKS
    # =========================================================================

    def _check_double_spaces(self) -> List[ErrorInstance]:
        """Check #9: Multiple consecutive spaces between words."""
        pattern = re.compile(r'  +')  # Two or more spaces
        return self._find_all_occurrences(
            pattern=pattern,
            check_id=9,
            check_name="Multiple Consecutive Spaces",
            error_type="spacing_error",
            description_fn=lambda m, _: f"Found {len(m.group())} consecutive spaces - should be single space"
        )

    def _check_space_before_punctuation(self) -> List[ErrorInstance]:
        """Check #10: Space before punctuation marks."""
        errors = []
        pattern = re.compile(r'\s+([.,;:])')
        
        for line_text, line_bbox, page_num in self.line_info:
            for match in pattern.finditer(line_text):
                # Skip decimal numbers like "3. 14" or list items like "1. Introduction"
                if match.start() > 0 and line_text[match.start()-1].isdigit():
                    continue
                
                errors.append(ErrorInstance(
                    check_id=10,
                    check_name="Space Before Punctuation",
                    description="Remove space before comma, period, semicolon, or colon",
                    page_num=page_num,
                    text=match.group(),
                    bbox=self._calculate_match_bbox(line_text, match, line_bbox),
                    error_type="punctuation_spacing"
                ))
        
        return errors

    def _check_missing_space_after_punctuation(self) -> List[ErrorInstance]:
        """Check #11: Missing space after comma, period, or semicolon."""
        errors = []
        
        # Missing space after comma (directly followed by letter)
        comma_pattern = re.compile(r',(?=[A-Za-z])')
        errors.extend(self._find_all_occurrences(
            pattern=comma_pattern,
            check_id=11,
            check_name="Missing Space After Comma",
            error_type="punctuation_spacing",
            description_fn=lambda m, _: "Comma should be followed by a space"
        ))
        
        # Missing space after period (between words)
        period_pattern = re.compile(r'\.(?=[A-Z][a-z])')
        errors.extend(self._find_all_occurrences(
            pattern=period_pattern,
            check_id=11,
            check_name="Missing Space After Period",
            error_type="punctuation_spacing",
            description_fn=lambda m, _: "Period should be followed by a space"
        ))
        
        # Missing space after semicolon
        semicolon_pattern = re.compile(r';(?=[A-Za-z])')
        errors.extend(self._find_all_occurrences(
            pattern=semicolon_pattern,
            check_id=11,
            check_name="Missing Space After Semicolon",
            error_type="punctuation_spacing",
            description_fn=lambda m, _: "Semicolon should be followed by a space"
        ))
        
        return errors

    def _check_repeated_words(self) -> List[ErrorInstance]:
        """Check #12: Repeated consecutive words."""
        errors = []
        pattern = re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE)
        
        for line_text, line_bbox, page_num in self.line_info:
            for match in pattern.finditer(line_text):
                word = match.group(1).lower()
                # Skip intentional repetitions or numbers
                if word in ['very', 'long', 'far', 'many', 'much'] or word.isdigit():
                    continue
                
                errors.append(ErrorInstance(
                    check_id=12,
                    check_name="Repeated Word",
                    description=f"Word '{match.group(1)}' appears twice consecutively",
                    page_num=page_num,
                    text=match.group(),
                    bbox=self._calculate_match_bbox(line_text, match, line_bbox),
                    error_type="repeated_word"
                ))
        
        return errors

    def _check_multiple_punctuation(self) -> List[ErrorInstance]:
        """Check #13: Multiple consecutive punctuation marks."""
        errors = []
        pattern = re.compile(r'([.!?])\1+')
        
        for line_text, line_bbox, page_num in self.line_info:
            for match in pattern.finditer(line_text):
                # Allow ellipsis (...) as it might be intentional
                if match.group() == '...':
                    continue
                
                errors.append(ErrorInstance(
                    check_id=13,
                    check_name="Multiple Punctuation Marks",
                    description=f"Multiple consecutive punctuation '{match.group()}' inappropriate for academic writing",
                    page_num=page_num,
                    text=match.group(),
                    bbox=self._calculate_match_bbox(line_text, match, line_bbox),
                    error_type="punctuation_error"
                ))
        
        return errors

    def _check_trailing_spaces(self) -> List[ErrorInstance]:
        """Check #14: Trailing whitespace at end of lines."""
        errors = []
        
        for line_text, line_bbox, page_num in self.line_info:
            # Check if line has trailing spaces or tabs
            if line_text and line_text != line_text.rstrip():
                trailing_count = len(line_text) - len(line_text.rstrip())
                errors.append(ErrorInstance(
                    check_id=14,
                    check_name="Trailing Whitespace",
                    description=f"Line has {trailing_count} trailing space(s) at the end",
                    page_num=page_num,
                    text=repr(line_text[-20:]) if len(line_text) > 20 else repr(line_text),
                    bbox=line_bbox,
                    error_type="whitespace_error"
                ))
        
        return errors

    def _check_et_al_formatting(self) -> List[ErrorInstance]:
        """Check #15: Correct 'et al.' formatting."""
        # Match: "et al" (missing period) or "et. al." (wrong format)
        pattern = re.compile(r'\bet\s+al(?!\.)|et\.\s*al\.', re.IGNORECASE)
        return self._find_all_occurrences(
            pattern=pattern,
            check_id=15,
            check_name="Incorrect et al. Formatting",
            error_type="citation_format",
            description_fn=lambda m, _: "Should be 'et al.' (with period after 'al', not after 'et')"
        )

    def _check_first_person_pronouns(self) -> List[ErrorInstance]:
        """Check #16: First-person pronouns in IEEE-style papers."""
        errors = []
        pattern = re.compile(r'\b(I|we|our|my|us|We|Our|My|Us)\b')
        
        for line_text, line_bbox, page_num in self.line_info:
            # Skip acknowledgments section
            if 'acknowledgment' in line_text.lower() or 'acknowledge' in line_text.lower():
                continue
            
            for match in pattern.finditer(line_text):
                word = match.group()
                idx = match.start()
                
                # Skip if part of acronym or abbreviation
                if idx > 0 and line_text[idx-1].isupper():
                    continue
                if match.end() < len(line_text) and line_text[match.end()].isupper():
                    continue
                
                errors.append(ErrorInstance(
                    check_id=16,
                    check_name="First-Person Pronoun",
                    description=f"IEEE-style papers prefer impersonal tone over first-person pronouns like '{word}'",
                    page_num=page_num,
                    text=word,
                    bbox=self._calculate_match_bbox(line_text, match, line_bbox),
                    error_type="writing_style"
                ))
        
        return errors
    #     """Check #37: Missing space after comma, period, or semicolon."""
    #     errors = []
        
    #     # Missing space after comma (directly followed by letter)
    #     comma_pattern = re.compile(r',(?=[A-Za-z])')
    #     errors.extend(self._find_all_occurrences(
    #         pattern=comma_pattern,
    #         check_id=37,
    #         check_name="Missing Space After Comma",
    #         error_type="punctuation_spacing",
    #         description_fn=lambda m, _: "Comma should be followed by a space"
    #     ))
        
    #     # Missing space after period (between words)
    #     period_pattern = re.compile(r'\.(?=[A-Z][a-z])')
    #     errors.extend(self._find_all_occurrences(
    #         pattern=period_pattern,
    #         check_id=37,
    #         check_name="Missing Space After Period",
    #         error_type="punctuation_spacing",
    #         description_fn=lambda m, _: "Period should be followed by a space"
    #     ))
        
    #     # Missing space after semicolon
    #     semicolon_pattern = re.compile(r';(?=[A-Za-z])')
    #     errors.extend(self._find_all_occurrences(
    #         pattern=semicolon_pattern,
    #         check_id=37,
    #         check_name="Missing Space After Semicolon",
    #         error_type="punctuation_spacing",
    #         description_fn=lambda m, _: "Semicolon should be followed by a space"
    #     ))
        
    #     return errors

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _is_likely_equation(self, text: str) -> bool:
        """
        Heuristic score to decide whether a line is a displayed equation.
        Score >= 4 → treat as equation.
        """
        score = 0
        line = text.strip()

        if len(line) < 3:
            return False

        if re.search(r'[=+\*^×÷≤≥≈≠∑∫∂∇√∏∆λμπσΩαβγδεθ]', line):
            score += 2
        if re.search(r'\b[a-zA-Z]\b', line) and re.search(r'[=+\-*/]', line):
            score += 2
        if re.search(r'\(\d+\)\s*$', line):
            score += 5
        if re.search(r'[_^]\{?\w+\}?|\w+_\d+|\w+\^\d+', line):
            score += 2
        if re.search(r'[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]', line):
            score += 1
        if re.search(r'\([^)]+\).*[=+\-*/]|[=+\-*/].*\([^)]+\)', line):
            score += 1

        common_words = len(re.findall(
            r'\b(the|and|is|of|in|to|for|with|this|that|are|was|were|be|been|'
            r'being|have|has|had|do|does|did|will|would|should|could|can|may|might)\b',
            line.lower()
        ))
        if common_words > 2:
            score -= 3
        if re.match(r'^(The|This|That|These|Those|In|For|However|Therefore|Thus|Hence)\b', line):
            score -= 2
        if len(line) > 150:
            score -= 1
        if re.match(r'^\(\d+\)\s+[A-Z][a-z]+', line):
            score -= 4
        words = re.findall(r'\b[a-zA-Z]{3,}\b', line)
        math_symbols = re.findall(r'[=+\-*/^×÷≤≥≈≠∑∫∂∇√]', line)
        if len(words) > 5 and len(math_symbols) < 2:
            score -= 2

        return score >= 4

    def _calculate_match_bbox(
        self,
        full_line: str,
        match: re.Match,
        line_bbox: Tuple[float, float, float, float],
        padding: int = 2,
    ) -> Tuple[float, float, float, float]:
        """
        Approximate the bounding box of a regex match within its line
        using linear interpolation across the line width.
        """
        text_len = len(full_line)
        if text_len == 0:
            return line_bbox

        x0, y0, x1, y1 = line_bbox
        char_w = (x1 - x0) / text_len
        mx0 = x0 + match.start() * char_w
        mx1 = x0 + match.end()   * char_w

        return (
            max(x0, mx0 - padding),
            y0 - padding,
            min(x1, mx1 + padding),
            y1 + padding,
        )

    # =========================================================================
    # PDF ANNOTATION
    # =========================================================================

    def annotate_pdf(
        self,
        doc: fitz.Document,
        errors: List[ErrorInstance],
        output_path: str,
    ):
        """
        Write a highlight annotation for every ErrorInstance into the PDF,
        then save to output_path.
        """
        color_map = {
            "missing_abstract":          (1.00, 0.70, 0.70),
            "missing_index_terms":       (1.00, 0.80, 0.60),
            "missing_references":        (1.00, 0.85, 0.60),
            "non_roman_heading":         (0.90, 0.90, 0.50),
            "missing_introduction":      (1.00, 0.70, 0.70),
            "non_ieee_citation":         (1.00, 0.75, 0.75),
            "non_ieee_reference_format": (0.85, 0.95, 1.00),
            "invalid_figure_label":      (0.95, 0.85, 1.00),
            "invalid_table_numbering":   (0.80, 0.95, 0.85),
            "equation_numbering":        (1.00, 0.90, 0.70),
        }

        for error in errors:
            page = doc[error.page_num]
            color = color_map.get(error.error_type, (1.00, 1.00, 0.60))

            hl = page.add_highlight_annot(error.bbox)
            hl.set_colors(stroke=color)
            hl.set_opacity(0.5)
            hl.info["title"]   = f"Check #{error.check_id}: {error.check_name}"
            hl.info["content"] = f"{error.description}\n\nFound: '{error.text}'"
            hl.update()

        doc.save(output_path, garbage=4, deflate=True)
        doc.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

def process_pdf(
    input_path: str,
    output_path: str,
) -> Tuple[List[ErrorInstance], str, Dict, Dict]:
    """
    Full pipeline: open PDF → detect errors → annotate → save.

    Returns:
        errors         – list of ErrorInstance objects
        output_path    – path to the annotated PDF
        statistics     – document statistics dict
        extracted_data – raw extracted text and line data
    """
    detector = PDFErrorDetector()
    errors, doc, statistics = detector.detect_errors(input_path)
    detector.annotate_pdf(doc, errors, output_path)
    extracted_data = detector.export_extracted_data()
    return errors, output_path, statistics, extracted_data