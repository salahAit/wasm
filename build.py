import PyInstaller.__main__
import customtkinter
import os
import platform

# Find customtkinter path to include its assets
ctk_path = os.path.dirname(customtkinter.__file__)

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
