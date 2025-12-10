"""
Hugging Face Spaces entry point for FastAPI backend.
This file is used by Hugging Face Spaces to run the FastAPI application.
"""
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Verify model loading before starting app
print("=" * 50)
print("Checking embedding model configuration...")
print("=" * 50)

# Import ingestion to trigger model loading
try:
    from src.data import ingestion
    print(f"Embedding provider: {ingestion.EMBEDDING_PROVIDER}")
    print(f"Embedding model: {ingestion.EMBEDDING_MODEL}")
    
    if ingestion.EMBEDDING_PROVIDER == "huggingface":
        if ingestion.hf_model is None:
            print("⚠️ WARNING: FastEmbedding model is None!")
            print("Attempting to load FastEmbedding model...")
            try:
                from fastembed import TextEmbedding
                ingestion.hf_model = TextEmbedding(model_name=ingestion.EMBEDDING_MODEL)
                print("✅ FastEmbedding model loaded successfully in app.py!")
            except Exception as e:
                print(f"❌ CRITICAL: Failed to load FastEmbedding model: {e}")
                print("Install with: pip install fastembed")
                import traceback
                traceback.print_exc()
        else:
            print("✅ FastEmbedding model is loaded!")
    else:
        print(f"✅ Using {ingestion.EMBEDDING_PROVIDER} embedding provider")
except Exception as e:
    print(f"❌ ERROR importing ingestion module: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)

# Import the FastAPI app from the main module
from src.api.main import app

# Hugging Face Spaces will automatically detect and run this app
# The app is configured to run on port 7860 (Hugging Face default)
# or the port specified by the PORT environment variable
