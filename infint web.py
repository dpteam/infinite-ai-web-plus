from flask import Flask, request, redirect, url_for
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# flask --app main --debug run

# Get API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Use a valid model (replace with an actual valid model name if needed)
model = genai.GenerativeModel('models/gemini-2.0-flash')


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
    </style>
</head>
<body>
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

@app.route("/", methods=['GET'])
def home():
    return SEARCH_PAGE_HTML, 200, {'Content-Type': 'text/html'}

@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('home'))
    
    # Convert the query to a URL-friendly format
    search_path = query.replace(' ', '-').lower()
    return redirect(f"/{search_path}")

@app.route("/<path:path>", methods=['POST', 'GET'])
def catch_all(path=""):
    if request.form:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", f"form data: {json.dumps(request.form)}")
    else:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", f"")

    prompt_content = prompt_content.replace("{{URL_PATH}}", path)
    
    response = model.generate_content(prompt_content)
    ai_data = response.text

    print(ai_data)

    content_type = ai_data.splitlines()[0]
    response_data = "\n".join(ai_data.splitlines()[1:])
    return response_data, 200, {'Content-Type': content_type}

if __name__ == '__main__':
    app.run(debug=True)