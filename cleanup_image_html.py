import os
import glob
from pathlib import Path

def is_image_path_html(file_path):
    """Check if a file path is an HTML file for an image URL."""
    image_extensions = ['.png.html', '.jpg.html', '.jpeg.html', '.gif.html', '.webp.html', '.bmp.html']
    return any(file_path.lower().endswith(ext) for ext in image_extensions)

def cleanup_image_html_files():
    """Remove HTML files that were incorrectly created for image URLs."""
    # Get the web directory path
    web_dir = Path(__file__).parent / 'web'
    
    # Find all HTML files in the web directory
    html_files = glob.glob(str(web_dir / "**" / "*.html"), recursive=True)
    
    # Filter for HTML files that correspond to image URLs
    image_html_files = [f for f in html_files if is_image_path_html(f)]
    
    print(f"Found {len(image_html_files)} HTML files created for image URLs:")
    
    # Remove each file
    for file_path in image_html_files:
        print(f"Removing: {file_path}")
        try:
            os.remove(file_path)
            # Create corresponding image directory if needed
            image_path = file_path[:-5]  # Remove .html extension
            image_dir = os.path.dirname(image_path)
            os.makedirs(image_dir, exist_ok=True)
            print(f"File removed successfully")
        except Exception as e:
            print(f"Error removing {file_path}: {e}")
            
    print(f"\nCleanup complete. Removed {len(image_html_files)} image HTML files.")

if __name__ == "__main__":
    cleanup_image_html_files()