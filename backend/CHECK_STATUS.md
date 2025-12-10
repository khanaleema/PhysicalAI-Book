# Status Check Guide

## All Variables Are Set ✅

I can see all variables are set in Hugging Face Spaces. Now let's check why initialization is failing.

## Step 1: Check Detailed Health Status

Visit this URL to see detailed status:
```
https://aleemakhan-physical-ai-backend.hf.space/health
```

This will show:
- Which environment variables are detected
- Specific issues
- What's failing

## Step 2: Check Logs

1. Go to: https://huggingface.co/spaces/aleemakhan/physical-ai-backend
2. Click **Logs** tab
3. Look for these messages:
   - ✅ "Vector DB initialized successfully"
   - ✅ "LLM Provider initialized"
   - ✅ "RAG Pipeline initialized"
   - ❌ Any error messages

## Step 3: Verify Variable Values

Click "View" on each variable to verify:
- **QDRANT_URL**: Should be `https://5ac6479a-425f-4066-9031-d3415d506e94.eu-central-1-0.aws.cloud.qdrant.io:6333`
- **QDRANT_API_KEY**: Should match your key
- **GROQ_API_KEY**: Should match your key
- **LLM_PROVIDER**: Should be `groq`
- **EMBEDDING_PROVIDER**: Should be `huggingface`
- **EMBEDDING_MODEL**: Should be `BAAI/bge-small-en-v1.5`

## Step 4: Force Rebuild

If variables are correct but still not working:
1. Go to Settings
2. Scroll down to "Danger Zone"
3. Click "Rebuild Space"
4. Wait 5-10 minutes
5. Check health again

## Common Issues:

1. **QDRANT connection failing**: Check if URL has `:6333` port
2. **GROQ_API_KEY invalid**: Verify key is active
3. **Embedding model loading**: FastEmbedding might need time to download on first run

## Quick Test:

After rebuild, test with:
```bash
curl https://aleemakhan-physical-ai-backend.hf.space/health
```

Should return:
```json
{
  "status": "healthy",
  "rag_initialized": true,
  "vector_db_initialized": true,
  "llm_initialized": true
}
```

