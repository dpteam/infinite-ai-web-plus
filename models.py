import requests
import json
import re
from config import (
    AI_PROVIDER, BASE_PROMPT, MAX_TOKENS, TEMPERATURE, TOP_P,
    get_ai_config
)
from templates import get_content_template
from utils import save_to_cache

# Try to import Gemini, but make it optional
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

def generate_content(path, form_data=None, use_cache=True):
    """Generate content using the configured AI provider."""
    print(f"Using AI provider: {AI_PROVIDER}")
    
    # Prepare the prompt
    if form_data:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", f"form data: {json.dumps(form_data)}")
    else:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", "")
    
    prompt_content = prompt_content.replace("{{URL_PATH}}", path)
    
    # Route to the appropriate provider
    if AI_PROVIDER == "openrouter":
        content_type, response_data = generate_openrouter(prompt_content)
    elif AI_PROVIDER == "openai":
        content_type, response_data = generate_openai(prompt_content)
    elif AI_PROVIDER == "gemini":
        content_type, response_data = generate_gemini(prompt_content)
    else:
        raise ValueError(f"Unsupported AI provider: {AI_PROVIDER}")
    
    # For HTML responses, ensure we have rich CSS styling
    if content_type == "text/html":
        response_data = process_html_response(response_data, path)
    
    # Save to cache if caching is enabled
    if use_cache:
        save_to_cache(path, content_type, response_data)
        
    return content_type, response_data

def generate_openrouter(prompt):
    """Generate content using OpenRouter API."""
    config = get_ai_config()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
        "HTTP-Referer": "https://your-site.com",
        "X-Title": "Infinite AI Web"
    }
    
    data = {
        "model": config["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_p": TOP_P
    }
    
    print(f"Sending request to OpenRouter API for model: {config['model']}")
    response = requests.post(f"{config['base_url']}/chat/completions", 
                           headers=headers, json=data, timeout=120)
    response.raise_for_status()
    response_data = response.json()
    
    ai_data = response_data["choices"][0]["message"]["content"]
    return extract_content_type_and_data(ai_data)

def generate_openai(prompt):
    """Generate content using OpenAI-compatible API."""
    config = get_ai_config()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}"
    }
    
    data = {
        "model": config["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_p": TOP_P
    }
    
    print(f"Sending request to OpenAI-compatible API at {config['base_url']}")
    response = requests.post(f"{config['base_url']}/chat/completions", 
                           headers=headers, json=data, timeout=120)
    response.raise_for_status()
    response_data = response.json()
    
    ai_data = response_data["choices"][0]["message"]["content"]
    return extract_content_type_and_data(ai_data)

def generate_gemini(prompt):
    """Generate content using Google Gemini API."""
    if not GEMINI_AVAILABLE:
        raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
    
    config = get_ai_config()
    
    # Configure Gemini
    genai.configure(api_key=config['api_key'])
    model = genai.GenerativeModel(config['model'])
    
    print(f"Sending request to Gemini API for model: {config['model']}")
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "max_output_tokens": MAX_TOKENS,
        }
    )
    
    return extract_content_type_and_data(response.text)

def extract_content_type_and_data(ai_data):
    """Extract content type and data from AI response."""
    lines = ai_data.splitlines()
    if not lines:
        raise ValueError("Empty response from model")
    
    content_type = lines[0].strip()
    response_data = "\n".join(lines[1:])
    
    return content_type, response_data

def process_html_response(html_content, path):
    """Process HTML response to ensure rich styling and content."""
    # Check if the HTML already has a proper structure
    if "<html" not in html_content.lower():
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{format_title(path)}</title>
    {get_content_template()}
</head>
<body>
    {html_content}
    <div class="back-to-search">
        <a href="../..">Back to Search</a>
    </div>
</body>
</html>"""
    
    # If it has HTML structure but missing our CSS, add it
    if "<style" not in html_content.lower():
        html_content = html_content.replace("</head>", f"{get_content_template()}\n</head>")
    
    # Add back to search link if it's not there
    if "back-to-search" not in html_content.lower() and "</body>" in html_content:
        back_link = '\n<div class="back-to-search">\n<a href="../..">Back to Search</a>\n</div>\n'
        html_content = html_content.replace("</body>", f"{back_link}</body>")
    
    return html_content

def format_title(path):
    """Format a URL path into a readable page title."""
    if path.startswith("web/"):
        path = path[4:]
    
    title = path.replace("-", " ").replace("/", " - ")
    title = " ".join(word.capitalize() for word in title.split())
    
    return title