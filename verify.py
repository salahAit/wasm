import os
import fitz
import sys
import shutil
# Add current directory to path to import main
sys.path.append(os.getcwd())

from logic import extract_barcode_number, generate_barcode_image, stamp_pdf

def create_dummy_pdf(filename):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a dummy PDF file for testing.", fontsize=20)
    doc.save(filename)
    doc.close()
    return filename

def test_logic():
    print("Starting verification...")
    
    # Setup directories
    test_dir = "test_env"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Test 1: Extract Barcode Number
    filename = "file-01-02-03-26.pdf"
    expected_code = "01020326"
    extracted = extract_barcode_number(filename)
    if extracted == expected_code:
        print(f"[PASS] Extracted barcode: {extracted}")
    else:
        print(f"[FAIL] Expected {expected_code}, got {extracted}")
        
    # Test 2: Generate Barcode
    barcode_img = generate_barcode_image(expected_code)
    if barcode_img and os.path.exists(barcode_img):
        print(f"[PASS] Barcode image generated: {barcode_img}")
    else:
        print(f"[FAIL] Barcode image generation failed")
        return

    # Test 3: Stamp PDF
    pdf_path = os.path.join(test_dir, filename)
    create_dummy_pdf(pdf_path)
    output_path = os.path.join(test_dir, "processed_" + filename)
    
    success = stamp_pdf(pdf_path, output_path, barcode_img)
    
    if success and os.path.exists(output_path):
        print(f"[PASS] PDF stamped successfully: {output_path}")
        # Verify database logic isn't tested here as it's coupled with App class in previous design, 
        # but logic functions are what we care about most for correctness.
        # DB logic is standard sqlite3, less prone to logic errors than PDF manipulation.
    else:
        print(f"[FAIL] PDF stamping failed")

    # Cleanup
    if os.path.exists(barcode_img):
        os.remove(barcode_img)
    # shutil.rmtree(test_dir) # Keep for inspection if needed

if __name__ == "__main__":
    test_logic()
