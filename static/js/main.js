// Main JavaScript for Research Paper Error Checker — Student Mode

let currentJobId = null;
let allErrors = [];

let uploadSection, processingSection, resultsSection, uploadArea,
    fileInput, browseBtn, downloadBtn, newUploadBtn, formatSelect;

document.addEventListener('DOMContentLoaded', () => {
    uploadSection = document.getElementById('upload-section');
    processingSection = document.getElementById('processing-section');
    resultsSection = document.getElementById('results-section');
    uploadArea = document.getElementById('upload-area');
    fileInput = document.getElementById('file-input');
    browseBtn = document.getElementById('browse-btn');
    downloadBtn = document.getElementById('download-btn');
    newUploadBtn = document.getElementById('new-upload-btn');
    formatSelect = document.getElementById('format-select');
    setupEventListeners();
});

function setupEventListeners() {
    browseBtn.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); fileInput.click(); });
    fileInput.addEventListener('change', (e) => { if (e.target.files.length > 0) handleFileUpload(e.target.files[0]); });
    uploadArea.addEventListener('click', (e) => { if (e.target !== browseBtn && !browseBtn.contains(e.target)) fileInput.click(); });
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', () => { uploadArea.classList.remove('dragover'); });
    uploadArea.addEventListener('drop', (e) => { e.preventDefault(); uploadArea.classList.remove('dragover'); if (e.dataTransfer.files.length > 0) handleFileUpload(e.dataTransfer.files[0]); });
    downloadBtn.addEventListener('click', () => { if (currentJobId) window.location.href = `/download/${currentJobId}`; });
    newUploadBtn.addEventListener('click', resetApp);
    document.addEventListener('click', (e) => { if (e.target.classList.contains('filter-btn')) handleFilterClick(e.target); });
}

async function handleFileUpload(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) { alert('Please upload a PDF file.'); return; }
    if (file.size > 50 * 1024 * 1024) { alert('File size must be less than 50MB.'); return; }

    showSection(processingSection);

    const formData = new FormData();
    formData.append('file', file);
    if (formatSelect && formatSelect.value) {
        formData.append('format_id', formatSelect.value);
    }

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Upload failed');
        }
        const result = await response.json();
        if (result.success) {
            currentJobId = result.job_id;
            allErrors = result.errors;
            displayResults(result);
        } else {
            throw new Error('Processing failed');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
        resetApp();
    }
}

function displayResults(result) {
    showSection(resultsSection);

    document.getElementById('total-errors').textContent = result.error_count;
    const uniquePages = new Set(result.errors.map(e => e.page_num));
    document.getElementById('pages-with-errors').textContent = uniquePages.size;

    const stats = result.statistics || {};
    const el = id => document.getElementById(id);
    if (el('total-figures')) el('total-figures').textContent = stats.total_figures || 0;
    if (el('total-tables')) el('total-tables').textContent = stats.total_tables || 0;
    if (el('total-equations')) el('total-equations').textContent = stats.total_equations || 0;

    displaySectionsStatus(result);
    displayErrorTypesSummary(result.errors);
    displayErrorList(result.errors);

    if (result.reference_analysis && !result.reference_analysis.error) {
        displayReferenceAnalysis(result.reference_analysis);
    }
}

// ── Required sections status badges ──────────────────────────────────────────

function displaySectionsStatus(result) {
    const container = document.getElementById('sections-status');
    const badges = document.getElementById('sections-badges');
    if (!container || !badges) return;

    const mandatory = result.mandatory_sections || [];
    if (mandatory.length === 0) { container.classList.add('hidden'); return; }

    const sectionErrors = new Set(
        result.errors.filter(e => e.error_type === 'missing_required_section')
                     .map(e => e.text)
    );

    badges.innerHTML = mandatory.map(sec => {
        const missing = sectionErrors.has(sec);
        return `<span class="sec-badge ${missing ? 'sec-missing' : 'sec-present'}">${missing ? '✗' : '✓'} ${sec}</span>`;
    }).join('');

    container.classList.remove('hidden');
}

// ── Error type summary cards ─────────────────────────────────────────────────

function displayErrorTypesSummary(errors) {
    const errorTypes = {};
    errors.forEach(error => {
        const type = error.error_type;
        if (!errorTypes[type]) errorTypes[type] = { count: 0, name: error.check_name, checkId: error.check_id };
        errorTypes[type].count++;
    });

    const container = document.getElementById('error-types-container');
    container.innerHTML = '';
    Object.entries(errorTypes).forEach(([type, info]) => {
        const card = document.createElement('div');
        card.className = 'error-type-card';
        card.innerHTML = `
            <div class="error-type-info">
                <h4>Check #${info.checkId}: ${info.name}</h4>
                <p>${getErrorTypeDescription(type)}</p>
            </div>
            <div class="error-type-count">${info.count}</div>
        `;
        container.appendChild(card);
    });
}

