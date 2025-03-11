from flask import Flask, request
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
model = genai.GenerativeModel('models/gemini-1.5-pro')


app = Flask(__name__)


BASE_PROMPT = """Create a response document with content that matches the following URL path: 
    `{{URL_PATH}}`
The first line is the Content-Type of the response.
The following lines is the returned data.
In case of a html response, add relative href links with to related topics.
{{OPTIONAL_DATA}}
Content-Type:
"""

@app.route("/", methods = ['POST', 'GET'])
@app.route("/<path:path>", methods = ['POST', 'GET'])
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
    app.run()