// Main JavaScript for Research Paper Error Checker

let currentJobId = null;
let allErrors = [];

// DOM Elements (will be initialized after DOM loads)
let uploadSection, processingSection, resultsSection, uploadArea, fileInput, browseBtn, downloadBtn, newUploadBtn;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Research Paper Error Checker - JavaScript loaded');
    
    // Initialize DOM elements
    uploadSection = document.getElementById('upload-section');
    processingSection = document.getElementById('processing-section');
    resultsSection = document.getElementById('results-section');
    uploadArea = document.getElementById('upload-area');
    fileInput = document.getElementById('file-input');
    browseBtn = document.getElementById('browse-btn');
    downloadBtn = document.getElementById('download-btn');
    newUploadBtn = document.getElementById('new-upload-btn');
    
    console.log('DOM elements:', {
        uploadSection: !!uploadSection,
        processingSection: !!processingSection,
        resultsSection: !!resultsSection,
        uploadArea: !!uploadArea,
        fileInput: !!fileInput,
        browseBtn: !!browseBtn
    });
    setupEventListeners();
    console.log('Event listeners setup complete');
});

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Browse button
    browseBtn.addEventListener('click', (e) => {
        console.log('Browse button clicked');
        e.preventDefault();
        e.stopPropagation();
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        console.log('File input changed, files:', e.target.files);
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
    
    // Drag and drop
    uploadArea.addEventListener('click', (e) => {
        console.log('Upload area clicked');
        // Don't trigger if clicking the browse button
        if (e.target !== browseBtn && !browseBtn.contains(e.target)) {
            fileInput.click();
        }
    });
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
        console.log('Drag over upload area');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
        console.log('Drag leave upload area');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        console.log('File dropped, files:', e.dataTransfer.files);
        
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
    
    // Download button
    downloadBtn.addEventListener('click', () => {
        console.log('Download button clicked, job_id:', currentJobId);
        if (currentJobId) {
            window.location.href = `/download/${currentJobId}`;
        }
    });
    
    // New upload button
    newUploadBtn.addEventListener('click', () => {
        console.log('New upload button clicked');
        resetApp();
    });
    
    // Filter buttons
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('filter-btn')) {
            console.log('Filter button clicked:', e.target.getAttribute('data-filter'));
            handleFilterClick(e.target);
        }
    });
    
    console.log('Event listeners setup complete');
}

async function handleFileUpload(file) {
    console.log('handleFileUpload called with file:', file.name, 'size:', file.size);
    
    // Validate file
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Please upload a PDF file.');
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        alert('File size must be less than 50MB.');
        return;
    }
    
    console.log('File validation passed, showing processing section');
    
    // Show processing section
    showSection(processingSection);
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('Sending POST request to /upload');
    
    try {
        // Upload and process
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        console.log('Response received:', response.status, response.statusText);
        
        if (!response.ok) {
            const error = await response.json();
            console.error('Server error:', error);
            throw new Error(error.error || 'Upload failed');
        }
        
        const result = await response.json();
        console.log('Processing result:', result);
        
        if (result.success) {
            currentJobId = result.job_id;
            allErrors = result.errors;
            console.log('Displaying results for', allErrors.length, 'errors');
            displayResults(result);
        } else {
            throw new Error('Processing failed');
        }
        
    } catch (error) {
        console.error('Error during upload/processing:', error);
        alert(`Error: ${error.message}`);
        resetApp();
    }
}

function displayResults(result) {
    console.log('displayResults called with:', result);
    
    showSection(resultsSection);

    const totalErrorsEl = document.getElementById('total-errors');
    const pagesWithErrorsEl = document.getElementById('pages-with-errors');
    const errorTypesContainer = document.getElementById('error-types-container');
    const errorList = document.getElementById('error-list');

    console.log('Elements found:', {
        totalErrorsEl: !!totalErrorsEl,
        pagesWithErrorsEl: !!pagesWithErrorsEl,
        errorTypesContainer: !!errorTypesContainer,
        errorList: !!errorList
    });

    if (!totalErrorsEl || !pagesWithErrorsEl || !errorTypesContainer || !errorList) {
        console.error("One or more required DOM elements missing:", {
            totalErrorsEl: !!totalErrorsEl,
            pagesWithErrorsEl: !!pagesWithErrorsEl,
            errorTypesContainer: !!errorTypesContainer,
            errorList: !!errorList
        });
        return;
    }

    console.log('Setting error count to:', result.error_count);
    totalErrorsEl.textContent = result.error_count;

    const uniquePages = new Set(result.errors.map(e => e.page_num));
    console.log('Setting pages with errors to:', uniquePages.size);
    pagesWithErrorsEl.textContent = uniquePages.size;

    console.log('Displaying error types summary...');
    displayErrorTypesSummary(result.errors);
    
    console.log('Displaying error list...');
    displayErrorList(result.errors);
    
    console.log('displayResults complete!');
}

