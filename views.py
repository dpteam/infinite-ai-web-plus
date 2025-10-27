from flask import request, redirect, url_for, Response
import os
from config import ROOT_DIR, WEB_DIR
from models import generate_content
from utils import save_to_cache, load_from_cache, generate_index_html, is_cached
from templates import SEARCH_PAGE_HTML, generate_error_page

def setup_routes(app):
    @app.route("/", methods=['GET'])
    def home():
        # Check if we have cached home page in web directory
        content_type, cached_content = load_from_cache('index')
        if cached_content:
            return cached_content, 200, {'Content-Type': content_type}
        
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
        # Check cache first
        content_type, cached_content = load_from_cache('index')
        if cached_content:
            return cached_content, 200, {'Content-Type': content_type}
        
        # Generate an up-to-date index.html and serve it
        generate_index_html()
        with open(os.path.join(ROOT_DIR, "index.html"), "r", encoding="utf-8") as f:
            content = f.read()
        
        # Cache the index content
        save_to_cache('index', 'text/html', content)
        
        return content, 200, {'Content-Type': 'text/html'}

    @app.route("/<path:path>", methods=['POST', 'GET'])
    def catch_all(path=""):
        print(f"Handling request for path: {path}")
        
        # Special handling for index.html
        if path == "index.html":
            return redirect(url_for('index'))
        
        # Check if we should use cache (default: yes)
        use_cache = request.args.get('nocache', '0') == '0'
        
        # First check cache
        if use_cache:
            content_type, cached_content = load_from_cache(path)
            if cached_content:
                print(f"Serving from cache: {path}")
                return cached_content, 200, {'Content-Type': content_type}
        
        # Then check if file exists in web directory (legacy support)
        web_file_path = os.path.join(WEB_DIR, path + ".html")
        if os.path.exists(web_file_path):
            print(f"Serving existing file from web directory: {web_file_path}")
            with open(web_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Cache this content for future requests
            if use_cache:
                save_to_cache(path, 'text/html', content)
            
            return content, 200, {'Content-Type': 'text/html'}
        
        # Then check if file exists in root directory (for backward compatibility)
        root_file_path = os.path.join(ROOT_DIR, path + ".html")
        if os.path.exists(root_file_path):
            print(f"Serving existing file from root directory: {root_file_path}")
            with open(root_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Cache this content for future requests
            if use_cache:
                save_to_cache(path, 'text/html', content)
            
            return content, 200, {'Content-Type': 'text/html'}
        
        # Generate content for any path that hasn't been found
        print(f"No existing file found for {path}, generating rich content...")
        
        # Get form data if available
        form_data = request.form if request.form else None
        
        # Generate content with enhanced settings
        try:
            content_type, response_data = generate_content(path, form_data, use_cache=use_cache)
            
            return response_data, 200, {'Content-Type': content_type}
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            error_page = generate_error_page(path, e)
            return error_page, 500, {'Content-Type': 'text/html'}

    @app.route("/api/cache/clear/<path:path>")
    def clear_cache_path(path):
        """Clear cache for specific path"""
        from utils import clear_cache_for_path
        success = clear_cache_for_path(path)
        if success:
            return f"Cache cleared for: {path}", 200
        else:
            return f"Error clearing cache for: {path}", 500

    @app.route("/api/cache/clear")
    def clear_all_cache():
        """Clear all cache"""
        from web_folder_cleaner import clean_web_folder
        try:
            clean_web_folder()
            return "All cache cleared successfully", 200
        except Exception as e:
            return f"Error clearing cache: {str(e)}", 500

    @app.route("/api/cache/stats")
    def cache_stats():
        """Get cache statistics"""
        from utils import get_cache_stats
        stats = get_cache_stats()
        return {
            'status': 'success',
            'data': stats
        }, 200