#!/usr/bin/env python3
"""Test Gemini API key directly."""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key from .env: {api_key[:10]}...{api_key[-4:] if api_key else 'NOT FOUND'}")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    print("OK: Gemini API configured")
    
    # Try common models directly
    test_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    for model_name in test_models:
        try:
            print(f"\nTesting model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello", generation_config={"max_output_tokens": 10})
            print(f"SUCCESS! Model {model_name} works!")
            print(f"   Response: {response.text}")
            break
        except Exception as e:
            error_msg = str(e)
            print(f"   Error for {model_name}: {error_msg}")
            continue
    else:
        print("\nERROR: All models failed!")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

