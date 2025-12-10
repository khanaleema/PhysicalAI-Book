#!/usr/bin/env python3
"""Test OpenAI API key."""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key from .env: {api_key[:15]}...{api_key[-4:] if api_key and len(api_key) > 19 else 'NOT FOUND'}")

if not api_key:
    print("ERROR: OPENAI_API_KEY not found")
    exit(1)

try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    print("OK: OpenAI client created")
    
    # Test with a simple call
    print("\nTesting OpenAI API...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    print("SUCCESS! OpenAI API works!")
    print(f"   Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()


