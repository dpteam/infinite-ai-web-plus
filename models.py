import google.generativeai as genai
import json
from config import API_KEY, BASE_PROMPT

# Configure the generative AI with API key
genai.configure(api_key=API_KEY)

# Initialize the model
model = genai.GenerativeModel('models/gemini-2.0-flash')

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
    response = model.generate_content(prompt_content)
    ai_data = response.text
    
    # Extract content type and response data
    lines = ai_data.splitlines()
    if not lines:
        raise ValueError("Empty response from model")
    
    content_type = lines[0].strip()
    response_data = "\n".join(lines[1:])
    
    return content_type, response_data
