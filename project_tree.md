# Infinite AI Web - Project Structure

This document outlines the structure of the Infinite AI Web project after refactoring.

## Project Tree

```
infinite-ai-web/
├── infinite_web.py        # Main entry point for the application
├── config.py              # Configuration settings and constants
├── models.py              # LLM integration and content generation
├── templates.py           # HTML templates and UI components
├── utils.py               # Helper functions for file operations
├── views.py               # Flask routes and request handling
├── index.html             # Generated index of saved searches
├── web/                   # Directory for saved HTML files
│   ├── [topic]/           # Topic-specific directories
│   └── ...                # Generated HTML files
└── .env                   # Environment variables (API keys)
```

## File Descriptions

### infinite_web.py
The main entry point for the application. Creates and runs the Flask application.

### config.py
Contains configuration settings, constants, and directory setup.

### models.py
Handles integration with the Gemini AI model and content generation.

### templates.py
Stores HTML templates for the search page and other UI components.

### utils.py
Provides helper functions for file operations and index generation.

### views.py
Contains all Flask routes and request handling logic.

### index.html
Generated list of all saved searches, linked to their respective content.

### web/
Directory containing all generated HTML content organized by topic.

## Running the Application

1. Ensure you have the required dependencies installed:
   ```
   pip install flask google-generativeai python-dotenv
   ```

2. Set up your API key in `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```
   python infinite_web.py
   ```

4. Open a browser and navigate to http://localhost:5000

## Deployment

When deploying to GitHub Pages, the application uses relative URLs to ensure links work correctly both locally and when hosted.
