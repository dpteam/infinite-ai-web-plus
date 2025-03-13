from config import APP_TITLE

# HTML template for the search page
SEARCH_PAGE_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{APP_TITLE}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            position: relative;
        }}
        .logo {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 30px;
            color: #4285f4;
            text-align: center;
        }}
        .search-container {{
            width: 100%;
            max-width: 584px;
        }}
        .search-bar {{
            width: 100%;
            padding: 12px 20px;
            margin: 8px 0;
            box-sizing: border-box;
            border: 1px solid #dfe1e5;
            border-radius: 24px;
            font-size: 16px;
            outline: none;
        }}
        .search-bar:hover, .search-bar:focus {{
            box-shadow: 0 1px 6px rgba(32,33,36,.28);
            border-color: rgba(223,225,229,0);
        }}
        .search-button {{
            background-color: #f8f9fa;
            border: 1px solid #f8f9fa;
            border-radius: 4px;
            color: #3c4043;
            font-family: Arial, sans-serif;
            font-size: 14px;
            margin: 11px 4px;
            padding: 0 16px;
            line-height: 27px;
            height: 36px;
            min-width: 54px;
            text-align: center;
            cursor: pointer;
            user-select: none;
        }}
        .search-button:hover {{
            box-shadow: 0 1px 1px rgba(0,0,0,.1);
            background-color: #f8f9fa;
            border: 1px solid #dadce0;
            color: #202124;
        }}
        .buttons {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 10px;
        }}
        .infinite {{
            background: linear-gradient(to right, #4285f4, #ea4335, #fbbc05, #34a853, #4285f4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 800% 100%;
            animation: gradient 10s linear infinite;
        }}
        @keyframes gradient {{
            0% {{
                background-position: 0% 0%;
            }}
            100% {{
                background-position: 800% 0%;
            }}
        }}
        .footer {{
            position: fixed;
            bottom: 20px;
            text-align: center;
            width: 100%;
            font-size: 14px;
            color: #70757a;
        }}
        .footer a {{
            color: #70757a;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        .links-container {{
            position: absolute;
            top: 20px;
            right: 20px;
        }}
        .links-container a {{
            color: #70757a;
            text-decoration: none;
            font-size: 14px;
        }}
        .links-container a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="links-container">
        <a href="index">Saved Searches</a>
    </div>
    <div class="logo"><span class="infinite">{APP_TITLE}</span></div>
    <div class="search-container">
        <form action="search" method="GET">
            <input type="text" class="search-bar" name="query" placeholder="Search the web..." autofocus>
            <div class="buttons">
                <button type="submit" class="search-button">Search</button>
            </div>
        </form>
    </div>
    <div class="footer">
        made with 🍋 by Lime1
    </div>
</body>
</html>
"""

def generate_error_page(path, error):
    """Generate an error page for failed requests."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Error - INFINITE AI WEB</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #ea4335; }}
            .home-link {{ margin-top: 30px; }}
        </style>
    </head>
    <body>
        <h1>Error Generating Content</h1>
        <p>There was an error generating content for: <strong>{path}</strong></p>
        <p>Error details: {str(error)}</p>
        <div class="home-link">
            <a href=".">Back to Search</a>
        </div>
    </body>
    </html>
    """

# Adding base CSS for generated content pages
CONTENT_PAGE_CSS = """
<style>
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
    }
    header {
        margin-bottom: 30px;
        border-bottom: 1px solid #eaeaea;
        padding-bottom: 20px;
    }
    h1 {
        color: #1a73e8;
        font-size: 2.5em;
    }
    h2 {
        color: #1967d2;
        font-size: 1.8em;
        margin-top: 40px;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 10px;
    }
    h3 {
        color: #174ea6;
        font-size: 1.4em;
        margin-top: 30px;
    }
    p {
        margin: 16px 0;
        font-size: 16px;
    }
    code {
        background-color: #f5f5f5;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }
    pre {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 6px;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        margin: 20px 0;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 25px 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    ul, ol {
        margin: 20px 0 20px 20px;
    }
    li {
        margin: 8px 0;
    }
    blockquote {
        border-left: 5px solid #e0e0e0;
        padding-left: 20px;
        margin: 20px 0;
        color: #666;
        font-style: italic;
    }
    .note {
        background-color: #e7f3fe;
        border-left: 6px solid #2196F3;
        padding: 10px;
        margin: 20px 0;
    }
    .warning {
        background-color: #fff3cd;
        border-left: 6px solid #ffc107;
        padding: 10px;
        margin: 20px 0;
    }
    .related-topics {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #eaeaea;
    }
    .related-topics h2 {
        color: #5f6368;
        font-size: 1.5em;
        margin-bottom: 20px;
    }
    .related-topics ul {
        margin-left: 0;
        padding-left: 0;
        list-style-type: none;
    }
    .related-topics li {
        margin: 10px 0;
    }
    .related-topics a {
        text-decoration: none;
        color: #1a73e8;
        padding: 8px 16px;
        border-radius: 4px;
        display: inline-block;
        transition: background-color 0.2s;
    }
    .related-topics a:hover {
        background-color: #f1f3f4;
        text-decoration: underline;
    }
    .back-to-search {
        display: block;
        margin-top: 40px;
        text-align: center;
    }
    .back-to-search a {
        text-decoration: none;
        color: #5f6368;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 14px;
        transition: background-color 0.2s;
    }
    .back-to-search a:hover {
        background-color: #f1f3f4;
        text-decoration: underline;
    }
</style>
"""

def get_content_template():
    """Returns the base template with CSS for content pages"""
    return CONTENT_PAGE_CSS
