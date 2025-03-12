from flask import Flask, request, redirect, url_for
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
import glob
import re
import datetime
import hashlib

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Use a valid model (replace with an actual valid model name if needed)
model = genai.GenerativeModel('models/gemini-2.0-flash')

# Define the root directory path - use absolute path to avoid issues
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT_DIR, "web")
print(f"Root directory path: {ROOT_DIR}")
print(f"Web directory path: {WEB_DIR}")
os.makedirs(WEB_DIR, exist_ok=True)

app = Flask(__name__)


BASE_PROMPT = """Generate a response for the URL path: `{{URL_PATH}}`

The first line must be the Content-Type (use 'text/html' for HTML responses).
All subsequent lines should contain ONLY the renderable content with NO explanatory text, examples, or instructions.

For HTML responses:
- Include proper HTML structure (doctype, html, head, body tags)
- Add a relevant title and content based on the URL path
- IMPORTANT: When creating links to related topics, always use the full path that includes the current context.
  For example, if the current URL is "/stronghold-crusader" and you're linking to "units", 
  use "/stronghold-crusader/units" instead of just "/units".
- Ensure all relative links maintain the parent context of the current URL path 
- Ensure the HTML is valid and immediately renderable in a browser

{{OPTIONAL_DATA}}
Content-Type:
"""

# HTML template for the search page
SEARCH_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INFINITE AI WEB</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            position: relative;
        }
        .logo {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 30px;
            color: #4285f4;
            text-align: center;
        }
        .search-container {
            width: 100%;
            max-width: 584px;
        }
        .search-bar {
            width: 100%;
            padding: 12px 20px;
            margin: 8px 0;
            box-sizing: border-box;
            border: 1px solid #dfe1e5;
            border-radius: 24px;
            font-size: 16px;
            outline: none;
        }
        .search-bar:hover, .search-bar:focus {
            box-shadow: 0 1px 6px rgba(32,33,36,.28);
            border-color: rgba(223,225,229,0);
        }
        .search-button {
            background-color: #f8f9fa;
            border: 1px solid #f8f9fa;
            border-radius: 4px;
            color: #3c4043;
            font-family: Arial, sans-serif;
            font-size: 14px;
            margin: 11px 4px;
            padding: 0 16px;
            line-height: 27px;
            height: 36px;
            min-width: 54px;
            text-align: center;
            cursor: pointer;
            user-select: none;
        }
        .search-button:hover {
            box-shadow: 0 1px 1px rgba(0,0,0,.1);
            background-color: #f8f9fa;
            border: 1px solid #dadce0;
            color: #202124;
        }
        .buttons {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 10px;
        }
        .infinite {
            background: linear-gradient(to right, #4285f4, #ea4335, #fbbc05, #34a853, #4285f4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 800% 100%;
            animation: gradient 10s linear infinite;
        }
        @keyframes gradient {
            0% {
                background-position: 0% 0%;
            }
            100% {
                background-position: 800% 0%;
            }
        }
        .footer {
            position: fixed;
            bottom: 20px;
            text-align: center;
            width: 100%;
            font-size: 14px;
            color: #70757a;
        }
        .footer a {
            color: #70757a;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .links-container {
            position: absolute;
            top: 20px;
            right: 20px;
        }
        .links-container a {
            color: #70757a;
            text-decoration: none;
            font-size: 14px;
        }
        .links-container a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="links-container">
        <a href="/index">Saved Searches</a>
    </div>
    <div class="logo"><span class="infinite">INFINITE AI WEB</span></div>
    <div class="search-container">
        <form action="/search" method="GET">
            <input type="text" class="search-bar" name="query" placeholder="Search the web..." autofocus>
            <div class="buttons">
                <button type="submit" class="search-button">Search</button>
            </div>
        </form>
    </div>
    <div class="footer">
        made with 🍋 by Lime1
    </div>
</body>
</html>
"""

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
        links_html += f'    <li><a href="/{path}">{display_path}</a></li>\n'
    
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
    <a href="/" class="home-link">Back to Search</a>
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

@app.route("/", methods=['GET'])
def home():
    # Save the home page HTML if it doesn't exist yet
    home_path = os.path.join(ROOT_DIR, "home.html")
    if not os.path.exists(home_path):
        with open(home_path, "w", encoding="utf-8") as f:
            f.write(SEARCH_PAGE_HTML)
        print("Saved home page HTML to home.html")
    
    return SEARCH_PAGE_HTML, 200, {'Content-Type': 'text/html'}

@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('home'))
    
    # Convert the query to a URL-friendly format
    search_path = query.replace(' ', '-').lower()
    return redirect(f"/{search_path}")

@app.route("/index", methods=['GET'])
def index():
    # Generate an up-to-date index.html and serve it
    generate_index_html()
    with open(os.path.join(ROOT_DIR, "index.html"), "r", encoding="utf-8") as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/html'}

@app.route("/<path:path>", methods=['POST', 'GET'])
def catch_all(path=""):
    print(f"Handling request for path: {path}")
    
    # Special handling for index.html
    if path == "index.html":
        return redirect(url_for('index'))
    
    # First check if file exists in web directory
    web_file_path = os.path.join(WEB_DIR, path + ".html")
    if os.path.exists(web_file_path):
        print(f"Serving existing file from web directory: {web_file_path}")
        with open(web_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/html'}
    
    # Then check if file exists in root directory (for backward compatibility)
    root_file_path = os.path.join(ROOT_DIR, path + ".html")
    if os.path.exists(root_file_path):
        print(f"Serving existing file from root directory: {root_file_path}")
        with open(root_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/html'}
    
    # Generate content for any path that hasn't been found
    print(f"No existing file found for {path}, generating content...")
    
    if request.form:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", f"form data: {json.dumps(request.form)}")
    else:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", f"")

    prompt_content = prompt_content.replace("{{URL_PATH}}", path)
    
    print("Generating content with LLM...")
    try:
        response = model.generate_content(prompt_content)
        ai_data = response.text

        print("Content generated successfully")
        
        # Extract content type and response data
        lines = ai_data.splitlines()
        if not lines:
            return "Error: Empty response from model", 500
            
        content_type = lines[0].strip()
        response_data = "\n".join(lines[1:])
        
        print(f"Content type: {content_type}")
        
        # Save all HTML responses to the file system, regardless of how they're accessed
        if content_type == "text/html":
            print(f"Saving HTML response for path: {path}")
            save_html_response(path, response_data)
        
        return response_data, 200, {'Content-Type': content_type}
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        error_page = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error - INFINITE AI WEB</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #ea4335; }}
                .home-link {{ margin-top: 30px; }}
            </style>
        </head>
        <body>
            <h1>Error Generating Content</h1>
            <p>There was an error generating content for: <strong>{path}</strong></p>
            <p>Error details: {str(e)}</p>
            <div class="home-link">
                <a href="/">Back to Search</a>
            </div>
        </body>
        </html>
        """
        return error_page, 500, {'Content-Type': 'text/html'}

if __name__ == '__main__':
    # Create index.html if it doesn't exist yet
    if not os.path.exists(os.path.join(ROOT_DIR, "index.html")):
        print("Generating initial index.html...")
        generate_index_html()
    
    print("Starting Flask application...")
    app.run(debug=True)