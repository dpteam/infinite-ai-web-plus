import google.generativeai as genai
import json
import re
from config import API_KEY, BASE_PROMPT
from templates import get_content_template

# Configure the generative AI with API key
genai.configure(api_key=API_KEY)

# Initialize the model with better parameters
model = genai.GenerativeModel(
    'models/gemini-2.0-flash',
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
)

def generate_content(path, form_data=None):
    """Generate content using the LLM."""
    print(f"Generating content for path: {path}")
    
    # Prepare the prompt
    if form_data:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", f"form data: {json.dumps(form_data)}")
    else:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", "")
    
    prompt_content = prompt_content.replace("{{URL_PATH}}", path)
    
    # Generate content
    print("Sending request to Gemini...")
    response = model.generate_content(prompt_content)
    ai_data = response.text
    
    # Extract content type and response data
    lines = ai_data.splitlines()
    if not lines:
        raise ValueError("Empty response from model")
    
    content_type = lines[0].strip()
    response_data = "\n".join(lines[1:])
    
    # For HTML responses, ensure we have rich CSS styling
    if content_type == "text/html":
        # Process HTML to enhance it with our standard CSS
        response_data = process_html_response(response_data, path)
        
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
    # Remove any initial 'web/' part
    if path.startswith("web/"):
        path = path[4:]
    
    # Replace dashes and slashes with spaces
    title = path.replace("-", " ").replace("/", " - ")
    
    # Capitalize words
    title = " ".join(word.capitalize() for word in title.split())
    
    return title
