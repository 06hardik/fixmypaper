#!/usr/bin/env python3
"""
Demonstration of PyMuPDF image extraction and resolution checking.
"""

import fitz  # PyMuPDF

def extract_and_check_images(pdf_path):
    """Extract all images from PDF and check their resolution."""
    doc = fitz.open(pdf_path)
    
    all_images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get all images on this page
        image_list = page.get_images(full=True)
        
        print(f"\n📄 Page {page_num + 1}: Found {len(image_list)} images")
        
        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]  # Image reference number
            
            # Extract image details
            base_image = doc.extract_image(xref)
            
            image_data = {
                'page': page_num + 1,
                'xref': xref,
                'width': base_image['width'],
                'height': base_image['height'],
                'colorspace': base_image['colorspace'],
                'bpc': base_image['bpc'],  # Bits per component
                'ext': base_image['ext'],  # Extension (png, jpeg, etc.)
                'size_bytes': len(base_image['image']),
            }
            
            # Calculate DPI (dots per inch)
            # Get image dimensions in the PDF (in points)
            img_rects = page.get_image_rects(xref)
            if img_rects:
                rect = img_rects[0]  # Use first occurrence
                width_points = rect.width
                height_points = rect.height
                
                # Convert points to inches (72 points = 1 inch)
                width_inches = width_points / 72
                height_inches = height_points / 72
                
                # Calculate DPI
                dpi_x = image_data['width'] / width_inches if width_inches > 0 else 0
                dpi_y = image_data['height'] / height_inches if height_inches > 0 else 0
                
                image_data['dpi_x'] = dpi_x
                image_data['dpi_y'] = dpi_y
                image_data['dpi_avg'] = (dpi_x + dpi_y) / 2
                
                # Check quality
                if image_data['dpi_avg'] < 150:
                    quality = "❌ LOW (< 150 DPI)"
                elif image_data['dpi_avg'] < 300:
                    quality = "⚠️ MEDIUM (150-300 DPI)"
                else:
                    quality = "✅ HIGH (≥ 300 DPI)"
                
                image_data['quality'] = quality
            else:
                image_data['dpi_x'] = 0
                image_data['dpi_y'] = 0
                image_data['dpi_avg'] = 0
                image_data['quality'] = "⚠️ UNKNOWN"
            
            all_images.append(image_data)
            
            # Print details
            print(f"\n  Image {img_idx + 1}:")
            print(f"    Dimensions: {image_data['width']} x {image_data['height']} pixels")
            print(f"    Resolution: {image_data['dpi_avg']:.1f} DPI")
            print(f"    Quality: {image_data['quality']}")
            print(f"    Format: {image_data['ext']}")
            print(f"    Size: {image_data['size_bytes'] / 1024:.1f} KB")
    
    doc.close()
    
    # Summary
    print(f"\n" + "="*60)
    print(f"📊 SUMMARY:")
    print(f"   Total images: {len(all_images)}")
    
    low_res = [img for img in all_images if img['dpi_avg'] > 0 and img['dpi_avg'] < 150]
    medium_res = [img for img in all_images if 150 <= img['dpi_avg'] < 300]
    high_res = [img for img in all_images if img['dpi_avg'] >= 300]
    
    print(f"   ❌ Low resolution (< 150 DPI): {len(low_res)}")
    print(f"   ⚠️ Medium resolution (150-300 DPI): {len(medium_res)}")
    print(f"   ✅ High resolution (≥ 300 DPI): {len(high_res)}")
    
    return all_images

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_image_extraction.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    images = extract_and_check_images(pdf_path)
