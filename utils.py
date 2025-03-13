import os
import glob
from config import ROOT_DIR, WEB_DIR

def save_html_response(path, html_content):
    """Save HTML content to a file in the web directory based on the path."""
    # Remove leading slash if present
    if path.startswith("/"):
        path = path[1:]
    
    # Skip saving if this is an index request that should go to root
    if path == "index":
        print("Skipping saving index.html to web directory as it belongs in root")
        generate_index_html()
        return True
        
    print(f"Attempting to save file for path: {path}")
    
    try:
        # Create directory structure if needed
        if "/" in path:
            dir_path = os.path.join(WEB_DIR, os.path.dirname(path))
            print(f"Creating directory: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(WEB_DIR, path + ".html")
        else:
            # If it's a root level path, save directly in web directory
            file_path = os.path.join(WEB_DIR, path + ".html")
        
        print(f"Saving content to file: {file_path}")
        
        # Save HTML content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Successfully saved HTML to {file_path}")
        
        # Regenerate the index.html file
        generate_index_html()
        
        return True
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return False

def generate_index_html():
    """Generate an index.html file listing all saved queries alphabetically."""
    # Get all HTML files in web directory
    html_files = glob.glob(os.path.join(WEB_DIR, "**", "*.html"), recursive=True)
    print(f"Found {len(html_files)} HTML files in web directory")
    
    # Extract paths from filenames and sort them alphabetically
    paths = []
    for file_path in html_files:
        # Skip any Flask-related files and index.html in web directory
        if "flask" in file_path.lower() or os.path.basename(file_path) == "index.html":
            continue
        
        # Get relative path from root directory
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        # Convert Windows backslashes to forward slashes for URLs
        rel_path = rel_path.replace("\\", "/")
        # Remove .html extension
        if rel_path.endswith(".html"):
            rel_path = rel_path[:-5]
        # If the file is named index.html in a subdirectory, get the directory name
        if rel_path.endswith("/index"):
            rel_path = rel_path[:-6]
        
        print(f"Adding path: {rel_path}")
        paths.append(rel_path)
    
    # Sort paths alphabetically
    paths.sort()
    
    # Generate HTML list of links
    links_html = ""
    for path in paths:
        # Format path for display (replace hyphens with spaces, capitalize words)
        display_path = path.replace("-", " ").replace("/", " › ")
        display_path = " ".join([word.capitalize() for word in display_path.split()])
        # Remove the leading slash from links to make them relative
        links_html += f'    <li><a href="{path}">{display_path}</a></li>\n'
    
    # If no links, add a message
    if not links_html:
        links_html = '    <li>No searches saved yet. Try searching for something!</li>\n'
    
    # Generate complete HTML
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INFINITE AI WEB - Saved Searches</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: #4285f4;
            text-align: center;
            margin-bottom: 30px;
        }}
        ul {{
            list-style-type: none;
            padding: 0;
        }}
        li {{
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        a {{
            color: #1a73e8;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .home-link {{
            display: block;
            margin-top: 30px;
            text-align: center;
        }}
        .infinite {{
            background: linear-gradient(to right, #4285f4, #ea4335, #fbbc05, #34a853, #4285f4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 800% 100%;
            animation: gradient 10s linear infinite;
            font-weight: bold;
        }}
        @keyframes gradient {{
            0% {{
                background-position: 0% 0%;
            }}
            100% {{
                background-position: 800% 0%;
            }}
        }}
        .footer {{
            margin-top: 50px;
            text-align: center;
            color: #70757a;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1><span class="infinite">INFINITE AI WEB</span></h1>
    <h2>Saved Searches</h2>
    <ul>
{links_html}
    </ul>
    <a href="." class="home-link">Back to Search</a>
    <div class="footer">
        made with 🍋 by Lime1
    </div>
</body>
</html>"""
    
    # Save the index.html file to ROOT_DIR instead of WEB_DIR
    index_path = os.path.join(ROOT_DIR, "index.html")
    print(f"Saving index.html to {index_path}")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    
    # Delete any index.html in web directory to prevent conflicts
    web_index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(web_index_path):
        print(f"Removing duplicate index.html from web directory: {web_index_path}")
        try:
            os.remove(web_index_path)
        except Exception as e:
            print(f"Warning: Failed to remove web directory index.html: {str(e)}")
    
    print("Index generated successfully")
