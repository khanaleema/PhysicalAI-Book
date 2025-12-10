# Hugging Face Spaces Deployment Guide

## Environment Variables to Set in Hugging Face Spaces

Go to your Space Settings → Variables and add these:

### Required Variables:

```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=physical_ai_book
DATABASE_URL=your_database_url_here
AUTH_SECRET_KEY=your_auth_secret_key_here
```

### Optional Configuration:

```
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
CORS_ORIGINS=*
PORT=7860
```

## Deployment Steps:

1. Push code to Hugging Face Space
2. Set all environment variables in Space Settings
3. Wait for rebuild (usually 5-10 minutes)
4. Check logs for any errors
5. Test the `/health` endpoint first

## Testing:

```bash
# Health check
curl https://aleemakhan-physical-ai-backend.hf.space/health

# Test query
curl -X POST https://aleemakhan-physical-ai-backend.hf.space/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What is physical AI?"}'
```

