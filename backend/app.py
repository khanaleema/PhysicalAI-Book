"""
Hugging Face Spaces entry point for FastAPI backend.
This file is used by Hugging Face Spaces to run the FastAPI application.
"""
import os
import sys
import importlib.util

# CRITICAL: Remove env vars BEFORE any other imports
for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
    os.environ.pop(key, None)

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# CRITICAL: Register ingestion module BEFORE any other imports try to use it
# This fixes the import error in rag_pipeline.py and other modules
import importlib.util
ingestion_path = os.path.join(backend_dir, 'src', 'data', 'ingestion.py')

if os.path.exists(ingestion_path):
    try:
        spec = importlib.util.spec_from_file_location("src.data.ingestion", ingestion_path)
        ingestion_module = importlib.util.module_from_spec(spec)
        # Register in sys.modules so other imports can find it
        sys.modules['src.data.ingestion'] = ingestion_module
        sys.modules['src.data'] = type(sys)('src.data')  # Create parent package
        sys.modules['src.data'].ingestion = ingestion_module  # Add ingestion to parent
        spec.loader.exec_module(ingestion_module)
        print("✅ Ingestion module registered successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not pre-register ingestion module: {e}")
else:
    print(f"⚠️ Warning: ingestion.py not found at {ingestion_path}")

# Verify model loading before starting app
print("=" * 50)
print("Checking embedding model configuration...")
print("=" * 50)

# Now use the pre-registered module directly (no import needed)
try:
    # Get the pre-registered module
    ingestion = sys.modules.get('src.data.ingestion')
    if not ingestion:
        # Try to import from src.data (should work after __init__.py loads it)
        try:
            from src.data import ingestion
        except ImportError:
            raise ImportError("Ingestion module not available - check __init__.py")
    
    EMBEDDING_PROVIDER = ingestion.EMBEDDING_PROVIDER
    EMBEDDING_MODEL = ingestion.EMBEDDING_MODEL
    hf_model = ingestion.hf_model
    
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
    print(f"❌ ERROR importing ingestion module: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)

# Import the FastAPI app from the main module
from src.api.main import app

# Hugging Face Spaces will automatically detect and run this app
# The app is configured to run on port 7860 (Hugging Face default)
# or the port specified by the PORT environment variable
