import os
import re
import sqlite3
import threading
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import fitz  # PyMuPDF
import barcode
from barcode.writer import ImageWriter
import pandas as pd
import json
import csv

# Configuration
DB_NAME = "codeabar.db"
TABLE_NAME = "codeabar"

from logic import extract_barcode_number, generate_barcode_image, stamp_pdf

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WASM")
        self.geometry("700x550")
        
        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Log area expands

        # Title
        self.label_title = ctk.CTkLabel(self, text="WASM - PDF Processor", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20)

        # Folder Selection Frame
        self.frame_top = ctk.CTkFrame(self)
        self.frame_top.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frame_top.grid_columnconfigure(0, weight=1)

        self.entry_folder = ctk.CTkEntry(self.frame_top, placeholder_text="Select Folder containing PDFs...")
        self.entry_folder.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_browse = ctk.CTkButton(self.frame_top, text="Browse", command=self.browse_folder)
        self.btn_browse.grid(row=0, column=1, padx=10, pady=10)

        # Log Area
        self.textbox_log = ctk.CTkTextbox(self, width=660)
        self.textbox_log.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox_log.insert("0.0", "Welcome! Please select a folder to begin processing.\n")

        # Progress Bar
        self.progressbar = ctk.CTkProgressBar(self)
        self.progressbar.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.progressbar.set(0)

        # Start Button
        self.btn_start = ctk.CTkButton(self, text="Start Processing", command=self.start_processing, height=40, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_start.grid(row=4, column=0, padx=20, pady=20)

        # Database Setup
        self.init_db()

    def init_db(self):
        """Initialize the SQLite database."""
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT,
                    barcode_num TEXT,
                    process_date TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            self.log("Database initialized successfully.")
        except Exception as e:
            self.log(f"Error initializing database: {e}")

    def log(self, message):
        """Add a message to the log area (thread-safe)."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        self.after(0, self._append_to_log, full_message)

    def _append_to_log(self, message):
        self.textbox_log.insert("end", message)
        self.textbox_log.see("end")

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, folder_path)
            self.log(f"Selected folder: {folder_path}")

    def update_progress(self, current, total):
        progress = current / total
        self.after(0, lambda: self.progressbar.set(progress))

    def process_thread(self, source_folder):
        """Background thread to process files."""
        self.after(0, lambda: self.btn_start.configure(state="disabled"))
        self.update_progress(0, 1)
        
        try:
            files = [f for f in os.listdir(source_folder) if f.lower().endswith('.pdf')]
            total_files = len(files)
            
            if total_files == 0:
                self.log("No PDF files found in the selected folder.")
                self.after(0, lambda: self.btn_start.configure(state="normal"))
                return

            # Create 'processed' subfolder
            processed_dir = os.path.join(source_folder, "processed")
            os.makedirs(processed_dir, exist_ok=True)
            
            processed_count = 0
            processed_data = []
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            for i, filename in enumerate(files):
                full_input_path = os.path.join(source_folder, filename)
                
                # 1. Extract Info
                self.log(f"Processing: {filename}...")
                barcode_num = extract_barcode_number(filename)
                
                if not barcode_num:
                    self.log(f"Skipping {filename}: Could not extract barcode number.")
                    self.update_progress(i + 1, total_files)
                    continue
                
                # 2. Generate Barcode
                barcode_img_path = generate_barcode_image(barcode_num)
                if not barcode_img_path:
                    self.log(f"Error generating barcode for {barcode_num}.")
                    self.update_progress(i + 1, total_files)
                    continue
                    
                # 3. Stamp PDF
                full_output_path = os.path.join(processed_dir, filename)
                
                # We need to ensure we don't block the GUI with heavy PDF ops, but we are in a thread, so it's fine.
                try:
                    success = stamp_pdf(full_input_path, full_output_path, barcode_img_path)
                except Exception as e:
                     self.log(f"Error stamping PDF: {e}")
                     success = False

                # Cleanup barcode image
                if os.path.exists(barcode_img_path):
                    os.remove(barcode_img_path)

                if success:
                    # 4. Save to Database
                    try:
                        cursor.execute(f"INSERT INTO {TABLE_NAME} (file_name, barcode_num, process_date) VALUES (?, ?, ?)",
                                       (filename, barcode_num, datetime.datetime.now()))
                        conn.commit()
                        self.log(f"Success! Saved to {full_output_path}")
                        processed_count += 1
                    except Exception as e:
                        self.log(f"Database error: {e}")
                
                self.update_progress(i + 1, total_files)
            
            conn.close()
            self.log(f"Done! Processed {processed_count}/{total_files} files.")
            self.after(0, lambda: messagebox.showinfo("Complete", f"Processing complete.\nProcessed {processed_count} files."))
            
        except Exception as e:
            self.log(f"Critical Error: {e}")
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self.btn_start.configure(state="normal"))

    def start_processing(self):
        folder_path = self.entry_folder.get()
        if not folder_path or not os.path.exists(folder_path):
            messagebox.showwarning("Warning", "Please select a valid folder.")
            return

        threading.Thread(target=self.process_thread, args=(folder_path,), daemon=True).start()


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
