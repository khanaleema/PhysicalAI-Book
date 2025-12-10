# 🚀 Quick Deployment Guide - Railway (Easiest Option)

## Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub (easiest way)

## Step 2: Deploy Backend
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Select your repository: `khanaleema/PhysicalAI-Book`
4. Railway will auto-detect it's a Python project
5. Set **Root Directory** to: `backend`
6. Railway will automatically:
   - Detect `requirements.txt`
   - Install dependencies
   - Run the app

## Step 3: Add Environment Variables
In Railway dashboard, go to your service → **Variables** tab, add:

```
GROQ_API_KEY=your_groq_api_key_here
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_PROVIDER=groq
CORS_ORIGINS=*
```

## Step 4: Get Your Backend URL
1. Railway will give you a URL like: `https://your-app.up.railway.app`
2. Copy this URL

## Step 5: Update Frontend
1. Open `book/docusaurus.config.ts`
2. Update `apiUrl`:
```typescript
customFields: {
  apiUrl: 'https://your-app.up.railway.app', // Your Railway URL
},
```

## Step 6: Deploy Frontend
1. Push changes to GitHub
2. GitHub Actions will auto-deploy to GitHub Pages

## ✅ Done!
Your backend will be live on Railway (much more reliable than Hugging Face!)

---

# Alternative: Render.com (Also Free)

1. Go to https://render.com
2. Sign up with GitHub
3. Click **"New"** → **"Web Service"**
4. Connect your GitHub repo
5. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Add same environment variables as above
7. Click **"Create Web Service"**
8. Render will give you a URL like: `https://your-app.onrender.com`

