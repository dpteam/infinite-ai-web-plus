import google.generativeai as genai
import json
import re
import os
import base64
import traceback
import uuid
import mimetypes
from io import BytesIO
from config import API_KEY, BASE_PROMPT, IMAGE_PROMPT
from templates import get_content_template
# Add PIL import for fallback image generation
from PIL import Image, ImageDraw, ImageFont
# Import types from google.genai for newer client approach
from google import genai as google_genai
from google.genai import types

# Configure the legacy genai with API key
genai.configure(api_key=API_KEY)

# Initialize the model with better parameters for text content
model = genai.GenerativeModel(
    'models/gemini-2.0-flash-exp',
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
)

# Create a Google genai client for image generation
client = google_genai.Client(api_key=API_KEY)

def is_image_path(path):
    """Check if the path ends with an image file extension."""
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']
    return any(path.lower().endswith(ext) for ext in image_extensions)

def get_image_type_from_path(path):
    """Extract the image type from the path."""
    if path.lower().endswith('.png'):
        return 'image/png'
    elif path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
        return 'image/jpeg'
    elif path.lower().endswith('.gif'):
        return 'image/gif'
    elif path.lower().endswith('.webp'):
        return 'image/webp'
    elif path.lower().endswith('.bmp'):
        return 'image/bmp'
    else:
        return 'image/png'  # Default to PNG if extension not recognized

