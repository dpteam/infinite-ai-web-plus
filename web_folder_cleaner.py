import os
import shutil
from pathlib import Path
import sys

# Check for required packages
def check_required_packages():
    missing_packages = []
    
    # Check for python-dotenv
    try:
        import dotenv
    except ImportError:
        missing_packages.append("python-dotenv")
    
    # Check for google-generativeai
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
    # Path to web folder
    web_folder = Path(__file__).parent / 'web'
    
    if not web_folder.exists():
        print(f"Web folder not found at {web_folder}")
        return
    
    print(f"Cleaning contents of {web_folder}")
    
    # List all items in the web folder
    for item in web_folder.iterdir():
        try:
            if item.is_file():
                # Remove file
                os.remove(item)
                print(f"Removed file: {item.name}")
            elif item.is_dir():
                # Remove directory and all its contents
                shutil.rmtree(item)
                print(f"Removed directory: {item.name}")
        except Exception as e:
            print(f"Error removing {item.name}: {e}")
    
    print(f"Finished cleaning {web_folder}")

def list_gemini_models():
    # Import required packages here, after they've been verified
    import dotenv
    import google.generativeai as genai
    
    # Load environment variables
    dotenv.load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        return
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # List available models
        print("\nFetching available Gemini models...")
        models = genai.list_models()
        
        print("\nAvailable Gemini models:")
        gemini_models_found = False
        
        for model in models:
            if 'gemini' in model.name.lower():
                gemini_models_found = True
                print(f"- {model.name}")
                if hasattr(model, 'display_name'):
                    print(f"  • Display Name: {model.display_name}")
                print(f"  • Supported Generation Methods: {', '.join(model.supported_generation_methods)}")
                print()
        
        if not gemini_models_found:
            print("No Gemini models found.")
                
    except Exception as e:
        print(f"Error fetching Gemini models: {e}")

def show_menu():
    while True:
        print("\n===== Developer Script Menu =====")
        print("1. Clear web folder")
        print("2. List all available Gemini models")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            clean_web_folder()
        elif choice == '2':
            list_gemini_models()
        elif choice == '3':
            print("Exiting script. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Check for required packages before proceeding
    if check_required_packages():
        show_menu()
    else:
        sys.exit(1)