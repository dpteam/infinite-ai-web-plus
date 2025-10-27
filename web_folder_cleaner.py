import os
import shutil
from pathlib import Path
import sys

def check_required_packages():
    missing_packages = []
    
    # Check for python-dotenv
    try:
        import dotenv
    except ImportError:
        missing_packages.append("python-dotenv")
    
    # Check for requests
    try:
        import requests
    except ImportError:
        missing_packages.append("requests")
    
    # Check for google-generativeai only if using Gemini
    from config import AI_PROVIDER
    if AI_PROVIDER == "gemini":
        try:
            import google.generativeai
        except ImportError:
            missing_packages.append("google-generativeai")
    
    if missing_packages:
        print("Missing required packages. Please install:")
        for package in missing_packages:
            print(f"  pip install {package}")
        print("\nAfter installing, run this script again.")
        return False
    
    return True

def clean_web_folder():
    """Clear the entire web cache directory"""
    from config import WEB_DIR
    web_folder = Path(WEB_DIR)
    
    if not web_folder.exists():
        print(f"Web folder not found at {web_folder}")
        return False
    
    print(f"Cleaning contents of {web_folder}")
    
    # List all items in the web folder
    for item in web_folder.iterdir():
        try:
            if item.is_file():
                os.remove(item)
                print(f"Removed file: {item.name}")
            elif item.is_dir():
                shutil.rmtree(item)
                print(f"Removed directory: {item.name}")
        except Exception as e:
            print(f"Error removing {item.name}: {e}")
    
    print(f"Finished cleaning {web_folder}")
    return True

def list_available_models():
    """List available models for the current provider"""
    from config import AI_PROVIDER, get_ai_config
    import requests
    
    config = get_ai_config()
    
    if AI_PROVIDER == "openrouter":
        list_openrouter_models(config)
    elif AI_PROVIDER == "openai":
        list_openai_models(config)
    elif AI_PROVIDER == "gemini":
        list_gemini_models(config)

def list_openrouter_models(config):
    """List OpenRouter models"""
    headers = {"Authorization": f"Bearer {config['api_key']}"}
    
    try:
        print("\nFetching available models from OpenRouter...")
        response = requests.get(f"{config['base_url']}/models", headers=headers)
        response.raise_for_status()
        models_data = response.json()
        
        print(f"\nAvailable OpenRouter models:")
        if 'data' in models_data:
            for model in models_data['data']:
                print(f"- {model['id']}")
                if 'name' in model:
                    print(f"  • Name: {model['name']}")
                print()
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")

def list_openai_models(config):
    """List OpenAI-compatible models"""
    headers = {"Authorization": f"Bearer {config['api_key']}"}
    
    try:
        print(f"\nFetching available models from {config['base_url']}...")
        response = requests.get(f"{config['base_url']}/models", headers=headers)
        response.raise_for_status()
        models_data = response.json()
        
        print(f"\nAvailable models:")
        if 'data' in models_data:
            for model in models_data['data']:
                print(f"- {model['id']}")
        else:
            print("Unexpected response format from API")
    except Exception as e:
        print(f"Error fetching models: {e}")

def list_gemini_models(config):
    """List Gemini models"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=config['api_key'])
        
        print("\nFetching available Gemini models...")
        models = genai.list_models()
        
        print("\nAvailable Gemini models:")
        for model in models:
            if 'gemini' in model.name.lower():
                print(f"- {model.name}")
                if hasattr(model, 'display_name'):
                    print(f"  • Display Name: {model.display_name}")
                print()
    except Exception as e:
        print(f"Error fetching Gemini models: {e}")

def show_ai_status():
    """Show current AI configuration"""
    from config import AI_PROVIDER, get_ai_config
    config = get_ai_config()
    
    print(f"\n=== Current AI Configuration ===")
    print(f"Provider: {AI_PROVIDER}")
    print(f"Name: {config['name']}")
    print(f"Model: {config.get('model', 'N/A')}")
    if 'base_url' in config:
        print(f"Base URL: {config.get('base_url', 'N/A')}")
    print("================================")

def show_menu():
    while True:
        print("\n===== AI Cache Management Menu =====")
        print("1. Clear entire web cache")
        print("2. Show AI status")
        print("3. List available models for current provider")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            clean_web_folder()
        elif choice == '2':
            show_ai_status()
        elif choice == '3':
            list_available_models()
        elif choice == '4':
            print("Exiting script. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    if check_required_packages():
        show_menu()
    else:
        sys.exit(1)