# Backend Hugging Face Space Deployment Commands

## Option 1: Using Git with Token

**IMPORTANT:** Replace `YOUR_HF_TOKEN` with your actual Hugging Face token!

```powershell
cd C:\Users\user\Desktop\PhysicalAI-Book\backend

# Add Hugging Face remote (replace YOUR_HF_TOKEN with actual token)
git remote add hf https://YOUR_HF_TOKEN@huggingface.co/spaces/aleemakhan/physical-ai-backend

# Or update existing remote
git remote set-url hf https://YOUR_HF_TOKEN@huggingface.co/spaces/aleemakhan/physical-ai-backend

# Stage and commit changes
git add requirements.txt src/data/ingestion.py
git commit -m "Fix sentence-transformers dependencies"

# Push to Hugging Face
git push hf main
```

## Option 2: Manual Upload (Easier)

1. Go to: https://huggingface.co/spaces/aleemakhan/physical-ai-backend
2. Click "Files and versions" tab
3. Click "Upload file" button
4. Upload these files:
   - `requirements.txt` (from backend folder)
   - `src/data/ingestion.py` (from backend/src/data folder)
5. Space will auto-rebuild

## Files to Upload:
- `C:\Users\user\Desktop\PhysicalAI-Book\backend\requirements.txt`
- `C:\Users\user\Desktop\PhysicalAI-Book\backend\src\data\ingestion.py`
