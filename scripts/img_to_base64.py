import base64
import os
import mimetypes
import sys
import urllib.request
import urllib.error

def get_image_content(source):
    """
    Retrieves image content and mime type from a URL or local file.
    """
    if source.startswith('http://') or source.startswith('https://'):
        try:
            # Add a User-Agent header to avoid 403 Forbidden on some sites
            req = urllib.request.Request(
                source, 
                data=None, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            with urllib.request.urlopen(req) as response:
                content = response.read()
                mime_type = response.headers.get_content_type()
                return content, mime_type
        except urllib.error.URLError as e:
            print(f"Error downloading URL: {e}")
            return None, None
    else:
        if not os.path.exists(source):
            print(f"Error: File not found at {source}")
            return None, None
        
        try:
            with open(source, "rb") as image_file:
                content = image_file.read()
            mime_type = mimetypes.guess_type(source)[0]
            return content, mime_type
        except Exception as e:
            print(f"Error reading file: {e}")
            return None, None

def main():
    print("=========================================")
    print("   Image to Base64 Converter Tool")
    print("=========================================")
    print("Supported inputs: Local file paths or HTTP/HTTPS URLs")
    
    while True:
        source = input("\nEnter image URL or local file path (or 'q' to quit): ").strip()
        
        if source.lower() == 'q':
            break

        # Remove quotes if user copied path as "path"
        if source.startswith('"') and source.endswith('"'):
            source = source[1:-1]
        elif source.startswith("'") and source.endswith("'"):
            source = source[1:-1]

        if not source:
            print("Empty input. Please try again.")
            continue

        print(f"Processing: {source} ...")
        content, mime_type = get_image_content(source)

        if content:
            if not mime_type:
                mime_type = 'image/png' # Default fallback if detection fails
                print("Warning: Could not detect MIME type, defaulting to image/png")

            encoded_string = base64.b64encode(content).decode('utf-8')
            full_string = f"data:{mime_type};base64,{encoded_string}"
            
            output_filename = "base64_output.txt"
            try:
                with open(output_filename, "w") as f:
                    f.write(full_string)
                print(f"\n[SUCCESS] Base64 data saved to '{output_filename}'")
                print(f"Total length: {len(full_string)} characters")
                print("Instruction: Open 'base64_output.txt', copy ALL text, and paste it into your HTML img src.")
                print(f"Example: <img src=\"{full_string[:30]}...\" alt=\"Logo\">")
            except Exception as e:
                print(f"Error writing output file: {e}")
        else:
            print("\n[FAILED] Conversion failed. Please check the path/URL and try again.")

if __name__ == "__main__":
    main()
