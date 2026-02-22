import subprocess
import sys
import os
import platform

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
pyinstaller_args = [
    'main.py',
    '--name=wasm',
    '--onefile',
    '--windowed',  # Hide console window
    f'--add-data={ctk_path}{separator}customtkinter',
    '--icon=wasm.ico',
    '--clean',
    '--noconfirm',
    # Hidden imports that PyInstaller may miss
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageDraw',
    '--hidden-import=PIL.ImageFont',
    '--hidden-import=barcode',
    '--hidden-import=barcode.codex',
    '--hidden-import=barcode.code128',
    '--hidden-import=barcode.writer',
]

print(f"Building with arguments: {pyinstaller_args}")

# Run PyInstaller via subprocess
cmd = [sys.executable, '-m', 'PyInstaller'] + pyinstaller_args
print(f"Executing command: {' '.join(cmd)}")
subprocess.check_call(cmd)

