# HTML template for the search page
SEARCH_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INFINITE AI WEB</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            position: relative;
        }
        .logo {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 30px;
            color: #4285f4;
            text-align: center;
        }
        .search-container {
            width: 100%;
            max-width: 584px;
        }
        .search-bar {
            width: 100%;
            padding: 12px 20px;
            margin: 8px 0;
            box-sizing: border-box;
            border: 1px solid #dfe1e5;
            border-radius: 24px;
            font-size: 16px;
            outline: none;
        }
        .search-bar:hover, .search-bar:focus {
            box-shadow: 0 1px 6px rgba(32,33,36,.28);
            border-color: rgba(223,225,229,0);
        }
        .search-button {
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
        }
        .search-button:hover {
            box-shadow: 0 1px 1px rgba(0,0,0,.1);
            background-color: #f8f9fa;
            border: 1px solid #dadce0;
            color: #202124;
        }
        .buttons {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 10px;
        }
        .infinite {
            background: linear-gradient(to right, #4285f4, #ea4335, #fbbc05, #34a853, #4285f4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 800% 100%;
            animation: gradient 10s linear infinite;
        }
        @keyframes gradient {
            0% {
                background-position: 0% 0%;
            }
            100% {
                background-position: 800% 0%;
            }
        }
        .footer {
            position: fixed;
            bottom: 20px;
            text-align: center;
            width: 100%;
            font-size: 14px;
            color: #70757a;
        }
        .footer a {
            color: #70757a;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .links-container {
            position: absolute;
            top: 20px;
            right: 20px;
        }
        .links-container a {
            color: #70757a;
            text-decoration: none;
            font-size: 14px;
        }
        .links-container a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="links-container">
        <a href="index">Saved Searches</a>
    </div>
    <div class="logo"><span class="infinite">INFINITE AI WEB</span></div>
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
