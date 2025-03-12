import os
import shutil
from pathlib import Path

def clean_web_folder():
    # Path to web folder
    web_folder = Path(__file__).parent / 'web'
    
    if not web_folder.exists():
        print(f"Web folder not found at {web_folder}")
        return
    
    print(f"Cleaning contents of {web_folder}")
    
    # List all items in the web folder
    for item in web_folder.iterdir():
        try:
            if item.is_file():
                # Remove file
                os.remove(item)
                print(f"Removed file: {item.name}")
            elif item.is_dir():
                # Remove directory and all its contents
                shutil.rmtree(item)
                print(f"Removed directory: {item.name}")
        except Exception as e:
            print(f"Error removing {item.name}: {e}")
    
    print(f"Finished cleaning {web_folder}")

if __name__ == "__main__":
    clean_web_folder()