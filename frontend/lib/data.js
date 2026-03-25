export const ALL_SECTIONS = [
  "Abstract",
  "Index Terms",
  "Introduction",
  "Related Work",
  "Background",
  "Methodology",
  "System Design",
  "Implementation",
  "Experiments",
  "Results",
  "Evaluation",
  "Discussion",
  "Conclusion",
  "Future Work",
  "Acknowledgments",
  "References",
];

export const AVAILABLE_CHECKS = {
  metadata_completeness: {
    name: "Metadata Completeness",
    description: "Title, authors, and publication date are present",
    category: "Metadata",
    error_types: ["metadata_incomplete"],
    default: true,
  },
  abstract_exists: {
    name: "Abstract Section Exists",
    description: "Paper contains an Abstract section",
    category: "Structure",
    error_types: ["missing_abstract"],
    default: true,
  },
  abstract_word_count: {
    name: "Abstract Word Count (150–250 words)",
    description: "Abstract must be between 150 and 250 words",
    category: "Structure",
    error_types: ["abstract_word_count"],
    default: true,
  },
  index_terms: {
    name: "Index Terms / Keywords",
    description: "Paper contains an Index Terms or Keywords section",
    category: "Structure",
    error_types: ["missing_index_terms"],
    default: true,
  },
  references_section: {
    name: "References Section Exists",
    description: "Paper contains a References section",
    category: "Structure",
    error_types: ["missing_references"],
    default: true,
  },
  roman_numeral_headings: {
    name: "Roman Numeral Section Headings",
    description: "Section headings use Roman numerals (e.g. I. INTRODUCTION)",
    category: "Structure",
    error_types: ["non_roman_heading"],
    default: true,
  },
  introduction_section: {
    name: "Introduction Section (I. INTRODUCTION)",
    description: "Paper has a correctly formatted Introduction section",
    category: "Structure",
    error_types: ["missing_introduction"],
    default: true,
  },
  figure_label_format: {
    name: "Figure Label Format (Fig. N / Figure N)",
    description: "Figures use 'Fig. N' or 'Figure N' convention",
    category: "Numbering",
    error_types: ["invalid_figure_label"],
    default: true,
  },
  table_label_format: {
    name: "Table Label Format (TABLE I)",
    description: "Tables use 'TABLE' all-caps with Roman numerals",
    category: "Numbering",
    error_types: ["invalid_table_numbering"],
    default: true,
  },
  equation_numbering: {
    name: "Equation Numbering (1), (2), ...",
    description: "Equations numbered sequentially in parentheses",
    category: "Numbering",
    error_types: ["equation_numbering"],
    default: true,
  },
  figure_sequential: {
    name: "Sequential Figure Numbering",
    description: "Figures numbered 1, 2, 3, ... with no gaps",
    category: "Numbering",
    error_types: ["figure_numbering_sequence"],
    default: true,
  },
  table_sequential: {
    name: "Sequential Table Numbering",
    description: "Tables numbered sequentially with no gaps",
    category: "Numbering",
    error_types: ["table_numbering_sequence"],
    default: true,
  },
  reference_sequential: {
    name: "Sequential Reference Numbering [1],[2],[3]",
    description: "References numbered [1],[2],[3],... with no gaps",
    category: "Numbering",
    error_types: ["reference_numbering_sequence"],
    default: true,
  },
  caption_placement: {
    name: "Caption Placement (Fig below / Table above)",
    description: "Figure captions below figures; table captions above tables",
    category: "Formatting",
    error_types: ["caption_placement"],
    default: true,
  },
  reference_format: {
    name: "Reference Format [n] Author, Title, ...",
    description: "References formatted as [1] Author, Title, ...",
    category: "References",
    error_types: ["non_ieee_reference_format"],
    default: true,
  },
  url_doi_validity: {
    name: "URL & DOI Validity",
    description: "URLs and DOIs are well-formed and unbroken",
    category: "References",
    error_types: ["broken_url", "broken_doi"],
    default: true,
  },
  repeated_words: {
    name: "Repeated Words",
    description: "Consecutive repeated words (e.g. 'the the')",
    category: "Writing",
    error_types: ["repeated_word"],
    default: false,
  },
  et_al_formatting: {
    name: "et al. Formatting",
    description: "Correct usage: 'et al.' with period after 'al'",
    category: "Writing",
    error_types: ["citation_format"],
    default: true,
  },
  first_person_pronouns: {
    name: "First-Person Pronouns (I, we, our)",
    description: "Flags first-person pronouns in academic text",
    category: "Writing",
    error_types: ["writing_style"],
    default: false,
  },
};

