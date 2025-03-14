from flask import Flask
import os
from config import ROOT_DIR
from views import setup_routes
from utils import generate_index_html

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    setup_routes(app)
    return app

if __name__ == '__main__':
    # Print directory information
    from config import ROOT_DIR, WEB_DIR
    print(f"Root directory path: {ROOT_DIR}")
    print(f"Web directory path: {WEB_DIR}")
    
    # Create index.html if it doesn't exist yet
    if not os.path.exists(os.path.join(ROOT_DIR, "index.html")):
        print("Generating initial index.html...")
        generate_index_html()
    
    # Create and run the app
    app = create_app()
    print("Starting Flask application...")
    app.run(debug=True)