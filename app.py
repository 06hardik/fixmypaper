"""
Flask application for Research Paper Error Checker.
"""
import os
import uuid
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pdf_processor import process_pdf, AVAILABLE_CHECKS, ALL_SECTIONS
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

FORMATS_FILE = Path(__file__).parent / "formats.json"

processing_results = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'


def _build_document_overview(extracted_data, original_filename, statistics, error_count):
    """Build a lightweight, UI-friendly summary from extracted data."""
    full_text = (extracted_data or {}).get("full_text", "") or ""
    lines = [ln.strip() for ln in full_text.splitlines() if ln.strip()]

    title = lines[0] if lines else original_filename
    # Heuristic: use the second non-empty line if it looks like author metadata.
    authors = "Not detected"
    if len(lines) > 1 and len(lines[1]) < 140:
        authors = lines[1]

    abstract = "Not detected"
    lower_text = full_text.lower()
    abstract_idx = lower_text.find("abstract")
    if abstract_idx >= 0:
        snippet = full_text[abstract_idx: abstract_idx + 1200]
        parts = snippet.split("\n", 1)
        abstract_candidate = parts[1] if len(parts) > 1 else snippet
        abstract = " ".join(abstract_candidate.split())[:550] or "Not detected"

    stats = statistics or {}
    insights = [
        f"{error_count} formatting issue(s) detected",
        f"{stats.get('total_figures', 0)} figure(s) and {stats.get('total_tables', 0)} table(s) identified",
        f"{stats.get('total_equations', 0)} equation(s) detected",
    ]

    return {
        "title": title[:200],
        "authors": authors[:240],
        "abstract": abstract,
        "key_insights": insights,
    }


def load_formats():
    if FORMATS_FILE.exists():
        with open(FORMATS_FILE) as f:
            return json.load(f).get("formats", [])
    return []


def save_formats(formats):
    with open(FORMATS_FILE, "w") as f:
        json.dump({"formats": formats}, f, indent=2)


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    checks_by_cat = {}
    for cid, info in AVAILABLE_CHECKS.items():
        checks_by_cat.setdefault(info["category"], []).append(info["name"])
    return render_template('home.html', checks_by_cat=checks_by_cat)


@app.route('/professor')
def professor():
    checks_by_cat = {}
    for cid, info in AVAILABLE_CHECKS.items():
        checks_by_cat.setdefault(info["category"], []).append({
            "id": cid, **info,
        })
    return render_template('professor.html',
                           all_sections=ALL_SECTIONS,
                           checks_by_cat=checks_by_cat,
                           formats=load_formats())


@app.route('/student')
def student():
    return render_template('student.html', formats=load_formats())


# ── Format API ────────────────────────────────────────────────────────────────

@app.route('/api/formats', methods=['GET'])
def list_formats():
    return jsonify(load_formats())


@app.route('/api/formats', methods=['POST'])
def create_format():
    data = request.get_json(force=True)
    if not data.get('name') or not data.get('created_by'):
        return jsonify({'error': 'name and created_by are required'}), 400

    new_fmt = {
        "id":                 str(uuid.uuid4()),
        "name":               data["name"].strip(),
        "created_by":         data["created_by"].strip(),
        "is_system":          False,
        "description":        data.get("description", "").strip(),
        "mandatory_sections": data.get("mandatory_sections", []),
        "enabled_checks":     data.get("enabled_checks", []),
    }
    formats = load_formats()
    formats.append(new_fmt)
    save_formats(formats)
    return jsonify(new_fmt), 201


@app.route('/api/formats/<fmt_id>', methods=['DELETE'])
def delete_format(fmt_id):
    formats = load_formats()
    updated = [f for f in formats if f["id"] != fmt_id or f.get("is_system")]
    if len(updated) == len(formats):
        return jsonify({'error': 'Format not found or is a system format'}), 404
    save_formats(updated)
    return jsonify({'success': True})


# ── Upload & Process ──────────────────────────────────────────────────────────

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    # Read optional format_id from the form
    format_id = request.form.get('format_id', '')
    required_sections = []
    enabled_check_types = None

    if format_id:
        formats = load_formats()
        fmt = next((f for f in formats if f["id"] == format_id), None)
        if fmt:
            required_sections = fmt.get("mandatory_sections", [])
            enabled_checks = fmt.get("enabled_checks", [])
            if enabled_checks:
                types = {"missing_required_section"}
                for cid in enabled_checks:
                    if cid in AVAILABLE_CHECKS:
                        types.update(AVAILABLE_CHECKS[cid]["error_types"])
                enabled_check_types = types

    try:
        job_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                  f"{job_id}_{original_filename}")
        file.save(input_path)

        output_filename = f"annotated_{original_filename}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'],
                                   f"{job_id}_{output_filename}")

        print(f"[PROCESSING] Starting PDF processing (format={format_id or 'none'})…")
        errors, annotated_path, statistics, extracted_data, reference_analysis = process_pdf(
            input_path, output_path,
            required_sections=required_sections or None,
            enabled_check_types=enabled_check_types,
        )
        print(f"[PROCESSING] Complete — {len(errors)} errors")

        json_path = os.path.join(app.config['PROCESSED_FOLDER'],
                                 f"{job_id}_extracted_data.json")
        with open(json_path, 'w', encoding='utf-8') as jf:
            json.dump(extracted_data, jf, indent=2, ensure_ascii=False)

        processing_results[job_id] = {
            'job_id': job_id,
            'original_filename': original_filename,
            'output_filename': output_filename,
            'input_path': input_path,
            'output_path': output_path,
            'errors': [
                {
                    'check_id': e.check_id,
                    'check_name': e.check_name,
                    'description': e.description,
                    'page_num': e.page_num + 1,
                    'text': e.text,
                    'error_type': e.error_type,
                }
                for e in errors
            ],
            'error_count': len(errors),
            'statistics': statistics,
            'reference_analysis': reference_analysis,
            'mandatory_sections': required_sections,
            'document_overview': _build_document_overview(
                extracted_data, original_filename, statistics, len(errors)
            ),
            'processed_at': datetime.now().isoformat(),
        }

        return jsonify({
            'job_id': job_id,
            'original_filename': original_filename,
            'error_count': len(errors),
            'errors': processing_results[job_id]['errors'],
            'statistics': statistics,
            'reference_analysis': reference_analysis,
            'mandatory_sections': required_sections,
            'document_overview': processing_results[job_id]['document_overview'],
            'success': True,
        })

    except Exception as e:
        print(f"[UPLOAD] ERROR: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/download/<job_id>')
def download_file(job_id):
    if job_id not in processing_results:
        return jsonify({'error': 'Job not found'}), 404
    result = processing_results[job_id]
    if not os.path.exists(result['output_path']):
        return jsonify({'error': 'Processed file not found'}), 404
    return send_file(result['output_path'], as_attachment=True,
                     download_name=result['output_filename'],
                     mimetype='application/pdf')


@app.route('/results/<job_id>')
def get_results(job_id):
    if job_id not in processing_results:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(processing_results[job_id])


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    print("Starting Research Paper Error Checker…")
    print("Open your browser to: http://localhost:5001")
    app.run( host='0.0.0.0', port=5001)
