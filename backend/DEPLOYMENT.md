# Backend Deployment Guide

## Option 1: Railway (Recommended - Easy & Free Tier Available)

1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python and install dependencies
5. Add environment variables:
   - `GROQ_API_KEY` - Your Groq API key
   - `EMBEDDING_PROVIDER` - Set to "huggingface" or "openai"
   - `EMBEDDING_MODEL` - Model name (e.g., "sentence-transformers/all-MiniLM-L6-v2")
   - `LLM_PROVIDER` - Set to "groq" (default)
   - `CORS_ORIGINS` - Set to "*" or your frontend URL
6. Railway will automatically deploy and give you a URL like: `https://your-app.railway.app`

## Option 2: Render (Free Tier Available)

1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Add environment variables (same as Railway)
6. Click "Create Web Service"
7. Render will give you a URL like: `https://your-app.onrender.com`

## Option 3: Fly.io (Free Tier Available)

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Initialize: `fly launch` (in backend directory)
4. Deploy: `fly deploy`
5. Set secrets: `fly secrets set GROQ_API_KEY=your_key`
6. Get URL: `fly info`

## Option 4: Hugging Face Spaces (Current - Has Issues)

If you want to continue with Hugging Face:
1. Push code to Hugging Face Space
2. Set environment variables in Space settings
3. Wait for rebuild

## Environment Variables Required

```bash
GROQ_API_KEY=your_groq_api_key_here
EMBEDDING_PROVIDER=huggingface  # or "openai"
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_PROVIDER=groq
CORS_ORIGINS=*
```

## Update Frontend API URL

After deployment, update `book/docusaurus.config.ts`:

```typescript
customFields: {
  apiUrl: 'https://your-new-backend-url.com',
},
```

Then rebuild and redeploy frontend.

