# Hugging Face Space Update Instructions

## ⚠️ IMPORTANT: Backend files Hugging Face Space par manually update karni hain!

### Files to Upload:

1. **requirements.txt** - Updated with torch and transformers
   - Location: `C:\Users\user\Desktop\PhysicalAI-Book\backend\requirements.txt`
   - Contains: torch>=2.0.0, transformers>=4.30.0, sentence-transformers==2.2.2

2. **src/data/ingestion.py** - Better error handling
   - Location: `C:\Users\user\Desktop\PhysicalAI-Book\backend\src\data\ingestion.py`
   - Contains: Improved model loading with lazy loading fallback

### Steps:

1. Go to: https://huggingface.co/spaces/aleemakhan/physical-ai-backend
2. Click **"Files and versions"** tab
3. Click **"Upload file"** button
4. Upload these 2 files:
   - `requirements.txt` (replace existing)
   - `src/data/ingestion.py` (replace existing)
5. Space automatically rebuild hoga (2-3 minutes)
6. Check **"Logs"** tab to verify:
   - `torch` installs correctly
   - `transformers` installs correctly  
   - `sentence-transformers` installs correctly
   - Model loads successfully: "✅ Hugging Face model loaded successfully!"

### After Rebuild:

- Check if Space is "Running" (green dot)
- Test API: https://aleemakhan-physical-ai-backend.hf.space/docs
- Test query endpoint: POST to `/query`

### Current Status:

- ✅ Files updated in GitHub
- ⏳ Waiting for Hugging Face Space update
- ⏳ Space needs manual file upload

