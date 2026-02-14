"""
PDF Processor for detecting and annotating research paper errors.
Comprehensive error detection for academic papers.
"""
import re
import fitz  # PyMuPDF
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ErrorInstance:
    """Represents a detected error in the PDF."""
    check_id: int
    check_name: str
    description: str
    page_num: int
    text: str
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    error_type: str


class PDFErrorDetector:
    """Detects formatting errors in research papers based on comprehensive checks."""
    
    def __init__(self):
        # Store full document text for document-level checks
        self.full_text = ""
        self.page_texts = []
        self.line_info = []  # (text, bbox, page_num)
        
    def _extract_all_text(self, doc: fitz.Document):
        """Extract all text from document for analysis."""
        self.full_text = ""
        self.page_texts = []
        self.line_info = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            self.page_texts.append(page_text)
            self.full_text += page_text + "\n"
            
            # Get text with position information
            text_instances = page.get_text("dict")
            blocks = text_instances.get("blocks", [])
            
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        line_text = ""
                        line_bbox = None
                        
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                            if line_bbox is None:
                                line_bbox = span["bbox"]
                            else:
                                # Expand bounding box
                                line_bbox = (
                                    min(line_bbox[0], span["bbox"][0]),
                                    min(line_bbox[1], span["bbox"][1]),
                                    max(line_bbox[2], span["bbox"][2]),
                                    max(line_bbox[3], span["bbox"][3])
                                )
                        
                        if line_text.strip() and line_bbox:
                            self.line_info.append((line_text, line_bbox, page_num))
    
    def _collect_statistics(self, doc: fitz.Document) -> Dict:
        """
        Collect document statistics for infographics.
        Returns dictionary with word count, images, tables, figures.
        """
        statistics = {
            'total_words': 0,
            'total_images': 0,
            'total_tables': 0,
            'total_figures': 0,
            'total_pages': len(doc)
        }
        
        # Count words
        words = self.full_text.split()
        statistics['total_words'] = len(words)
        
        # Count figures (from captions)
        figure_pattern = r'Figure\s+(\d+)'
        figure_numbers = set()
        for match in re.finditer(figure_pattern, self.full_text, re.IGNORECASE):
            figure_numbers.add(int(match.group(1)))
        statistics['total_figures'] = len(figure_numbers)
        
        # Count tables (from captions)
        table_pattern = r'Table\s+(\d+)'
        table_numbers = set()
        for match in re.finditer(table_pattern, self.full_text, re.IGNORECASE):
            table_numbers.add(int(match.group(1)))
        statistics['total_tables'] = len(table_numbers)
        
        # Count images (embedded images in PDF)
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            statistics['total_images'] += len(image_list)
        
        return statistics
    
    def detect_errors(self, pdf_path: str) -> Tuple[List[ErrorInstance], fitz.Document, Dict]:
        """
        Detect all errors in the PDF.
        Returns list of errors, PDF document object, and statistics.
        """
        doc = fitz.open(pdf_path)
        all_errors = []
        
        # Extract all text for document-level analysis
        self._extract_all_text(doc)
        
        # Collect statistics
        statistics = self._collect_statistics(doc)
        
        # Run line-level checks
        for line_text, line_bbox, page_num in self.line_info:
            errors = self._check_line(line_text, line_bbox, page_num)
            all_errors.extend(errors)
        
        # Run document-level checks
        doc_errors = self._run_document_checks(doc)
        all_errors.extend(doc_errors)
        
        return all_errors, doc, statistics
    
    def _run_document_checks(self, doc: fitz.Document) -> List[ErrorInstance]:
        """Run checks that require full document analysis."""
        errors = []
        
        # Figures & Tables
        errors.extend(self._check_figure_citations())
        errors.extend(self._check_table_citations())
        errors.extend(self._check_figure_numbering())
        errors.extend(self._check_table_numbering())
        
        # Equations
        errors.extend(self._check_equation_numbering())
        errors.extend(self._check_equation_parentheses())
        errors.extend(self._check_equation_references())
        
        # Citations
        errors.extend(self._check_citation_style_consistency())
        errors.extend(self._check_citation_reference_match())
        errors.extend(self._check_uncited_references())
        errors.extend(self._check_reference_order())
        errors.extend(self._check_doi_in_references())
        errors.extend(self._check_url_format())
        
        # Acronyms
        errors.extend(self._check_acronym_definitions())
        
        return errors
    
    # ========== FIGURES & TABLES ==========
    
    def _check_figure_citations(self) -> List[ErrorInstance]:
        """Check #1: Every figure is cited in text."""
        errors = []
        
        # Extract defined figures (captions)
        figure_pattern = r'Figure\s+(\d+)'
        defined_figures = set()
        for match in re.finditer(figure_pattern, self.full_text, re.IGNORECASE):
            defined_figures.add(int(match.group(1)))
        
        # Extract cited figures
        cite_patterns = [
            r'Figure\s+(\d+)',
            r'Fig\.?\s*(\d+)',
            r'figure\s+(\d+)'
        ]
        cited_figures = set()
        for pattern in cite_patterns:
            for match in re.finditer(pattern, self.full_text):
                cited_figures.add(int(match.group(1)))
        
        # Find uncited figures
        uncited = defined_figures - cited_figures
        
        for fig_num in sorted(uncited):
            # Find the figure caption location
            for line_text, line_bbox, page_num in self.line_info:
                if re.search(rf'Figure\s+{fig_num}\b', line_text, re.IGNORECASE):
                    errors.append(ErrorInstance(
                        check_id=1,
                        check_name="Figure Not Cited in Text",
                        description=f"Figure {fig_num} is defined but never cited in the text",
                        page_num=page_num,
                        text=f"Figure {fig_num}",
                        bbox=line_bbox,
                        error_type="figure_citation"
                    ))
                    break
        
        return errors
    
    def _check_table_citations(self) -> List[ErrorInstance]:
        """Check #2: Every table is cited in text."""
        errors = []
        
        # Extract defined tables
        table_pattern = r'Table\s+(\d+)'
        defined_tables = set()
        for match in re.finditer(table_pattern, self.full_text, re.IGNORECASE):
            defined_tables.add(int(match.group(1)))
        
        # Extract cited tables
        cited_tables = set()
        for match in re.finditer(table_pattern, self.full_text):
            cited_tables.add(int(match.group(1)))
        
        # Find uncited tables
        uncited = defined_tables - cited_tables
        
        for table_num in sorted(uncited):
            for line_text, line_bbox, page_num in self.line_info:
                if re.search(rf'Table\s+{table_num}\b', line_text, re.IGNORECASE):
                    errors.append(ErrorInstance(
                        check_id=2,
                        check_name="Table Not Cited in Text",
                        description=f"Table {table_num} is defined but never cited in the text",
                        page_num=page_num,
                        text=f"Table {table_num}",
                        bbox=line_bbox,
                        error_type="table_citation"
                    ))
                    break
        
        return errors
    
    def _check_figure_numbering(self) -> List[ErrorInstance]:
        """Check #5: Sequential numbering of figures."""
        errors = []
        
        # Extract all figure numbers
        figure_numbers = []
        for match in re.finditer(r'Figure\s+(\d+)', self.full_text, re.IGNORECASE):
            figure_numbers.append(int(match.group(1)))
        
        if not figure_numbers:
            return errors
        
        # Remove duplicates and sort
        unique_figures = sorted(set(figure_numbers))
        max_fig = max(unique_figures)
        expected = list(range(1, max_fig + 1))
        
        # Find missing numbers
        missing = set(expected) - set(unique_figures)
        
        if missing:
            # Find first occurrence of any figure to report error
            for line_text, line_bbox, page_num in self.line_info:
                if re.search(r'Figure\s+\d+', line_text, re.IGNORECASE):
                    errors.append(ErrorInstance(
                        check_id=5,
                        check_name="Non-Sequential Figure Numbering",
                        description=f"Figure numbering is not sequential. Missing: {sorted(missing)}",
                        page_num=page_num,
                        text=line_text[:50],
                        bbox=line_bbox,
                        error_type="figure_numbering"
                    ))
                    break
        
        return errors
    
    def _check_table_numbering(self) -> List[ErrorInstance]:
        """Check #5: Sequential numbering of tables."""
        errors = []
        
        # Extract all table numbers
        table_numbers = []
        for match in re.finditer(r'Table\s+(\d+)', self.full_text, re.IGNORECASE):
            table_numbers.append(int(match.group(1)))
        
        if not table_numbers:
            return errors
        
        # Remove duplicates and sort
        unique_tables = sorted(set(table_numbers))
        max_table = max(unique_tables)
        expected = list(range(1, max_table + 1))
        
        # Find missing numbers
        missing = set(expected) - set(unique_tables)
        
        if missing:
            for line_text, line_bbox, page_num in self.line_info:
                if re.search(r'Table\s+\d+', line_text, re.IGNORECASE):
                    errors.append(ErrorInstance(
                        check_id=5,
                        check_name="Non-Sequential Table Numbering",
                        description=f"Table numbering is not sequential. Missing: {sorted(missing)}",
                        page_num=page_num,
                        text=line_text[:50],
                        bbox=line_bbox,
                        error_type="table_numbering"
                    ))
                    break
        
        return errors
    
    # ========== EQUATIONS ==========
    
    def _check_equation_numbering(self) -> List[ErrorInstance]:
        """Check #9: Equations numbered consecutively."""
        errors = []
        
        # Extract equation numbers from lines that are likely equations
        eq_numbers = []
        eq_locations = {}
        
        for line_text, line_bbox, page_num in self.line_info:
            # Check if this line is likely an equation
            if self._is_likely_equation(line_text):
                # Look for equation number at end: (1), (2), etc.
                match = re.search(r'\((\d+)\)\s*$', line_text)
                if match:
                    eq_num = int(match.group(1))
                    eq_numbers.append(eq_num)
                    eq_locations[eq_num] = (line_text, line_bbox, page_num)
        
        if len(eq_numbers) < 2:
            return errors
        
        # Remove duplicates and sort
        unique_eq_nums = sorted(set(eq_numbers))
        
        # Check if sequential
        for i in range(len(unique_eq_nums) - 1):
            if unique_eq_nums[i+1] != unique_eq_nums[i] + 1:
                # Non-sequential found
                if unique_eq_nums[i+1] in eq_locations:
                    line_text, line_bbox, page_num = eq_locations[unique_eq_nums[i+1]]
                    errors.append(ErrorInstance(
                        check_id=9,
                        check_name="Non-Sequential Equation Numbering",
                        description=f"Equation ({unique_eq_nums[i+1]}) does not follow ({unique_eq_nums[i]}) sequentially",
                        page_num=page_num,
                        text=f"({unique_eq_nums[i+1]})",
                        bbox=line_bbox,
                        error_type="equation_numbering"
                    ))
                break
        
        return errors
    
    def _check_equation_parentheses(self) -> List[ErrorInstance]:
        """Check #10: Equation numbers in parentheses."""
        errors = []
        
        # Look for lines that are likely equations but have numbers without parentheses
        for line_text, line_bbox, page_num in self.line_info:
            # Use heuristic to identify equations
            if self._is_likely_equation(line_text):
                # Check if it has a number at the end but NOT in parentheses
                # Pattern: ends with number but no (n) format
                if re.search(r'\d+\s*$', line_text) and not re.search(r'\(\d+\)\s*$', line_text):
                    match = re.search(r'(\d+)\s*$', line_text)
                    if match:
                        errors.append(ErrorInstance(
                            check_id=10,
                            check_name="Equation Number Not in Parentheses",
                            description="Equation numbers should be wrapped in parentheses like (1), not just 1",
                            page_num=page_num,
                            text=match.group(1),
                            bbox=line_bbox,
                            error_type="equation_format"
                        ))
        
        return errors
    
    def _check_equation_references(self) -> List[ErrorInstance]:
        """Check #11: Every equation referenced in text."""
        errors = []
        
        # Extract defined equation numbers
        defined_equations = set()
        for match in re.finditer(r'\((\d+)\)', self.full_text):
            defined_equations.add(int(match.group(1)))
        
        # Extract equation references
        ref_patterns = [
            r'Eq\.?\s*\((\d+)\)',
            r'equation\s*\((\d+)\)',
            r'Equation\s*\((\d+)\)'
        ]
        referenced_equations = set()
        for pattern in ref_patterns:
            for match in re.finditer(pattern, self.full_text, re.IGNORECASE):
                referenced_equations.add(int(match.group(1)))
        
        # Find unreferenced equations
        unreferenced = defined_equations - referenced_equations
        
        for eq_num in sorted(unreferenced):
            for line_text, line_bbox, page_num in self.line_info:
                if f'({eq_num})' in line_text:
                    errors.append(ErrorInstance(
                        check_id=11,
                        check_name="Equation Not Referenced in Text",
                        description=f"Equation ({eq_num}) is never referenced in the text",
                        page_num=page_num,
                        text=f"({eq_num})",
                        bbox=line_bbox,
                        error_type="equation_reference"
                    ))
                    break
        
        return errors
    
    # ========== CITATIONS ==========
    
    def _check_citation_style_consistency(self) -> List[ErrorInstance]:
        """Check #16: Citation style consistency (IEEE vs APA)."""
        errors = []
        
        # Detect citation styles
        ieee_pattern = r'\[\d+\]'
        apa_pattern = r'\([A-Za-z]+,\s*\d{4}\)'
        
        ieee_count = len(re.findall(ieee_pattern, self.full_text))
        apa_count = len(re.findall(apa_pattern, self.full_text))
        
        # If both styles present, flag inconsistency
        if ieee_count > 0 and apa_count > 0:
            # Find first APA citation
            for line_text, line_bbox, page_num in self.line_info:
                if re.search(apa_pattern, line_text):
                    errors.append(ErrorInstance(
                        check_id=16,
                        check_name="Inconsistent Citation Style",
                        description=f"Mixed citation styles detected: {ieee_count} IEEE-style [n] and {apa_count} APA-style (Author, Year)",
                        page_num=page_num,
                        text=line_text[:50],
                        bbox=line_bbox,
                        error_type="citation_style"
                    ))
                    break
        
        return errors
    
    def _check_citation_reference_match(self) -> List[ErrorInstance]:
        """Check #18: 1:1 match between citations and reference list."""
        errors = []
        
        # Extract cited numbers [1], [2], etc.
        cited_numbers = set()
        for match in re.finditer(r'\[(\d+)\]', self.full_text):
            cited_numbers.add(int(match.group(1)))
        
        # Extract reference list numbers
        reference_numbers = set()
        in_references = False
        for line_text, line_bbox, page_num in self.line_info:
            # Detect references section
            if re.search(r'\b(References|REFERENCES|Bibliography|BIBLIOGRAPHY)\b', line_text):
                in_references = True
                continue
            
            if in_references:
                # Match [1] or 1. at start of line
                match = re.match(r'^\s*[\[\(]?(\d+)[\]\)]?\.?\s+', line_text)
                if match:
                    reference_numbers.add(int(match.group(1)))
        
        # Find citations with no reference
        missing_refs = cited_numbers - reference_numbers
        if missing_refs:
            for num in sorted(missing_refs):
                # Find first occurrence
                for line_text, line_bbox, page_num in self.line_info:
                    if f'[{num}]' in line_text:
                        errors.append(ErrorInstance(
                            check_id=18,
                            check_name="Citation Missing from References",
                            description=f"Citation [{num}] appears in text but not in reference list",
                            page_num=page_num,
                            text=f"[{num}]",
                            bbox=line_bbox,
                            error_type="citation_mismatch"
                        ))
                        break
        
        return errors
    
    def _check_uncited_references(self) -> List[ErrorInstance]:
        """Check #19: References not cited in text."""
        errors = []
        
        # Extract cited numbers
        cited_numbers = set()
        for match in re.finditer(r'\[(\d+)\]', self.full_text):
            cited_numbers.add(int(match.group(1)))
        
        # Extract reference list numbers
        reference_numbers = set()
        reference_locations = {}
        in_references = False
        
        for line_text, line_bbox, page_num in self.line_info:
            if re.search(r'\b(References|REFERENCES|Bibliography)\b', line_text):
                in_references = True
                continue
            
            if in_references:
                match = re.match(r'^\s*[\[\(]?(\d+)[\]\)]?\.?\s+', line_text)
                if match:
                    num = int(match.group(1))
                    reference_numbers.add(num)
                    reference_locations[num] = (line_text, line_bbox, page_num)
        
        # Find uncited references
        # uncited = reference_numbers - cited_numbers
        # for num in sorted(uncited):
        #     if num in reference_locations:
        #         line_text, line_bbox, page_num = reference_locations[num]
        #         errors.append(ErrorInstance(
        #             check_id=19,
        #             check_name="Uncited Reference",
        #             description=f"Reference [{num}] is listed but never cited in the text",
        #             page_num=page_num,
        #             text=line_text[:60],
        #             bbox=line_bbox,
        #             error_type="uncited_reference"
        #         ))
        
        return errors
    
    def _check_reference_order(self) -> List[ErrorInstance]:
        """Check #20: References ordered correctly (IEEE style)."""
        errors = []
        
        reference_numbers = []
        reference_locations = []
        in_references = False
        
        for line_text, line_bbox, page_num in self.line_info:
            if re.search(r'\b(References|REFERENCES)\b', line_text):
                in_references = True
                continue
            
            if in_references:
                match = re.match(r'^\s*[\[\(]?(\d+)[\]\)]?\.?\s+', line_text)
                if match:
                    num = int(match.group(1))
                    reference_numbers.append(num)
                    reference_locations.append((line_text, line_bbox, page_num))
        
        # Check if in ascending order
        if reference_numbers != sorted(reference_numbers):
            # Find first out-of-order reference
            for i in range(len(reference_numbers) - 1):
                if reference_numbers[i] > reference_numbers[i+1]:
                    line_text, line_bbox, page_num = reference_locations[i+1]
                    errors.append(ErrorInstance(
                        check_id=20,
                        check_name="References Not in Order",
                        description=f"Reference [{reference_numbers[i+1]}] appears after [{reference_numbers[i]}] - should be in ascending order",
                        page_num=page_num,
                        text=line_text[:50],
                        bbox=line_bbox,
                        error_type="reference_order"
                    ))
                    break
        
        return errors
    
    def _check_doi_in_references(self) -> List[ErrorInstance]:
        """Check #22: DOI included in references."""
        errors = []
        
        doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
        in_references = False
        
        for line_text, line_bbox, page_num in self.line_info:
            if re.search(r'\b(References|REFERENCES)\b', line_text):
                in_references = True
                continue
            
            if in_references:
                # Check if this looks like a reference entry
                if re.match(r'^\s*[\[\(]?\d+[\]\)]?\.?\s+', line_text):
                    # Check if it has journal indicators
                    has_journal = bool(re.search(r'\b(vol\.|volume|pp\.|pages|no\.|number|journal)\b', line_text, re.IGNORECASE))
                    has_doi = bool(re.search(doi_pattern, line_text, re.IGNORECASE))
                    
                    if has_journal and not has_doi:
                        errors.append(ErrorInstance(
                            check_id=22,
                            check_name="Missing DOI in Reference",
                            description="Journal reference is missing a DOI",
                            page_num=page_num,
                            text=line_text[:60],
                            bbox=line_bbox,
                            error_type="missing_doi"
                        ))
        
        return errors
    
    def _check_url_format(self) -> List[ErrorInstance]:
        """Check #24: URL format validity."""
        errors = []
        
        url_pattern = r'https?://[^\s]+'
        
        for line_text, line_bbox, page_num in self.line_info:
            matches = re.finditer(url_pattern, line_text)
            for match in matches:
                url = match.group()
                # Check for common URL issues
                if url.endswith('.') or url.endswith(','):
                    errors.append(ErrorInstance(
                        check_id=24,
                        check_name="Malformed URL",
                        description="URL appears to include trailing punctuation",
                        page_num=page_num,
                        text=url[:50],
                        bbox=line_bbox,
                        error_type="url_format"
                    ))
        
        return errors
    
    # ========== ACRONYMS ==========
    
    def _check_acronym_definitions(self) -> List[ErrorInstance]:
        """Check #26: Acronyms defined at first occurrence."""
        errors = []
        
        # Find all acronyms (2+ consecutive capital letters)
        acronym_pattern = r'\b[A-Z]{2,}\b'
        defined_pattern = r'\([A-Z]{2,}\)'  # Acronym in parentheses indicates definition
        
        # Get defined acronyms
        defined_acronyms = set()
        for match in re.finditer(defined_pattern, self.full_text):
            acronym = match.group()[1:-1]  # Remove parentheses
            defined_acronyms.add(acronym)
        
        # Check all acronyms
        checked_acronyms = set()
        common_acronyms = {'USA', 'UK', 'EU', 'UN', 'IEEE', 'ACM', 'PDF', 'HTML', 'XML', 'JSON', 'API', 'USB', 'CPU', 'GPU', 'RAM', 'ROM', 'HTTP', 'HTTPS', 'FTP', 'DNS', 'IP', 'TCP', 'UDP'}
        
        for line_text, line_bbox, page_num in self.line_info:
            matches = re.finditer(acronym_pattern, line_text)
            for match in matches:
                acronym = match.group()
                
                # Skip if already checked or common
                if acronym in checked_acronyms or acronym in common_acronyms:
                    continue
                
                checked_acronyms.add(acronym)
                
                # Check if defined
                if acronym not in defined_acronyms:
                    errors.append(ErrorInstance(
                        check_id=26,
                        check_name="Undefined Acronym",
                        description=f"Acronym '{acronym}' used without definition (should be: Full Name ({acronym}))",
                        page_num=page_num,
                        text=acronym,
                        bbox=line_bbox,
                        error_type="undefined_acronym"
                    ))
        
        return errors
    
    # ========== LINE-LEVEL CHECKS ==========
    
    def _check_line(self, text: str, bbox: Tuple, page_num: int) -> List[ErrorInstance]:
        """Check a single line for formatting errors."""
        errors = []
        
        # Check #27: Space before unit
        unit_pattern = r'\b(\d+(?:\.\d+)?)(kg|g|mg|μg|m|cm|mm|μm|km|s|ms|μs|min|h|Hz|kHz|MHz|GHz|V|mV|A|mA|W|mW|kW|MW|°C|°F|K|Pa|kPa|MPa|GPa|N|J|kJ|MJ|mol|L|mL|μL|%)\b'
        for match in re.finditer(unit_pattern, text):
            errors.append(ErrorInstance(
                check_id=27,
                check_name="Missing Space Before Unit",
                description="Number and unit should be separated by a non-breaking space",
                page_num=page_num,
                text=match.group(),
                bbox=self._calculate_match_bbox(text, match, bbox),
                error_type="unit_spacing"
            ))
        
        # Check #28: En-dash for numeric ranges
        hyphen_range_pattern = r'\b(\d+)\s*-\s*(\d+)\b'
        for match in re.finditer(hyphen_range_pattern, text):
            # Exclude years like 2020-2021
            num1 = int(match.group(1))
            num2 = int(match.group(2))
            if not (num1 > 1900 and num2 > 1900 and abs(num2 - num1) <= 10):
                errors.append(ErrorInstance(
                    check_id=28,
                    check_name="Hyphen in Numeric Range",
                    description="Use en-dash (–) instead of hyphen (-) for numeric ranges",
                    page_num=page_num,
                    text=match.group(),
                    bbox=self._calculate_match_bbox(text, match, bbox),
                    error_type="dash_usage"
                ))
        
        # Check #29: Spacing after comma/period
        # Missing space after comma (unless comma is last character in line)
        comma_pattern = r',(?![,\s\d)])'
        for match in re.finditer(comma_pattern, text):
            # Skip if comma is at the end of the line (line break)
            if match.end() >= len(text.strip()):
                continue
            
            errors.append(ErrorInstance(
                check_id=29,
                check_name="Missing Space After Comma",
                description="Comma should be followed by a space",
                page_num=page_num,
                text=match.group() + text[match.end():match.end()+3] if match.end() < len(text) else match.group(),
                bbox=self._calculate_match_bbox(text, match, bbox),
                error_type="punctuation_spacing"
            ))
        
        # Missing space after period (between words)
        period_pattern = r'\.(?=[A-Z][a-z])'
        for match in re.finditer(period_pattern, text):
            errors.append(ErrorInstance(
                check_id=29,
                check_name="Missing Space After Period",
                description="Period should be followed by a space",
                page_num=page_num,
                text=match.group() + text[match.end():match.end()+5] if match.end() < len(text) else match.group(),
                bbox=self._calculate_match_bbox(text, match, bbox),
                error_type="punctuation_spacing"
            ))
        
        # Check #17: Punctuation before citation
        punct_citation_pattern = r'[.,;:]\s*\[\d+\]'
        for match in re.finditer(punct_citation_pattern, text):
            errors.append(ErrorInstance(
                check_id=17,
                check_name="Punctuation Before Citation",
                description="Punctuation should come after citation bracket, not before",
                page_num=page_num,
                text=match.group(),
                bbox=self._calculate_match_bbox(text, match, bbox),
                error_type="citation_punctuation"
            ))
        
        # Check #15: Proper punctuation after equations
        # Use heuristic scoring to identify equations
        if self._is_likely_equation(text):
            # Check if it's missing punctuation
            if not re.search(r'[.,;:]\s*$', text.strip()):
                errors.append(ErrorInstance(
                    check_id=15,
                    check_name="Missing Punctuation After Equation",
                    description="Displayed equations should be followed by punctuation (. or ,)",
                    page_num=page_num,
                    text=text.strip()[-50:] if len(text.strip()) > 50 else text.strip(),
                    bbox=bbox,
                    error_type="equation_punctuation"
                ))
        
        return errors
    
    def _is_likely_equation(self, text: str) -> bool:
        """
        Use heuristic scoring to determine if a line is likely an equation.
        
        Scoring system:
        - Math operators: +2
        - Single variables: +2
        - Equation number at end: +5
        - Missing punctuation: +1
        - Common words present: -3
        
        Threshold: score >= 4 means likely equation
        """
        score = 0
        line = text.strip()
        
        # Empty or very short lines
        if len(line) < 3:
            return False
        
        # 1. Has mathematical operators (+2)
        if re.search(r'[=+\*^×÷≤≥≈≠∑∫∂∇√∏∆λμπσΩαβγδεθ]', line):
            score += 2
        
        # 2. Has single-letter variables (common in equations) (+2)
        # Look for standalone letters like "x", "y", "a", "b" that are likely variables
        if re.search(r'\b[a-zA-Z]\b', line):
            score += 2
        
        # 3. Has equation number at end like (1), (2), etc. (+5)
        if re.search(r'\(\d+\)\s*$', line):
            score += 5

        
        # 5. Has subscripts/superscripts notation (common in equations) (+2)
        if re.search(r'[_^]\{?\w+\}?|\w+_\d+|\w+\^\d+', line):
            score += 2
        
        # 6. Has Greek letters or special symbols (+1)
        if re.search(r'[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]', line):
            score += 1
        
        # 7. Has fractions or parentheses grouping (common in math) (+1)
        if re.search(r'\([^)]+\).*[=+\-*/]|[=+\-*/].*\([^)]+\)', line):
            score += 1
        
        # PENALTIES:
        
        # 1. Contains many common English words (-3)
        common_words = len(re.findall(r'\b(the|and|is|of|in|to|for|with|this|that|are|was|were|be|been|being|have|has|had|do|does|did|will|would|should|could|can|may|might)\b', line.lower()))
        if common_words > 2:
            score -= 3
        
        # 2. Starts with common sentence starters (-2)
        if re.match(r'^(The|This|That|These|Those|In|For|However|Therefore|Thus|Hence)\b', line):
            score -= 2
        
        # 3. Too long to be a typical equation (>150 chars) (-1)
        if len(line) > 150:
            score -= 1
        
        # 4. Is a numbered list item like "(1) First item" (-4)
        if re.match(r'^\(\d+\)\s+[A-Z][a-z]+', line):
            score -= 4
        
        # 5. Contains many words relative to math symbols (-2)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', line)
        math_symbols = re.findall(r'[=+\-*/^×÷≤≥≈≠∑∫∂∇√]', line)
        if len(words) > 5 and len(math_symbols) < 2:
            score -= 2
        
        # Threshold: score >= 4 indicates likely equation
        return score >= 4
    
    def _calculate_match_bbox(self, full_text: str, match, line_bbox: Tuple) -> Tuple:
        """Calculate the bounding box for a regex match within a line."""
        start_pos = match.start()
        end_pos = match.end()
        text_length = len(full_text)
        
        if text_length == 0:
            return line_bbox
        
        # Approximate position within the line
        x0, y0, x1, y1 = line_bbox
        width = x1 - x0
        
        # Calculate approximate x positions
        char_width = width / text_length if text_length > 0 else width
        match_x0 = x0 + (start_pos * char_width)
        match_x1 = x0 + (end_pos * char_width)
        
        # Add padding
        padding = 2
        return (
            max(x0, match_x0 - padding),
            y0 - padding,
            min(x1, match_x1 + padding),
            y1 + padding
        )
    
    def annotate_pdf(self, doc: fitz.Document, errors: List[ErrorInstance], output_path: str):
        """Annotate the PDF with highlights at error locations."""
        # Color coding for different error types
        color_map = {
            "figure_citation": (1, 0.9, 0.7),
            "table_citation": (1, 0.9, 0.7),
            "figure_numbering": (1, 0.85, 0.6),
            "table_numbering": (1, 0.85, 0.6),
            "equation_numbering": (0.9, 0.85, 1),
            "equation_format": (0.9, 0.85, 1),
            "equation_reference": (0.9, 0.85, 1),
            "equation_punctuation": (1, 0.8, 1),
            "citation_style": (1, 0.7, 0.7),
            "citation_punctuation": (1, 0.8, 0.8),
            "citation_mismatch": (1, 0.7, 0.7),
            "uncited_reference": (0.9, 1, 0.9),
            "reference_order": (0.95, 0.95, 0.7),
            "missing_doi": (0.9, 1, 0.9),
            "url_format": (0.85, 0.95, 1),
            "undefined_acronym": (1, 0.95, 0.8),
            "unit_spacing": (0.8, 0.9, 1),
            "dash_usage": (1, 1, 0.6),
            "punctuation_spacing": (1, 0.9, 0.7)
        }
        
        for error in errors:
            page = doc[error.page_num]
            
            # Get color for this error type
            color = color_map.get(error.error_type, (1, 1, 0))
            
            # Add highlight annotation
            highlight = page.add_highlight_annot(error.bbox)
            highlight.set_colors(stroke=color)
            highlight.set_opacity(0.5)
            
            # Add comment with error description
            highlight.info["title"] = f"Check #{error.check_id}: {error.check_name}"
            highlight.info["content"] = f"{error.description}\n\nFound: '{error.text}'"
            highlight.update()
        
        # Save the annotated PDF
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()


def process_pdf(input_path: str, output_path: str) -> Tuple[List[ErrorInstance], str, Dict]:
    """
    Main function to process a PDF: detect errors and create annotated version.
    
    Returns:
        Tuple of (list of errors, path to annotated PDF, statistics dictionary)
    """
    detector = PDFErrorDetector()
    errors, doc, statistics = detector.detect_errors(input_path)
    detector.annotate_pdf(doc, errors, output_path)
    
    return errors, output_path, statistics
