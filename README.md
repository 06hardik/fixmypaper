# Research Paper Error Checker

A web application that automatically detects common formatting errors in research papers (PDFs) and creates annotated versions with highlighted errors.

## Features

- 📄 Detects 18+ types of formatting errors
- 🎯 Smart equation detection using heuristics
- 📊 Document statistics (words, images, tables, figures)
- 🎨 Color-coded error annotations
- 📥 Download annotated PDF with highlights
- 🔍 Comprehensive error checking

## Error Types Detected

### Figures & Tables
- Every figure cited in text
- Every table cited in text
- Sequential numbering

### Equations
- Consecutive numbering
- Proper parentheses format
- Referenced in text
- Punctuation after equations

### Citations & References
- Citation style consistency (IEEE vs APA)
- Proper punctuation placement
- Citations match reference list
- DOI included in journal articles
- Reference ordering

### Typography
- Space before units
- En-dash for numeric ranges
- Spacing after punctuation

### Acronyms
- Defined at first occurrence

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd research-paper-checker
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   Navigate to `http://localhost:5001`

## Deployment

### Deploy to Render.com (Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will auto-detect settings from `render.yaml`
6. Click "Create Web Service"

Your app will be live at: `https://your-app-name.onrender.com`

## Technology Stack

- **Backend**: Flask (Python)
- **PDF Processing**: PyMuPDF (fitz)
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Gunicorn

## Project Structure

```
research-paper-checker/
├── app.py                  # Flask application
├── pdf_processor.py        # PDF analysis and error detection
├── requirements.txt        # Python dependencies
├── Procfile               # Deployment configuration
├── render.yaml            # Render.com configuration
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── main.js        # Frontend logic
├── templates/
│   └── index.html         # Main page
├── uploads/               # Uploaded PDFs (temporary)
└── processed/             # Annotated PDFs (temporary)
```

## Usage

1. **Upload PDF**: Click "Browse Files" or drag & drop
2. **Wait for Processing**: 2-10 seconds depending on paper size
3. **View Results**: See error summary and statistics
4. **Download**: Get annotated PDF with highlighted errors

## Documentation

- `HOW_IT_WORKS.md` - In-depth system explanation
- `UPDATED_CHECKS.md` - All error checks documentation
- `STATISTICS_FEATURE.md` - Document statistics feature
- `DEPLOYMENT.md` - Deployment options guide

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions, please open a GitHub issue.