// ── Error list with filters ──────────────────────────────────────────────────

function displayErrorList(errors, filter = 'all') {
    const errorList = document.getElementById('error-list');
    errorList.innerHTML = '';

    let filtered;
    if (filter === 'all') {
        filtered = errors;
    } else if (filter === 'numbering') {
        filtered = errors.filter(e => ['invalid_figure_label','invalid_table_numbering','equation_numbering'].includes(e.error_type));
    } else if (filter === 'sequence') {
        filtered = errors.filter(e => ['figure_numbering_sequence','table_numbering_sequence','reference_numbering_sequence'].includes(e.error_type));
    } else if (filter === 'structure') {
        filtered = errors.filter(e => ['missing_abstract','missing_index_terms','missing_references','non_roman_heading','missing_introduction'].includes(e.error_type));
    } else if (filter === 'url_doi') {
        filtered = errors.filter(e => ['broken_url','broken_doi'].includes(e.error_type));
    } else {
        filtered = errors.filter(e => e.error_type === filter);
    }

    if (filtered.length === 0) {
        errorList.innerHTML = '<p style="text-align:center; color:#666;">No errors found for this filter.</p>';
        return;
    }

    filtered.forEach(error => {
        const item = document.createElement('div');
        item.className = 'error-item';
        item.setAttribute('data-error-type', error.error_type);
        item.innerHTML = `
            <div class="error-item-header">
                <div class="error-title">Check #${error.check_id}: ${error.check_name}</div>
                <div class="error-page">Page ${error.page_num}</div>
            </div>
            <div class="error-description">${error.description}</div>
            <div class="error-text">Found: "${escapeHtml(error.text)}"</div>
        `;
        errorList.appendChild(item);
    });
}

function handleFilterClick(button) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    button.classList.add('active');
    displayErrorList(allErrors, button.getAttribute('data-filter'));
}

function getErrorTypeDescription(type) {
    const desc = {
        'metadata_incomplete': 'Missing title, author(s), or publication date',
        'abstract_word_count': 'Abstract outside 150–250 word range',
        'missing_required_section': 'A mandatory section is missing from the document',
        'missing_abstract': 'Missing Abstract section',
        'missing_index_terms': 'Missing Index Terms section',
        'missing_references': 'Missing References section',
        'non_roman_heading': 'Non-Roman numeral section heading',
        'missing_introduction': 'Missing or misformatted Introduction',
        'invalid_figure_label': 'Incorrect figure label format',
        'invalid_table_numbering': 'Incorrect table numbering format',
        'equation_numbering': 'Equation numbering issues',
        'figure_numbering_sequence': 'Non-sequential figure numbering',
        'table_numbering_sequence': 'Non-sequential table numbering',
        'reference_numbering_sequence': 'Non-sequential reference numbering',
        'caption_placement': 'Incorrect caption placement',
        'broken_url': 'Broken or malformed URL',
        'broken_doi': 'Broken or malformed DOI',
        'spacing_error': 'Multiple consecutive spaces',
        'punctuation_spacing': 'Punctuation spacing issues',
        'repeated_word': 'Repeated consecutive words',
        'punctuation_error': 'Multiple punctuation marks',
        'whitespace_error': 'Trailing whitespace',
        'citation_format': 'Incorrect et al. formatting',
        'writing_style': 'First-person pronouns',
        'non_ieee_reference_format': 'Reference format issues',
    };
    return desc[type] || type;
}

// ── Reference Quality Analysis ───────────────────────────────────────────────

