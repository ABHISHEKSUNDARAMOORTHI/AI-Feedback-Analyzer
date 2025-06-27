import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("API Key not found!")
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    
    print("\n--- Listing Available Models ---")
    found_model = None
    try:
        for m in genai.list_models():
            # Filter models that support generateContent method
            if 'generateContent' in m.supported_generation_methods:
                print(f"  Found Model: {m.name}")
                # Prioritize a flash model or a pro model
                if "gemini-1.5-flash" in m.name.lower() and "latest" in m.name.lower():
                    found_model = m.name
                    print(f"  --> Using {found_model} for testing.")
                    break # Found the preferred model, no need to list more
                elif "gemini-pro" in m.name.lower() and not found_model: # Fallback if flash not found first
                    found_model = m.name # Keep looking for flash, but store pro as a backup
    except Exception as e:
        print(f"Error listing models: {e}")
        
    print("--- End Model List ---\n")

    if found_model:
        try:
            print(f"Attempting to generate content using: {found_model}")
            model = genai.GenerativeModel(found_model)
            response = model.generate_content("What is the capital of France?", safety_settings={'HARASSMENT': 'BLOCK_NONE'})
            print("\nAPI Test Successful! Response:")
            print(response.text)
        except Exception as e:
            print(f"\nAPI Test Failed with {found_model}: {e}")
    else:
        print("No suitable model found that supports 'generateContent'.")