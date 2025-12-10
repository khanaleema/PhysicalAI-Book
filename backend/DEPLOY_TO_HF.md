# Deploy Backend to Hugging Face Space

## Quick Steps:

1. **Go to Hugging Face Space:**
   - https://huggingface.co/spaces/aleemakhan/physical-ai-backend

2. **Upload Updated Files:**
   - Click "Files and versions" tab
   - Upload these files:
     - `requirements.txt` (with torch and transformers)
     - `src/data/ingestion.py` (with better error handling)
     - `Dockerfile` (if changed)

3. **Or Use Git (if connected):**
   ```bash
   cd backend
   git remote add hf https://huggingface.co/spaces/aleemakhan/physical-ai-backend
   git push hf main
   ```

4. **Wait for Rebuild:**
   - Space will automatically rebuild
   - Check logs for any errors
   - Verify sentence-transformers installs correctly

## Key Changes:
- Added `torch>=2.0.0` and `transformers>=4.30.0` to requirements.txt
- Improved error handling in model loading
- Added lazy loading fallback