function displayErrorTypesSummary(errors) {
    const errorTypes = {};
    
    // Count errors by type
    errors.forEach(error => {
        const type = error.error_type;
        if (!errorTypes[type]) {
            errorTypes[type] = {
                count: 0,
                name: error.check_name,
                checkId: error.check_id
            };
        }
        errorTypes[type].count++;
    });
    
    // Create cards
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

function displayErrorList(errors, filter = 'all') {
    const errorList = document.getElementById('error-list');
    errorList.innerHTML = '';

    // Filter errors
    let filteredErrors;
    if (filter === 'all') {
        filteredErrors = errors;
    } else if (filter === 'numbering') {
        // Special category: includes figure, table, and equation numbering
        filteredErrors = errors.filter(e => 
            e.error_type === 'invalid_figure_label' || 
            e.error_type === 'invalid_table_numbering' || 
            e.error_type === 'equation_numbering'
        );
    } else if (filter === 'structure') {
        // Special category: includes all structure-related checks
        filteredErrors = errors.filter(e => 
            e.error_type === 'missing_abstract' ||
            e.error_type === 'missing_index_terms' ||
            e.error_type === 'missing_references' ||
            e.error_type === 'non_roman_heading' ||
            e.error_type === 'missing_introduction'
        );
    } else {
        filteredErrors = errors.filter(e => e.error_type === filter);
    }

    if (filteredErrors.length === 0) {
        errorList.innerHTML = '<p style="text-align: center; color: #666;">No errors found for this filter.</p>';
        return;
    }
    
    // Create error items
    filteredErrors.forEach(error => {
        const errorItem = document.createElement('div');
        errorItem.className = 'error-item';
        errorItem.setAttribute('data-error-type', error.error_type);
        
        errorItem.innerHTML = `
            <div class="error-item-header">
                <div class="error-title">
                    Check #${error.check_id}: ${error.check_name}
                </div>
                <div class="error-page">Page ${error.page_num}</div>
            </div>
            <div class="error-description">${error.description}</div>
            <div class="error-text">Found: "${escapeHtml(error.text)}"</div>
        `;
        
        errorList.appendChild(errorItem);
    });
}

function handleFilterClick(button) {
    // Update active state
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    button.classList.add('active');
    
    // Filter errors
    const filter = button.getAttribute('data-filter');
    displayErrorList(allErrors, filter);
}

function getErrorTypeDescription(type) {
    const descriptions = {
        // Structure checks
        'missing_abstract': 'Missing Abstract section',
        'missing_index_terms': 'Missing Index Terms section',
        'missing_references': 'Missing References section',
        'non_roman_heading': 'Non-Roman numeral section heading',
        'missing_introduction': 'Missing or misformatted Introduction',
        
        // Numbering checks
        'invalid_figure_label': 'Incorrect figure label format',
        'invalid_table_numbering': 'Incorrect table numbering',
        'equation_numbering': 'Equation numbering issues',
        
        // Typography checks
        'spacing_error': 'Multiple consecutive spaces',
        'punctuation_spacing': 'Punctuation spacing issues',
        'repeated_word': 'Repeated consecutive words',
        'punctuation_error': 'Multiple punctuation marks',
        'whitespace_error': 'Trailing whitespace',
        'citation_format': 'Incorrect et al. formatting',
        'writing_style': 'First-person pronouns',
        'non_ieee_reference_format': 'Reference format issues'
    };
    return descriptions[type] || type;
}

function showSection(section) {
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    section.classList.remove('hidden');
}

function resetApp() {
    currentJobId = null;
    allErrors = [];
    fileInput.value = '';
    showSection(uploadSection);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