def create_fallback_image(prompt, image_format='PNG'):
    """Create a simple placeholder image with the prompt text."""
    print(f"Creating fallback image for prompt: {prompt}")
    
    # Create a simple colored background image
    width, height = 800, 600
    color = (240, 240, 250)  # Light blue-ish background
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    
    # Add text to the image
    try:
        # Try to use a system font
        font_size = 40
        try:
            font = ImageFont.truetype("Arial", font_size)
        except IOError:
            # Fallback to default font if Arial not available
            font = ImageFont.load_default()
            
        # Draw the prompt text
        text_color = (60, 60, 60)  # Dark gray text
        text = f"Image placeholder for: {prompt}"
        
        # Calculate text position (centered)
        text_width = draw.textlength(text, font=font)
        text_position = ((width - text_width) // 2, height // 2)
        
        # Draw the text
        draw.text(text_position, text, font=font, fill=text_color)
        
        # Add info text at the bottom
        info_text = "Generated fallback image"
        info_font_size = 24
        try:
            info_font = ImageFont.truetype("Arial", info_font_size)
        except IOError:
            info_font = ImageFont.load_default()
            
        info_text_width = draw.textlength(info_text, font=info_font)
        info_position = ((width - info_text_width) // 2, height - 50)
        draw.text(info_position, info_text, font=info_font, fill=(100, 100, 100))
        
    except Exception as e:
        print(f"Error adding text to fallback image: {str(e)}")
    
    # Save to BytesIO object
    img_byte_array = BytesIO()
    img.save(img_byte_array, format=image_format)
    img_byte_array.seek(0)
    
    # Return the binary data
    return img_byte_array.getvalue()

def decode_base64_image(image_data):
    """Properly decode base64 image data to binary format."""
    if isinstance(image_data, str):
        # Case 1: Data URL format (data:image/png;base64,ABC123...)
        if image_data.startswith('data:'):
            header, base64_data = image_data.split(',', 1)
            try:
                return base64.b64decode(base64_data)
            except Exception as e:
                print(f"Failed to decode Data URL: {str(e)}")
                return None
                
        # Case 2: Pure base64 string (just the encoded data)
        elif re.match(r'^[A-Za-z0-9+/=]+$', image_data.strip()):
            try:
                # Make sure padding is correct
                padding_needed = len(image_data) % 4
                if padding_needed:
                    image_data += '=' * (4 - padding_needed)
                return base64.b64decode(image_data)
            except Exception as e:
                print(f"Failed to decode pure base64: {str(e)}")
                return None
                
        # Case 3: Not recognizable as base64
        else:
            print("String data doesn't appear to be base64 encoded")
            return None
    else:
        # Already binary data
        return image_data

def print_response_details(response):
    """Print detailed information about the API response to help with debugging."""
    print("\n=== DETAILED API RESPONSE INFO ===")
    print(f"Response type: {type(response)}")
    
    # Show basic info about the response
    print("\nResponse structure:")
    
    # For client-based response
    if hasattr(response, 'candidates') and response.candidates:
        print(f"Has candidates: {len(response.candidates)} candidates found")
        for i, candidate in enumerate(response.candidates):
            if hasattr(candidate, 'content'):
                print(f"  Candidate {i} has content: {candidate.content is not None}")
                if candidate.content and hasattr(candidate.content, 'parts'):
                    print(f"    Content has {len(candidate.content.parts)} parts")
                    for j, part in enumerate(candidate.content.parts):
                        if hasattr(part, 'text') and part.text:
                            print(f"      Part {j} has text: {len(part.text)} chars")
                        if hasattr(part, 'inline_data'):
                            print(f"      Part {j} has inline_data: {part.inline_data is not None}")
                            if part.inline_data:
                                print(f"        MIME type: {part.inline_data.mime_type}")
                                print(f"        Data size: {len(part.inline_data.data) if part.inline_data.data else 0} bytes")
    
    # Print anything else available in the response that might be useful
    try:
        for attr in dir(response):
            if not attr.startswith('_') and not callable(getattr(response, attr)):
                value = getattr(response, attr)
                print(f"  {attr}: {type(value)}")
    except Exception as e:
        print(f"Error exploring response attributes: {str(e)}")
    
    print("=== END RESPONSE INFO ===\n")

def generate_image(prompt):
    """Generate an image using the Google genai client API with response modalities."""
    print(f"Generating image for prompt: {prompt}")
    
    # Remove file extension from prompt if present
    clean_prompt = os.path.splitext(prompt)[0].replace('-', ' ')
    
    # Format different prompts for image generation
    prompts = [
        f"Create a detailed visual image of a {clean_prompt}. This should be a high-quality image.",
        f"Generate a realistic image of {clean_prompt} with clear details.",
        f"Create a 3D rendered image of {clean_prompt} with detailed textures and lighting.",
        f"Design a professional photograph of {clean_prompt} with studio lighting."
    ]
    
    try:
        # Try each prompt until we get an image
        for idx, image_prompt in enumerate(prompts):
            print(f"\nAttempt {idx+1} with prompt: {image_prompt}")
            
            try:
                # Use the client to generate content with both text and image modalities
                response = client.models.generate_content(
                    model="models/gemini-2.0-flash-exp",
                    contents=image_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=['Text', 'Image'],
                        temperature=1.0,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=4096
                    )
                )
                
                print(f"Response received for attempt {idx+1}")
                
                # Check for candidates and parts containing image data
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and candidate.content:
                            for part in candidate.content.parts:
                                if hasattr(part, 'inline_data') and part.inline_data:
                                    print(f"Found image in response for attempt {idx+1}!")
                                    mime_type = part.inline_data.mime_type
                                    # Get the raw image data
                                    image_data = part.inline_data.data
                                    
                                    # Properly decode if it's base64
                                    decoded_data = decode_base64_image(image_data)
                                    if decoded_data:
                                        return decoded_data, mime_type
                                    else:
                                        print("Failed to decode image data, will try next prompt")
                
                # Debug response structure if no image was found
                print_response_details(response)
                
                # Check if we got a policy assessment or text-only response
                found_policy_text = False
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and candidate.content:
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    if 'policy' in part.text.lower():
                                        found_policy_text = True
                                        print(f"Received policy assessment text in attempt {idx+1}, trying next prompt")
                
                # If it's not a policy assessment and we still have no image, continue to next attempt
                if not found_policy_text:
                    print(f"No image found in response for attempt {idx+1}, but no policy assessment detected either")
                    
            except Exception as e:
                print(f"Error in attempt {idx+1}: {str(e)}")
                traceback.print_exc()
                continue
        
        # If we've tried all prompts and none worked, try one more creative approach
        try:
            final_prompt = f"Create a detailed visual image showing {clean_prompt}. Make it high quality, artistic and visually appealing."
            print("\nFinal attempt with special prompt:", final_prompt)
            
            response = client.models.generate_content(
                model="models/gemini-2.0-flash-exp",
                contents=final_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Image'],  # Force image-only response
                    temperature=1.0,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=4096
                )
            )
            
            # Check for image in final attempt
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                print("Found image in final attempt!")
                                mime_type = part.inline_data.mime_type
                                image_data = part.inline_data.data
                                
                                # Use our dedicated function to decode base64 data
                                decoded_data = decode_base64_image(image_data)
                                if decoded_data:
                                    return decoded_data, mime_type
                                else:
                                    print("Failed to decode image from final attempt")
            
            print("Final attempt failed to generate an image")
            print_response_details(response)
            
        except Exception as e:
            print(f"Error in final attempt: {str(e)}")
            traceback.print_exc()
        
        # If all attempts failed, create a fallback image
        print("\n⚠️ ALL IMAGE GENERATION ATTEMPTS FAILED")
        print("Creating fallback image instead")
        
        image_format = prompt.split('.')[-1].upper() if '.' in prompt else 'PNG'
        if image_format not in ['PNG', 'JPEG', 'JPG', 'GIF', 'WEBP', 'BMP']:
            image_format = 'PNG'
        
        # Create fallback image and determine mime type
        image_data = create_fallback_image(prompt, image_format)
        mime_type = f"image/{image_format.lower()}"
        if mime_type == "image/jpg":
            mime_type = "image/jpeg"
            
        return image_data, mime_type
        
    except Exception as e:
        print(f"\n❌ ERROR IN IMAGE GENERATION: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        
        # Create emergency fallback image
        try:
            print("Creating emergency fallback image due to exception")
            image_format = prompt.split('.')[-1].upper() if '.' in prompt else 'PNG'
            if image_format not in ['PNG', 'JPEG', 'JPG', 'GIF', 'WEBP', 'BMP']:
                image_format = 'PNG'
                
            image_data = create_fallback_image(prompt, image_format)
            mime_type = f"image/{image_format.lower()}"
            if mime_type == "image/jpg":
                mime_type = "image/jpeg"
                
            return image_data, mime_type
        except Exception as fallback_error:
            print(f"Even fallback image creation failed: {str(fallback_error)}")
            # Re-raise the original error
            raise e

def save_base64_to_file(image_data, mime_type):
    """Save base64 image data to a file and return the file path."""
    # Create static/images directory if it doesn't exist
    image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
    os.makedirs(image_dir, exist_ok=True)
    
    # Determine file extension from mime_type
    extension = mimetypes.guess_extension(mime_type)
    if not extension:
        # Default to .png if mime_type doesn't match known extensions
        extension = '.png'
    
    # Generate a unique filename
    filename = f"{uuid.uuid4().hex}{extension}"
    filepath = os.path.join(image_dir, filename)
    
    try:
        # If image_data is already bytes, write it directly
        if isinstance(image_data, bytes):
            with open(filepath, 'wb') as f:
                f.write(image_data)
            print(f"Saved image to {filepath}")
            return f"/static/images/{filename}"
        
        # If image_data is base64 string
        elif isinstance(image_data, str):
            # Handle data URLs (data:image/png;base64,...)
            if image_data.startswith('data:'):
                header, base64_data = image_data.split(',', 1)
                image_bytes = base64.b64decode(base64_data)
            # Handle pure base64 strings
            elif re.match(r'^[A-Za-z0-9+/=]+$', image_data.strip()):
                # Fix padding if needed
                padding_needed = len(image_data) % 4
                if padding_needed:
                    image_data += '=' * (4 - padding_needed)
                image_bytes = base64.b64decode(image_data)
            else:
                # Not a base64 string, encode and write as text
                image_bytes = image_data.encode('utf-8')
            
            # Write the decoded data to file
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            print(f"Saved decoded image to {filepath}")
            return f"/static/images/{filename}"
        
        else:
            print(f"Unexpected image data type: {type(image_data)}")
            return None
            
    except Exception as e:
        print(f"Error saving image to file: {str(e)}")
        traceback.print_exc()
        return None

def generate_content(path, form_data=None):
    """Generate content using the LLM."""
    print(f"Generating content for path: {path}")
    
    # If the path ends with an image extension, we ONLY generate an image, not HTML
    if is_image_path(path):
        print(f"Detected image path: {path}")
        # Extract prompt from the path
        prompt_from_path = path.rsplit('/', 1)[-1]
        prompt_from_path = os.path.splitext(prompt_from_path)[0].replace('-', ' ')
        
        # Use that as the basis for image generation
        image_prompt = f"{prompt_from_path}"
        
        # Generate an image
        try:
            image_data, mime_type = generate_image(image_prompt)
            print(f"Returning binary image data with MIME type: {mime_type}")
            
            # Return the binary image data directly
            return mime_type, image_data
        except Exception as e:
            print(f"Failed to generate image: {str(e)}")
            # If image generation fails, we'll generate a fallback HTML that explains the error
            error_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Generation Failed</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #ea4335; }}
        .home-link {{ margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>Image Generation Failed</h1>
    <p>There was an error generating the image for: <strong>{path}</strong></p>
    <p>Error details: {str(e)}</p>
    <div class="home-link">
        <a href="../..">Back to Search</a>
    </div>
</body>
</html>"""
            return "text/html", error_html
    
    # For non-image requests, generate HTML content as usual
    if form_data:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", f"form data: {json.dumps(form_data)}")
    else:
        prompt_content = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", "")
    
    prompt_content = prompt_content.replace("{{URL_PATH}}", path)
    
    # Generate text content
    print("Sending request to Gemini for text content...")
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
        
        # Add an image to the HTML content
        try:
            response_data = add_image_to_html(response_data, path)
        except Exception as e:
            print(f"Failed to add image to HTML: {str(e)}")
            # Continue without the image if it fails
    
    return content_type, response_data

def add_image_to_html(html_content, path):
    """Add an AI-generated image to the HTML content."""
    # Extract a relevant prompt from the path
    topic = path.replace('-', ' ').replace('/', ' ').strip()
    image_prompt = f"{topic}"
    
    try:
        # Generate the image
        image_data, mime_type = generate_image(image_prompt)
        
        # Save the image data to a file
        image_path = save_base64_to_file(image_data, mime_type)
        
        if image_path:
            # Create an image tag with the file path
            img_tag = f'<img src="{image_path}" alt="{topic}" style="max-width: 100%; height: auto; margin: 20px auto; display: block; border-radius: 5px;">'
            
            # Insert the image after the first heading
            if "<h1" in html_content:
                parts = html_content.split("</h1>", 1)
                if len(parts) == 2:
                    html_content = parts[0] + "</h1>" + img_tag + parts[1]
                else:
                    # Fallback - append image at the end of the body
                    html_content = html_content.replace("</body>", img_tag + "</body>")
            else:
                # Fallback - append image at the end of the body
                html_content = html_content.replace("</body>", img_tag + "</body>")
        
        return html_content
    except Exception as e:
        print(f"Error adding image to HTML: {str(e)}")
        return html_content

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
