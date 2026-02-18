from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_icon():
    size = (256, 256)
    bg_color = (0, 122, 204) # VS Code Blue - similar to user request for dark blue/white
    text_color = "white"
    
    img = Image.new('RGB', size, color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Try to use a default font, otherwise fall back to default
    try:
        # Linux standard font path often has DejaVu
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 150)
    except IOError:
        font = ImageFont.load_default()
        print("Warning: Using default font, might look small.")

    # Calculate text position to center it
    text = "W"
    
    # Create a mask for the text to handle sizing if font metrics are tricky
    # Text Anchor 'mm' means Middle Middle
    try:
        d.text((128, 128), text, fill=text_color, font=font, anchor="mm")
    except AttributeError:
        # Older Pillow versions don't support anchor
        w, h = d.textsize(text, font=font)
        d.text(((256-w)/2, (256-h)/2), text, fill=text_color, font=font)
        
    # Save as PNG
    img.save("wasm_icon.png")
    print("Created wasm_icon.png")
    
    # Save as ICO (requires sizes)
    # Windows icons support multiple sizes
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save("wasm.ico", format='ICO', sizes=icon_sizes)
    print("Created wasm.ico")

if __name__ == "__main__":
    create_icon()
