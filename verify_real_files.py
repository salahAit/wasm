import os
import shutil
import sys

# Add current directory to path to import logic
sys.path.append(os.getcwd())

from logic import extract_barcode_number, generate_barcode_image, stamp_pdf

def verify_real_files():
    source_folder = "files"
    processed_dir = os.path.join(source_folder, "processed")
    
    # Start fresh
    if os.path.exists(processed_dir):
        shutil.rmtree(processed_dir)
    os.makedirs(processed_dir, exist_ok=True)
    
    print(f"Processing files in '{source_folder}'...")
    
    files = [f for f in os.listdir(source_folder) if f.lower().endswith('.pdf')]
    
    if not files:
        print("No PDF files found in 'files' folder.")
        return

    success_count = 0
    
    for filename in files:
        full_input_path = os.path.join(source_folder, filename)
        print(f"\nScanning: {filename}")
        
        # 1. Extract
        barcode_num = extract_barcode_number(filename)
        if not barcode_num:
            print(f"  [FAIL] Could not extract barcode number from filename.")
            continue
        print(f"  [OK] Extracted Barcode: {barcode_num}")
        
        # 2. Generate Barcode
        barcode_img_path = generate_barcode_image(barcode_num)
        if not barcode_img_path:
            print(f"  [FAIL] Could not generate barcode image.")
            continue
        
        # 3. Stamp PDF
        full_output_path = os.path.join(processed_dir, filename)
        success = stamp_pdf(full_input_path, full_output_path, barcode_img_path)
        
        if success:
            print(f"  [PASS] Processed successfully -> {full_output_path}")
            success_count += 1
        else:
            print(f"  [FAIL] Failed to stamp PDF.")
            
        # Cleanup
        if os.path.exists(barcode_img_path):
            os.remove(barcode_img_path)

    print(f"\nSummary: Successfully processed {success_count}/{len(files)} files.")

if __name__ == "__main__":
    verify_real_files()
