import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AI Provider configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "openrouter")  # openrouter, openai, gemini

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-70b-instruct")

# OpenAI-compatible configuration (for LM Studio, LocalAI, etc.)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "default-key")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://192.168.1.222:1234/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "local-model")

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-exp")

# Common settings
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.95"))

# Define the root directory path - use absolute path to avoid issues
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT_DIR, "web")

# Create web directory if it doesn't exist
os.makedirs(WEB_DIR, exist_ok=True)

# Application title
APP_TITLE = "INFINITE AI WEB v1"

# Enhanced base prompt for richer content generation
BASE_PROMPT = """Generate a comprehensive and detailed response for the URL path: `{{URL_PATH}}`

The first line must be the Content-Type (use 'text/html' for HTML responses).
All subsequent lines should contain ONLY the renderable content with NO explanatory text, examples, or instructions.

For HTML responses:
- Include proper HTML structure (doctype, html, head, body tags)
- Add a relevant title and content based on the URL path
- Create rich, detailed content with multiple paragraphs explaining the topic thoroughly
- Include at least 3-4 well-developed sections with headings
- Add relevant details, examples, code snippets, or data tables when appropriate
- Use proper semantic HTML (headings, lists, tables, etc.) for structure
- Include a visually appealing layout with appropriate CSS styling
- IMPORTANT: When creating links to related topics, always use the full path that includes the current context.
  For example, if the current URL is "/stronghold-crusader" and you're linking to "units", 
  use "/stronghold-crusader/units" instead of just "/units".
- Create a "Related Topics" section at the end, but ONLY after providing substantial content
- Ensure all relative links maintain the parent context of the current URL path
- Ensure the HTML is valid and immediately renderable in a browser
- Focus on providing valuable, educational content rather than just navigation

{{OPTIONAL_DATA}}
Content-Type:
"""

def get_ai_config():
    """Get configuration for the current AI provider"""
    return {
        "openrouter": {
            "name": "OpenRouter",
            "api_key": OPENROUTER_API_KEY,
            "base_url": OPENROUTER_BASE_URL,
            "model": OPENROUTER_MODEL
        },
        "openai": {
            "name": "OpenAI-compatible",
            "api_key": OPENAI_API_KEY,
            "base_url": OPENAI_BASE_URL,
            "model": OPENAI_MODEL
        },
        "gemini": {
            "name": "Google Gemini",
            "api_key": GEMINI_API_KEY,
            "model": GEMINI_MODEL
        }
    }[AI_PROVIDER]