export function getChecksByCategory() {
  const map = {};
  for (const [id, info] of Object.entries(AVAILABLE_CHECKS)) {
    const cat = info.category;
    if (!map[cat]) map[cat] = [];
    map[cat].push({ id, ...info });
  }
  return map;
}

export function getCheckNamesByCategory() {
  const map = {};
  for (const info of Object.values(AVAILABLE_CHECKS)) {
    const cat = info.category;
    if (!map[cat]) map[cat] = [];
    map[cat].push(info.name);
  }
  return map;
}

export async function fetchFormats() {
  // Call same-origin endpoints; Next.js rewrites proxy to Flask.
  const res = await fetch(`/api/formats`);
  if (!res.ok) return [];
  return res.json();
}

export async function createFormat(payload) {
  const res = await fetch(`/api/formats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let message = "Failed to save format";
    try {
      const err = await res.json();
      message = err.error || message;
    } catch (_) {
      const text = await res.text().catch(() => "");
      if (text) message = text;
    }
    throw new Error(message);
  }
  return res.json();
}

export async function deleteFormat(id) {
  const res = await fetch(`/api/formats/${id}`, { method: "DELETE" });
  if (!res.ok) {
    let message = "Delete failed";
    try {
      const err = await res.json();
      message = err.error || message;
    } catch (_) {
      const text = await res.text().catch(() => "");
      if (text) message = text;
    }
    throw new Error(message);
  }
  return res.json();
}

export async function uploadPDF(file, formatId) {
  const form = new FormData();
  form.append("file", file);
  if (formatId) form.append("format_id", formatId);
  const res = await fetch(`/upload`, { method: "POST", body: form });
  if (!res.ok) {
    let message = "Upload failed";
    try {
      const err = await res.json();
      message = err.error || message;
    } catch (_) {
      const text = await res.text().catch(() => "");
      // Avoid crashing on HTML error pages.
      if (text) message = text.slice(0, 300);
    }
    throw new Error(message);
  }
  return res.json();
}

export function downloadURL(jobId) {
  return `/download/${jobId}`;
}

export const ERROR_DESCRIPTIONS = {
  metadata_incomplete: "Missing title, author(s), or publication date",
  abstract_word_count: "Abstract outside 150–250 word range",
  missing_required_section: "A mandatory section is missing from the document",
  missing_abstract: "Missing Abstract section",
  missing_index_terms: "Missing Index Terms section",
  missing_references: "Missing References section",
  non_roman_heading: "Non-Roman numeral section heading",
  missing_introduction: "Missing or misformatted Introduction",
  invalid_figure_label: "Incorrect figure label format",
  invalid_table_numbering: "Incorrect table numbering format",
  equation_numbering: "Equation numbering issues",
  figure_numbering_sequence: "Non-sequential figure numbering",
  table_numbering_sequence: "Non-sequential table numbering",
  reference_numbering_sequence: "Non-sequential reference numbering",
  caption_placement: "Incorrect caption placement",
  broken_url: "Broken or malformed URL",
  broken_doi: "Broken or malformed DOI",
  spacing_error: "Multiple consecutive spaces",
  punctuation_spacing: "Punctuation spacing issues",
  repeated_word: "Repeated consecutive words",
  punctuation_error: "Multiple punctuation marks",
  whitespace_error: "Trailing whitespace",
  citation_format: "Incorrect et al. formatting",
  writing_style: "First-person pronouns",
  non_ieee_reference_format: "Reference format issues",
};
