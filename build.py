import PyInstaller.__main__
import os
import platform
import sys

# Find customtkinter path manually to avoid importing it (which requires tkinter)
ctk_path = None
for path in sys.path:
    possible_path = os.path.join(path, 'customtkinter')
    if os.path.exists(possible_path):
        ctk_path = possible_path
        break

if ctk_path is None:
    print("Error: Could not find customtkinter package.")
    sys.exit(1)

# Determine separator for --add-data based on OS
# Linux/Mac uses ':', Windows uses ';'
separator = ';' if platform.system() == 'Windows' else ':'

# Build command arguments
args = [
    'main.py',
    '--name=wasm',
    '--onefile',
    '--windowed',  # Hide console window
    f'--add-data={ctk_path}{separator}customtkinter',
    '--icon=wasm.ico',
    '--clean',
    '--noconfirm',
]

print(f"Building with arguments: {args}")

# Run PyInstaller
PyInstaller.__main__.run(args)
