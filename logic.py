import re
import os
import fitz  # PyMuPDF
import barcode
from barcode.writer import ImageWriter

def extract_barcode_number(filename):
    """Extracts the barcode number from the filename."""
    # Current logic: extract all digits from the filename
    # file-01-02-03-26.pdf -> 01020326
    digits = re.findall(r'\d+', filename)
    if not digits:
        return None
    return "".join(digits)

def generate_barcode_image(barcode_num):
    """Generates a barcode image and returns the path to the temporary file."""
    try:
        # Code128 is a standard barcode format
        code128 = barcode.get_barcode_class('code128')
        my_barcode = code128(barcode_num, writer=ImageWriter())
        
        # Save to a temporary file
        temp_filename = f"temp_barcode_{barcode_num}"
        # barcode.save adds the extension automatically
        saved_filename = my_barcode.save(temp_filename)
        return saved_filename
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None

def stamp_pdf(input_path, output_path, barcode_image_path):
    """Adds the barcode image to the bottom left of every page in the PDF."""
    try:
        doc = fitz.open(input_path)
        img = open(barcode_image_path, "rb").read()
        
        for page in doc:
            # PDF coordinates: (0,0) is top-left.
            # We want bottom-left.
            # page.rect.height gives the height of the page.
            
            # Let's say we want it 20 units from left and 20 units from bottom.
            # Barcode size: ~200x80
            
            x_start = 20
            y_end = page.rect.height - 20
            y_start = y_end - 80
            x_end = x_start + 200
            
            target_rect = fitz.Rect(x_start, y_start, x_end, y_end)
            
            # Overlay the image
            page.insert_image(target_rect, stream=img)
        
        doc.save(output_path)
        doc.close()
        return True
    except Exception as e:
        print(f"Error stamping PDF: {e}")
        return False
