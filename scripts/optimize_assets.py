import os
import re
import base64
import io
from PIL import Image

ASSETS_DIR = os.path.join("components", "esp-wifi-connect", "assets")
HTML_FILES = ["wifi_configuration.html", "wifi_configuration_done.html"]
MAX_WIDTH = 600
JPEG_QUALITY = 70

def optimize_image_data(base64_string, mime_type):
    try:
        # Decode base64
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (e.g. for PNG with transparency to JPEG)
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Resize if too large
        if image.width > MAX_WIDTH:
            ratio = MAX_WIDTH / image.width
            new_height = int(image.height * ratio)
            image = image.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
            
        # Save to buffer as JPEG
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        
        # Encode back to base64
        new_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Return new src string
        return f"data:image/jpeg;base64,{new_base64}"
        
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return None

def process_html_file(filename):
    filepath = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    print(f"Processing {filename}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original_size = len(content)
    
    # Regex to find img src with base64
    # Matches src="data:image/TYPE;base64,DATA"
    pattern = re.compile(r'src=["\'](data:image/([a-zA-Z]+);base64,([^"\']+))["\']')
    
    def replace_callback(match):
        full_src = match.group(1)
        mime_subtype = match.group(2)
        base64_data = match.group(3)
        
        print(f"Found image of type {mime_subtype}, length {len(base64_data)}")
        
        new_src = optimize_image_data(base64_data, mime_subtype)
        
        if new_src:
            print(f"Optimized to length {len(new_src)}")
            return f'src="{new_src}"'
        else:
            return match.group(0) # Return original if failed

    new_content = pattern.sub(replace_callback, content)
    
    new_size = len(new_content)
    print(f"Size reduced from {original_size} to {new_size} bytes ({100 - new_size/original_size*100:.1f}%)")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    for html_file in HTML_FILES:
        process_html_file(html_file)

if __name__ == "__main__":
    main()
