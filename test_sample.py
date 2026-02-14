"""
Test script to verify the PDF processor works correctly.
Creates a sample test PDF with known errors.
"""
import fitz  # PyMuPDF
import os
from pdf_processor import process_pdf


def create_sample_pdf(output_path):
    """Create a sample PDF with various formatting errors."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size
    
    # Sample text with various errors
    sample_texts = [
        # Error: Punctuation before citation (Check #17)
        "This is a well-known fact,[1] which has been proven.",
        
        # Error: Hyphen instead of en-dash in range (Check #28)
        "The temperature range was 20-30 degrees Celsius.",
        
        # Error: Missing space after comma (Check #29)
        "The experiment included water,salt,and sugar.",
        
        # Error: Extra spaces after period (Check #29)
        "This is the first sentence.  This is the second.",
        
        # Error: Regular space before unit (Check #27)
        "The measurement was 25 kg and 100 mm in length.",
        
        # Correct examples (should not be flagged)
        "This is a correct citation [2].",
        "The range 50–60 Hz is optimal.",
        "Proper spacing: one, two, three.",
    ]
    
    y_position = 100
    for text in sample_texts:
        page.insert_text((50, y_position), text, fontsize=11)
        y_position += 30
    
    # Add a references section
    page.insert_text((50, y_position + 50), "References", fontsize=14)
    y_position += 80
    
    # Reference without DOI (Check #22)
    page.insert_text((50, y_position), 
                    "[1] Smith, J. (2023). Title of paper. Journal Name, vol. 10, no. 2, pp. 123-145.",
                    fontsize=10)
    
    doc.save(output_path)
    doc.close()
    print(f"Sample PDF created: {output_path}")


def test_processor():
    """Test the PDF processor with the sample PDF."""
    # Create sample PDF
    sample_pdf = "test_sample.pdf"
    output_pdf = "test_sample_annotated.pdf"
    
    print("Creating sample PDF with known errors...")
    create_sample_pdf(sample_pdf)
    
    print("\nProcessing PDF...")
    errors, annotated_path = process_pdf(sample_pdf, output_pdf)
    
    print(f"\nFound {len(errors)} errors:")
    print("-" * 80)
    
    for i, error in enumerate(errors, 1):
        print(f"\n{i}. Check #{error.check_id}: {error.check_name}")
        print(f"   Page: {error.page_num + 1}")
        print(f"   Description: {error.description}")
        print(f"   Found text: '{error.text}'")
        print(f"   Location: {error.bbox}")
    
    print("\n" + "=" * 80)
    print(f"Annotated PDF saved to: {output_pdf}")
    print("Open the annotated PDF to see highlighted errors!")
    
    # Cleanup
    if os.path.exists(sample_pdf):
        os.remove(sample_pdf)
        print(f"\nCleaned up test file: {sample_pdf}")


if __name__ == "__main__":
    test_processor()
