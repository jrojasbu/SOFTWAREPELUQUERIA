from PIL import Image
import os

img_path = r"C:/Users/JROJASBU/.gemini/antigravity/brain/427a8764-2a5b-4f58-b7e8-246f76299be2/uploaded_image_1768412174404.png"
output_path = r"c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SOFTWARE PELUQUERIA\Magical_Hair_v3.ico"

try:
    img = Image.open(img_path)
    # Ensure it's RGBA
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
        
    img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Icon saved successfully to {output_path}")
except Exception as e:
    print(f"Error creating icon: {e}")