function displayReferenceAnalysis(data) {
    const section = document.getElementById('reference-analysis-section');
    const summaryEl = document.getElementById('ref-summary');
    const entriesEl = document.getElementById('ref-entries');
    if (!section || !summaryEl || !entriesEl) return;

    const s = data.summary || {};
    const passed = s.checks_passed || [], failed = s.checks_failed || [];
    const total = s.total || 0, parsedOk = s.parsed_ok || 0;
    const style = s.style || 'Unknown', styleConf = s.style_confidence || '';
    const totalIssues = s.total_issues || 0;
    const confClass = { HIGH:'badge-high', MEDIUM:'badge-medium', LOW:'badge-low' }[styleConf] || 'badge-medium';

    summaryEl.innerHTML = `
        <div class="ref-summary-grid">
            <div class="ref-stat-card"><span class="ref-stat-value">${total}</span><span class="ref-stat-label">References Found</span></div>
            <div class="ref-stat-card"><span class="ref-stat-value">${parsedOk}</span><span class="ref-stat-label">Parsed OK</span></div>
            <div class="ref-stat-card"><span class="ref-stat-value ref-issues-count ${totalIssues > 0 ? 'has-issues' : 'no-issues'}">${totalIssues}</span><span class="ref-stat-label">Total Issues</span></div>
            <div class="ref-stat-card"><span class="ref-stat-value">${style} <span class="badge ${confClass}">${styleConf}</span></span><span class="ref-stat-label">Detected Style</span></div>
        </div>
        <div class="ref-checks-row">
            ${passed.map(c => `<span class="check-chip pass">✓ ${c}</span>`).join('')}
            ${failed.map(c => `<span class="check-chip fail">✗ ${c}</span>`).join('')}
        </div>
        ${(data.list_level_issues && data.list_level_issues.length > 0) ? `
        <div class="ref-list-issues">
            <strong>List-level issues:</strong>
            ${data.list_level_issues.map(i => `
                <div class="list-issue-item">
                    <span class="issue-pos">[${i.position}]</span>
                    <span class="issue-detail">${i.detail || i.check}</span>
                    ${i.expected ? `<span class="issue-expected">Expected: <code>${i.expected}</code></span>` : ''}
                </div>
            `).join('')}
        </div>` : ''}
    `;

    const entries = data.entries || [];
    if (entries.length === 0) {
        entriesEl.innerHTML = '<p class="no-refs">No individual reference entries available.</p>';
    } else {
        entriesEl.innerHTML = entries.map(entry => {
            const issues = entry.issues || [];
            const parsed = entry.parsed || {};
            const entryStyle = entry.style || {};
            const hasIssues = issues.length > 0;
            const cls = hasIssues ? 'entry-has-issues' : 'entry-ok';
            const icon = hasIssues ? '⚠' : '✓';
            return `
            <details class="ref-entry ${cls}">
                <summary class="ref-entry-summary">
                    <span class="entry-icon">${icon}</span>
                    <span class="entry-id">${entry.id}</span>
                    <span class="entry-preview">${((parsed.title || entry.raw_text || '').substring(0,80))}${(parsed.title || entry.raw_text || '').length > 80 ? '…' : ''}</span>
                    <span class="entry-issue-count ${hasIssues ? 'has-issues' : ''}">${hasIssues ? issues.length + ' issue' + (issues.length > 1 ? 's' : '') : 'OK'}</span>
                </summary>
                <div class="ref-entry-body">
                    <div class="entry-raw-text"><strong>Raw:</strong> <em>${entry.raw_text || ''}</em></div>
                    ${parsed.authors && parsed.authors.length ? `<div class="entry-meta">Authors: ${parsed.authors.join(', ')}</div>` : ''}
                    ${parsed.pub_date ? `<div class="entry-meta">Year: ${parsed.pub_date}</div>` : ''}
                    ${parsed.volume ? `<div class="entry-meta">Volume: ${parsed.volume}${parsed.issue ? ', Issue: ' + parsed.issue : ''}${parsed.pages ? ', Pages: ' + parsed.pages : ''}</div>` : ''}
                    ${parsed.doi ? `<div class="entry-meta">DOI: <a href="https://doi.org/${parsed.doi}" target="_blank">${parsed.doi}</a></div>` : ''}
                    ${entryStyle.predicted ? `<div class="entry-meta">Style: ${entryStyle.predicted} (${entryStyle.confidence || ''})</div>` : ''}
                    ${issues.length > 0 ? `
                    <ul class="entry-issues-list">
                        ${issues.map(iss => `
                            <li class="entry-issue">
                                <span class="issue-type-tag">${iss.check}</span>
                                <span class="issue-field">${iss.field || ''}</span>
                                <span class="issue-text">${iss.detail}</span>
                                ${iss.suggestion ? `<div class="issue-suggestion">💡 ${iss.suggestion}</div>` : ''}
                            </li>
                        `).join('')}
                    </ul>` : '<p class="entry-ok-msg">No issues found for this reference.</p>'}
                </div>
            </details>`;
        }).join('');
    }
    section.classList.remove('hidden');
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function showSection(section) {
    [uploadSection, processingSection, resultsSection].forEach(s => { if (s) s.classList.add('hidden'); });
    section.classList.remove('hidden');
}

function resetApp() {
    currentJobId = null;
    allErrors = [];
    fileInput.value = '';
    const ref = document.getElementById('reference-analysis-section');
    if (ref) ref.classList.add('hidden');
    const secStatus = document.getElementById('sections-status');
    if (secStatus) secStatus.classList.add('hidden');
    showSection(uploadSection);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
