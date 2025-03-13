import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")

# Define the root directory path - use absolute path to avoid issues
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT_DIR, "web")

# Create web directory if it doesn't exist
os.makedirs(WEB_DIR, exist_ok=True)

# Base prompt for content generation
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
