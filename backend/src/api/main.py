import os
# CRITICAL: Remove env vars BEFORE any other imports
for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
    os.environ.pop(key, None)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from src.models.schemas import UserQuery, ChatbotResponse
from src.core.rag_pipeline import RAGPipeline, LLMProvider
from src.data.ingestion import VectorDBClient
from src.core.database import Database
from src.api.auth import router as auth_router
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

# Include routers - Database-based auth (requires DATABASE_URL)
app.include_router(auth_router)
print(f"✅ Auth router included")

# Initialize RAG components with retry logic and lazy initialization
import time
from threading import Lock

# Global variables for lazy initialization
_vector_db_client = None
_llm_provider = None
_rag_pipeline = None
_init_lock = Lock()
_initialization_attempted = False

def print_env_status():
    """Print environment variable status (without values for security)"""
    print("=" * 60)
    print("Environment Variables Status:")
    print("=" * 60)
    env_vars = {
        "QDRANT_URL": os.getenv("QDRANT_URL"),
        "QDRANT_API_KEY": "SET" if os.getenv("QDRANT_API_KEY") else "NOT SET",
        "GEMINI_API_KEY": "SET" if os.getenv("GEMINI_API_KEY") else "NOT SET",
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "gemini"),
        "EMBEDDING_PROVIDER": os.getenv("EMBEDDING_PROVIDER", "NOT SET"),
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "NOT SET"),
    }
    for key, value in env_vars.items():
        if "KEY" in key or "URL" in key:
            print(f"  {key}: {value[:50] + '...' if value and len(str(value)) > 50 else value}")
        else:
            print(f"  {key}: {value}")
    print("=" * 60)

