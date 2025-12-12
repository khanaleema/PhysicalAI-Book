from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field
import os
import uuid
from src.models.schemas import UserQuery, ChatbotResponse
from src.core.rag_pipeline import RAGPipeline, LLMProvider
from src.data.ingestion import VectorDBClient
from src.core.database import Database
from src.api.simple_auth import router as auth_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Physical AI Book RAG API", version="1.0.0")

# CORS configuration (must be before routers)
# In production (Hugging Face Spaces), allow all origins
# In development, use specific origins from env
cors_origins_env = os.getenv("CORS_ORIGINS", "")
if cors_origins_env and cors_origins_env != "*":
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    # Allow all origins in production (Hugging Face Spaces)
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True if "*" not in cors_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - SIMPLE AUTH FIRST (no database dependency)
app.include_router(auth_router)

# Initialize RAG components
try:
    vector_db_client = VectorDBClient()
    print("✅ Vector DB initialized")
except Exception as e:
    print(f"❌ Failed to initialize Vector DB: {e}")
    vector_db_client = None

try:
    llm_provider = LLMProvider()
    print("✅ LLM Provider initialized")
except Exception as e:
    print(f"⚠️ LLM Provider failed (backend will use fallback): {e}")
    llm_provider = None

try:
    if vector_db_client and llm_provider:
        rag_pipeline = RAGPipeline(vector_db_client, llm_provider)
        print("✅ RAG Pipeline initialized")
    elif vector_db_client:
        # Create RAG pipeline even without LLM (will use fallback)
        rag_pipeline = RAGPipeline(vector_db_client, llm_provider)
        print("⚠️ RAG Pipeline initialized with fallback mode (no LLM)")
    else:
        rag_pipeline = None
        print("❌ Cannot initialize RAG Pipeline: Vector DB not available")
except Exception as e:
    print(f"❌ Failed to initialize RAG Pipeline: {e}")
    rag_pipeline = None

try:
    database = Database()
    print("✅ Database initialized")
except Exception as e:
    print(f"⚠️ Database initialization failed: {e}")
    database = None

@app.post("/query", response_model=ChatbotResponse, summary="Submit a user query to the chatbot.")
async def query_chatbot(user_query: UserQuery):
    """
    Submits a natural language query to the Physical AI & Humanoid Robotics Textbook QA Bot
    and retrieves a response based on the textbook content.
    
    If selected_text is provided, the bot will prioritize answering based on that selected text.
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized. Check your environment variables.")
    
    try:
        # Process the query
        response = rag_pipeline.process_user_query(user_query, selected_text=user_query.selected_text)
        
        # Save to database if available
        if database:
            conversation_id = user_query.session_id or "default-session"
            database.save_conversation(conversation_id)
            database.save_message(
                message_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                query_id=user_query.id,
                query_text=user_query.text,
                response_text=response.text,
                selected_text=user_query.selected_text
            )
        
        return response
    except ValueError as e:
        error_msg = str(e)
        # If it's an LLM initialization error, provide helpful guidance
        if "Gemini" in error_msg or "GEMINI_API_KEY" in error_msg:
            raise HTTPException(
                status_code=503, 
                detail=error_msg + " Please check backend logs for more details."
            )
        raise HTTPException(status_code=400, detail=f"Bad Request: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health", summary="Health check endpoint.")
async def health_check():
    """
    Checks the health of the API and RAG components.
    """
    status = {
        "status": "healthy",
        "rag_initialized": rag_pipeline is not None,
        "vector_db_initialized": vector_db_client is not None,
        "llm_initialized": llm_provider is not None
    }
    return status

# Translate endpoint - added directly to main.py for reliability
class TranslateRequest(BaseModel):
    content: str
    targetLanguage: str = Field(default="ur", alias="target_language")
    preserveFormatting: bool = Field(default=True, alias="preserve_formatting")
    
    class Config:
        populate_by_name = True  # Allow both field name and alias

@app.post("/translate", summary="Translate content to target language.")
async def translate_content(request: TranslateRequest):
    """Translate content to target language while preserving markdown formatting."""
    try:
        # Validate input
        if not request.content or len(request.content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Content is too short or empty")
        
        # Ensure targetLanguage has a default value
        target_lang = getattr(request, 'targetLanguage', None) or getattr(request, 'target_language', None) or "ur"
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Language code mapping
        lang_map = {
            'ur': 'Urdu (اردو)',
            'es': 'Spanish (Español)',
            'fr': 'French (Français)',
            'de': 'German (Deutsch)',
            'ar': 'Arabic (العربية)',
            'zh': 'Chinese (中文)',
            'ja': 'Japanese (日本語)',
            'hi': 'Hindi (हिन्दी)',
            'pt': 'Portuguese (Português)',
        }
        target_lang_name = lang_map.get(target_lang, target_lang)
        
        # Remove proxy env vars before importing Gemini
        # CRITICAL: Remove proxy env vars BEFORE importing google.generativeai
        for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
            os.environ.pop(key, None)
        
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""You are an expert translator specializing in translating technical and educational content from English to {target_lang_name}.

Translate the following content from English to {target_lang_name}. CRITICAL REQUIREMENTS:

1. Preserve ALL markdown formatting EXACTLY:
   - Headings: Keep # ## ### exactly as they are
   - Code blocks: Keep ```language``` format exactly, preserve code inside
   - Inline code: Keep `code` format exactly
   - Lists: Keep - * 1. 2. format exactly, maintain indentation
   - Links: Keep [text](url) format exactly
   - Bold: Keep **text** format exactly
   - Italic: Keep *text* format exactly
   - Blockquotes: Keep > format exactly
   - Tables: Keep | column | format exactly, preserve table structure
   - Horizontal rules: Keep --- exactly
   - Line breaks: Preserve ALL line breaks and paragraph spacing - DO NOT compress multiple lines into one

2. Translate ONLY the text content, NOT:
   - Markdown syntax symbols (# * - ` > | etc.)
   - Code in code blocks (keep code as-is)
   - URLs in links (keep URLs as-is)
   - Technical terms commonly used in English (API, JSON, HTTP, etc.)
   - Variable names, function names, class names in code
   - File paths, commands, or technical identifiers

3. CRITICAL: Preserve ALL line breaks and paragraph structure:
   - If there are multiple blank lines, keep them
   - If there are single line breaks, keep them
   - DO NOT merge paragraphs or compress content
   - Maintain the exact same line count and structure

4. Use proper script and maintain readability for {target_lang_name}.

5. Keep technical accuracy - translate concepts clearly.

6. IMPORTANT: The output should have the SAME number of lines as the input (or very close). Do not compress or summarize.

Original Content:
{request.content}

Return ONLY the translated content with all formatting and line breaks preserved exactly."""

        result = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 16000
            }
        )
        translated_content = result.text
        
        return {
            "translatedContent": translated_content,
            "targetLanguage": target_lang
        }
    except HTTPException:
        raise
    except Exception as e:
        error_detail = str(e)
        if 'GEMINI_API_KEY' in error_detail:
            error_detail = "GEMINI_API_KEY not configured. Please set it in environment variables."
        raise HTTPException(status_code=500, detail=f"Translation failed: {error_detail}")
