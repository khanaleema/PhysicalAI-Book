#!/usr/bin/env python3
"""Test script to check if OpenAI embeddings are working."""
import os
from dotenv import load_dotenv

load_dotenv()

# Test OpenAI embedding
api_key = os.getenv("OPENAI_API_KEY")
embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai")
embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

print(f"Embedding Provider: {embedding_provider}")
print(f"Embedding Model: {embedding_model}")
print(f"API Key present: {bool(api_key)}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")

if embedding_provider == "openai":
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        print("\nTesting OpenAI embedding...")
        response = client.embeddings.create(
            model=embedding_model,
            input="This is a test"
        )
        
        embedding = response.data[0].embedding
        print(f"✅ Success! Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")