def init_vector_db(max_retries=3, delay=2):
    """Initialize Vector DB with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempting to initialize Vector DB (attempt {attempt + 1}/{max_retries})...")
            print(f"   QDRANT_URL: {os.getenv('QDRANT_URL', 'NOT SET')}")
            print(f"   QDRANT_API_KEY: {'SET' if os.getenv('QDRANT_API_KEY') else 'NOT SET'}")
            client = VectorDBClient()
            print("✅ Vector DB initialized successfully")
            return client
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"❌ Failed to initialize Vector DB after {max_retries} attempts")
                return None

def init_llm_provider():
    """Initialize LLM Provider"""
    try:
        provider = LLMProvider()
        print("✅ LLM Provider initialized")
        return provider
    except Exception as e:
        print(f"⚠️ LLM Provider failed (backend will use fallback): {e}")
        import traceback
        traceback.print_exc()
        return None

def initialize_rag_components():
    """Lazy initialization of RAG components"""
    global _vector_db_client, _llm_provider, _rag_pipeline, _initialization_attempted
    
    with _init_lock:
        if _initialization_attempted:
            return _rag_pipeline
        
        _initialization_attempted = True
        print("=" * 60)
        print("Initializing RAG Components...")
        print("=" * 60)
        
        # Print environment status
        print_env_status()
        
        # Initialize components
        _vector_db_client = init_vector_db()
        _llm_provider = init_llm_provider()
        
        # Create RAG Pipeline
        try:
            if _vector_db_client and _llm_provider:
                _rag_pipeline = RAGPipeline(_vector_db_client, _llm_provider)
                print("✅ RAG Pipeline initialized with full features")
            elif _vector_db_client:
                # Create RAG pipeline even without LLM (will use fallback)
                _rag_pipeline = RAGPipeline(_vector_db_client, _llm_provider)
                print("⚠️ RAG Pipeline initialized with fallback mode (no LLM)")
            else:
                _rag_pipeline = None
                print("❌ Cannot initialize RAG Pipeline: Vector DB not available")
                print("💡 Check your QDRANT_URL and QDRANT_API_KEY environment variables")
        except Exception as e:
            print(f"❌ Failed to initialize RAG Pipeline: {e}")
            import traceback
            traceback.print_exc()
            _rag_pipeline = None
        
        print("=" * 60)
        return _rag_pipeline

# Initialize on startup (but with better error handling)
try:
    initialize_rag_components()
except Exception as e:
    print(f"❌ Startup initialization failed: {e}")
    import traceback
    traceback.print_exc()

# Export functions for use in endpoints
def get_vector_db_client():
    initialize_rag_components()
    return _vector_db_client

def get_llm_provider():
    initialize_rag_components()
    return _llm_provider

def get_rag_pipeline():
    return initialize_rag_components()

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
    # Try to initialize if not already done
    current_pipeline = initialize_rag_components()
    
    if not current_pipeline:
        error_detail = "RAG pipeline not initialized. "
        if not _vector_db_client:
            error_detail += "Vector DB connection failed. Check QDRANT_URL and QDRANT_API_KEY environment variables."
        elif not _llm_provider:
            error_detail += "LLM Provider failed. Check your GEMINI_API_KEY."
        else:
            error_detail += "Unknown initialization error. Check backend logs."
        raise HTTPException(status_code=503, detail=error_detail)
    
    try:
        # Validate query text
        if not user_query.text or not user_query.text.strip():
            raise HTTPException(status_code=400, detail="Query text cannot be empty")
        
        # Process the query
        response = current_pipeline.process_user_query(user_query, selected_text=user_query.selected_text)
        
        # Save to database if available
        if database:
            try:
                conversation_id = user_query.session_id or "default-session"
                database.save_conversation(conversation_id)
                database.save_message(
                    message_id=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                    query_id=user_query.id or str(uuid.uuid4()),
                    query_text=user_query.text,
                    response_text=response.text,
                    selected_text=user_query.selected_text
                )
            except Exception as db_error:
                # Don't fail the request if database save fails
                print(f"⚠️ Database save failed: {db_error}")
        
        return response
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
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
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error in query endpoint: {error_details}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/", summary="Root endpoint.")
def root():
    """Root endpoint."""
    return {
        "message": "Physical AI Book RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "translate": "/translate",
            "auth": "/auth"
        }
    }

# Translate endpoint - added directly to main.py for reliability
class TranslateRequest(BaseModel):
    content: str
    targetLanguage: str = Field(default="ur", alias="target_language")
    preserveFormatting: bool = Field(default=True, alias="preserve_formatting")
    
    class Config:
        populate_by_name = True

@app.post("/translate", summary="Translate content to target language.")
async def translate_content(request: TranslateRequest):
    """Translate content to target language while preserving markdown formatting."""
    try:
        # Validate input
        if not request.content or len(request.content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Content is too short or empty")
        
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

@app.get("/health", summary="Health check endpoint.")
async def health_check():
    """
    Checks the health of the API and RAG components.
    """
    # Check environment variables
    env_status = {
        "QDRANT_URL": bool(os.getenv("QDRANT_URL")),
        "QDRANT_API_KEY": bool(os.getenv("QDRANT_API_KEY")),
        "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY")),
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "not_set"),
        "EMBEDDING_PROVIDER": os.getenv("EMBEDDING_PROVIDER", "not_set"),
    }
    
    # Try to initialize if not done
    current_pipeline = initialize_rag_components()
    
    status = {
        "status": "healthy" if current_pipeline else "degraded",
        "rag_initialized": current_pipeline is not None,
        "vector_db_initialized": _vector_db_client is not None,
        "llm_initialized": _llm_provider is not None,
        "environment_variables": env_status,
        "issues": []
    }
    
    # Add specific issues
    if not _vector_db_client:
        status["issues"].append("Vector DB not initialized - check QDRANT_URL and QDRANT_API_KEY")
    if not _llm_provider:
        status["issues"].append("LLM Provider not initialized - check API keys")
    if not current_pipeline:
        status["issues"].append("RAG Pipeline not initialized")
    
    return status
