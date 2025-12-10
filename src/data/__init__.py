# Data package for ingestion and vector database
# CRITICAL: Load ingestion module and make it available
import os
import sys
import importlib.util

# Get absolute path to this file's directory
_current_dir = os.path.dirname(os.path.abspath(__file__))
_ingestion_file = os.path.join(_current_dir, 'ingestion.py')

# Verify file exists
if not os.path.exists(_ingestion_file):
    raise ImportError(f"CRITICAL: ingestion.py not found at {_ingestion_file}. Current dir: {_current_dir}")

# Load the module
try:
    _spec = importlib.util.spec_from_file_location("src.data.ingestion", _ingestion_file)
    if _spec is None or _spec.loader is None:
        raise ImportError(f"Could not create module spec for {_ingestion_file}")
    
    _ingestion_module = importlib.util.module_from_spec(_spec)
    # Register in sys.modules FIRST
    sys.modules['src.data.ingestion'] = _ingestion_module
    # Then execute
    _spec.loader.exec_module(_ingestion_module)
    
    # Make it available in this package's namespace
    ingestion = _ingestion_module
    
except Exception as e:
    import traceback
    _error = f"Failed to load ingestion.py: {e}\n{traceback.format_exc()}"
    print(f"❌ ERROR in __init__.py: {_error}")
    raise ImportError(_error)

# Verify it's set
if 'ingestion' not in locals() and 'ingestion' not in globals():
    raise ImportError("ingestion variable not set in __init__.py")

__all__ = ['ingestion']
