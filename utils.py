import os
import json
from config import WEB_DIR

def save_to_cache(path, content_type, content):
    """Save generated content to cache in web directory"""
    try:
        # Normalize path
        if path.startswith('/'):
            path = path[1:]
        if path == '':
            path = 'index'
        
        # Determine file path based on content type and path structure
        if '/' in path:
            # For nested paths like "games/stronghold/units"
            dir_path = os.path.join(WEB_DIR, os.path.dirname(path))
            file_name = os.path.basename(path)
            
            # Create directory if it doesn't exist
            os.makedirs(dir_path, exist_ok=True)
            
            # Determine file extension
            if content_type == 'text/html':
                file_path = os.path.join(dir_path, f"{file_name}.html")
            elif content_type == 'application/json':
                file_path = os.path.join(dir_path, f"{file_name}.json")
            elif content_type.startswith('text/'):
                file_path = os.path.join(dir_path, f"{file_name}.txt")
            else:
                file_path = os.path.join(dir_path, file_name)
        else:
            # For top-level paths like "programming"
            if content_type == 'text/html':
                file_path = os.path.join(WEB_DIR, f"{path}.html")
            elif content_type == 'application/json':
                file_path = os.path.join(WEB_DIR, f"{path}.json")
            elif content_type.startswith('text/'):
                file_path = os.path.join(WEB_DIR, f"{path}.txt")
            else:
                file_path = os.path.join(WEB_DIR, path)
        
        # Save content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Content cached to: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error caching content: {e}")
        return False

def load_from_cache(path):
    """Load content from cache if exists"""
    try:
        # Normalize path
        if path.startswith('/'):
            path = path[1:]
        if path == '':
            path = 'index'
        
        # Try different extensions and locations
        possible_paths = []
        
        if '/' in path:
            # For nested paths
            dir_path = os.path.join(WEB_DIR, os.path.dirname(path))
            file_name = os.path.basename(path)
            possible_paths.extend([
                os.path.join(dir_path, f"{file_name}.html"),
                os.path.join(dir_path, f"{file_name}.json"),
                os.path.join(dir_path, f"{file_name}.txt"),
                os.path.join(dir_path, file_name),
                os.path.join(dir_path, "index.html")  # directory index
            ])
        else:
            # For top-level paths
            possible_paths.extend([
                os.path.join(WEB_DIR, f"{path}.html"),
                os.path.join(WEB_DIR, f"{path}.json"),
                os.path.join(WEB_DIR, f"{path}.txt"),
                os.path.join(WEB_DIR, path),
                os.path.join(WEB_DIR, path, "index.html")  # directory index
            ])
        
        for file_path in possible_paths:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine content type from extension
                if file_path.endswith('.html'):
                    content_type = 'text/html'
                elif file_path.endswith('.json'):
                    content_type = 'application/json'
                elif file_path.endswith('.txt'):
                    content_type = 'text/plain'
                else:
                    content_type = 'text/html'  # default
                
                print(f"Content loaded from cache: {file_path}")
                return content_type, content
        
        return None, None
        
    except Exception as e:
        print(f"Error loading from cache: {e}")
        return None, None

def is_cached(path):
    """Check if content is cached"""
    content_type, content = load_from_cache(path)
    return content is not None

def clear_cache_for_path(path):
    """Clear cache for specific path"""
    try:
        # Normalize path
        if path.startswith('/'):
            path = path[1:]
        if path == '':
            path = 'index'
        
        # Possible cache file paths
        possible_paths = []
        
        if '/' in path:
            # For nested paths
            dir_path = os.path.join(WEB_DIR, os.path.dirname(path))
            file_name = os.path.basename(path)
            possible_paths.extend([
                os.path.join(dir_path, f"{file_name}.html"),
                os.path.join(dir_path, f"{file_name}.json"),
                os.path.join(dir_path, f"{file_name}.txt"),
                os.path.join(dir_path, file_name),
            ])
        else:
            # For top-level paths
            possible_paths.extend([
                os.path.join(WEB_DIR, f"{path}.html"),
                os.path.join(WEB_DIR, f"{path}.json"),
                os.path.join(WEB_DIR, f"{path}.txt"),
                os.path.join(WEB_DIR, path),
            ])
        
        # Also add directory index paths
        possible_paths.append(os.path.join(WEB_DIR, path, "index.html"))
        
        removed_count = 0
        for file_path in possible_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed cache: {file_path}")
                removed_count += 1
        
        # Also remove directory if empty
        dir_path = os.path.join(WEB_DIR, path)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            try:
                os.rmdir(dir_path)
                print(f"Removed empty directory: {dir_path}")
            except OSError:
                pass  # Directory not empty
        
        return removed_count > 0
        
    except Exception as e:
        print(f"Error clearing cache for path: {e}")
        return False

def get_cache_stats():
    """Get cache statistics"""
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(WEB_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            total_files += 1
            total_size += os.path.getsize(file_path)
    
    return {
        'total_files': total_files,
        'total_size_bytes': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'cache_location': WEB_DIR
    }

def save_html_response(path, content):
    """Legacy function - now uses save_to_cache"""
    return save_to_cache(path, 'text/html', content)

def generate_index_html():
    """Generate the index.html file in root directory (legacy)"""
    index_content = """<!DOCTYPE html>
<html>
<head>
    <title>AI Generated Content Index</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; }
        a { text-decoration: none; color: #0066cc; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>AI Generated Content Index</h1>
    <p>This is an auto-generated index of all created pages.</p>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/search">Search</a></li>
    </ul>
    <p>Use the search functionality to generate new content.</p>
</body>
</html>"""
    
    index_path = os.path.join(os.path.dirname(WEB_DIR), "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print("Generated index.html")