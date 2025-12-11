"""
Hugging Face Spaces entry point for FastAPI backend.
This file is used by Hugging Face Spaces to run the FastAPI application.
"""
import os
import sys

# CRITICAL: Remove env vars BEFORE any other imports
for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
    os.environ.pop(key, None)

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Verify model loading before starting app
print("=" * 50)
print("Checking embedding model configuration...")
print("=" * 50)

# Import ingestion module normally - let Python handle it
try:
    from src.data import ingestion
    
    EMBEDDING_PROVIDER = getattr(ingestion, 'EMBEDDING_PROVIDER', 'huggingface')
    EMBEDDING_MODEL = getattr(ingestion, 'EMBEDDING_MODEL', 'BAAI/bge-small-en-v1.5')
    hf_model = getattr(ingestion, 'hf_model', None)
    
    print(f"✅ Embedding provider: {EMBEDDING_PROVIDER}")
    print(f"✅ Embedding model: {EMBEDDING_MODEL}")
    
    if EMBEDDING_PROVIDER == "huggingface":
        if hf_model is None:
            print("⚠️ WARNING: FastEmbedding model is None!")
            print("Attempting to load FastEmbedding model...")
            try:
                from fastembed import TextEmbedding
                ingestion.hf_model = TextEmbedding(model_name=EMBEDDING_MODEL)
                print("✅ FastEmbedding model loaded successfully in app.py!")
            except Exception as e:
                print(f"❌ CRITICAL: Failed to load FastEmbedding model: {e}")
                print("Install with: pip install fastembed")
                import traceback
                traceback.print_exc()
        else:
            print("✅ FastEmbedding model is loaded!")
    else:
        print(f"✅ Using {EMBEDDING_PROVIDER} embedding provider")
except Exception as e:
    print(f"⚠️ WARNING: Could not check embedding configuration: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)

# Import the FastAPI app from the main module
from src.api.main import app

# Hugging Face Spaces will automatically detect and run this app
# The app is configured to run on port 7860 (Hugging Face default)
# or the port specified by the PORT environment variable
