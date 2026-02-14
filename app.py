"""
Flask application for Research Paper Error Checker.
"""
import os
import uuid
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pdf_processor import process_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Store processing results in memory (in production, use a database)
processing_results = {}


def allowed_file(filename):
    """Check if file is a PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'


@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF upload and initiate processing."""
    print(f"\n[UPLOAD] Received upload request")
    print(f"[UPLOAD] Request files: {list(request.files.keys())}")
    
    if 'file' not in request.files:
        print("[UPLOAD] Error: No file in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    print(f"[UPLOAD] File received: {file.filename}")
    
    if file.filename == '':
        print("[UPLOAD] Error: Empty filename")
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        print(f"[UPLOAD] Error: Invalid file type for {file.filename}")
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Generate unique ID for this processing job
        job_id = str(uuid.uuid4())
        print(f"[UPLOAD] Generated job_id: {job_id}")
        
        # Save uploaded file
        original_filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{original_filename}")
        file.save(input_path)
        print(f"[UPLOAD] File saved to: {input_path}")
        
        # Process the PDF
        output_filename = f"annotated_{original_filename}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{job_id}_{output_filename}")
        
        print(f"[PROCESSING] Starting PDF processing...")
        errors, annotated_path, statistics = process_pdf(input_path, output_path)
        print(f"[PROCESSING] Complete! Found {len(errors)} errors")
        print(f"[PROCESSING] Statistics: {statistics}")
        
        # Store results
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
                    'page_num': e.page_num + 1,  # Convert to 1-indexed
                    'text': e.text,
                    'error_type': e.error_type
                }
                for e in errors
            ],
            'error_count': len(errors),
            'statistics': statistics,
            'processed_at': datetime.now().isoformat()
        }
        
        print(f"[UPLOAD] Returning success response with {len(errors)} errors")
        
        # Return results summary
        return jsonify({
            'job_id': job_id,
            'original_filename': original_filename,
            'error_count': len(errors),
            'errors': processing_results[job_id]['errors'],
            'statistics': statistics,
            'success': True
        })
    
    except Exception as e:
        print(f"[UPLOAD] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/download/<job_id>')
def download_file(job_id):
    """Download the annotated PDF."""
    if job_id not in processing_results:
        return jsonify({'error': 'Job not found'}), 404
    
    result = processing_results[job_id]
    output_path = result['output_path']
    
    if not os.path.exists(output_path):
        return jsonify({'error': 'Processed file not found'}), 404
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name=result['output_filename'],
        mimetype='application/pdf'
    )


@app.route('/results/<job_id>')
def get_results(job_id):
    """Get processing results for a job."""
    if job_id not in processing_results:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(processing_results[job_id])


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    print("Starting Research Paper Error Checker...")
    print("Open your browser to: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
