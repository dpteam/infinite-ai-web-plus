from flask import request, redirect, url_for, Response
import os
from config import ROOT_DIR
from models import generate_content, is_image_path, get_image_type_from_path
from utils import save_html_response, generate_index_html, save_image_response
from templates import SEARCH_PAGE_HTML, generate_error_page

def setup_routes(app):
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
        # Use relative path (no leading slash)
        return redirect(f"{search_path}")

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
        
        # Check if this is a request for an image file
        if is_image_path(path):
            print(f"Image path detected: {path}")
            
            # First check if the image already exists
            from config import WEB_DIR
            image_file_path = os.path.join(WEB_DIR, path)
            if os.path.exists(image_file_path):
                print(f"Serving existing image file: {image_file_path}")
                # Read the binary image data
                with open(image_file_path, "rb") as f:
                    image_data = f.read()
                # Get the appropriate MIME type
                mime_type = get_image_type_from_path(path)
                # Return the binary data with the correct Content-Type
                return Response(image_data, mimetype=mime_type)
            
            # No existing image, so we need to generate one
            try:
                content_type, response_data = generate_content(path, None)
                
                # If we got an image back
                if content_type.startswith('image/'):
                    # Save the image for future requests
                    save_image_response(path, response_data, content_type)
                    # Return the binary data with the correct Content-Type
                    return Response(response_data, mimetype=content_type)
                else:
                    # Something went wrong - we got HTML instead of an image
                    # (this will be error HTML from the generate_content function)
                    return response_data, 200, {'Content-Type': content_type}
                    
            except Exception as e:
                print(f"Error generating image: {str(e)}")
                error_page = generate_error_page(path, e)
                return error_page, 500, {'Content-Type': 'text/html'}
        
        # For non-image paths, check if HTML file already exists in web directory
        from config import WEB_DIR
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
        
        # Get form data if available
        form_data = request.form if request.form else None
        
        # Generate content with enhanced settings
        try:
            content_type, response_data = generate_content(path, form_data)
            
            # Handle different content types
            if content_type.startswith('image/'):
                # For image responses, save the binary image data
                save_image_response(path, response_data, content_type)
                # Return the binary data with the correct Content-Type
                return Response(response_data, mimetype=content_type)
            elif content_type == "text/html":
                # For HTML responses, save the HTML content
                save_html_response(path, response_data)
                return response_data, 200, {'Content-Type': content_type}
            else:
                # For any other content types
                return response_data, 200, {'Content-Type': content_type}
                
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            error_page = generate_error_page(path, e)
            return error_page, 500, {'Content-Type': 'text/html'}
