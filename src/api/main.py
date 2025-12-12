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
# Try to use database auth, fallback to simple_auth if database fails
try:
    from src.api.auth import router as auth_router
    print("✅ Using database-based authentication")
except Exception as e:
    print(f"⚠️ Database auth failed, using simple auth: {e}")
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

# Personalize endpoint - added directly to main.py
class PersonalizeRequest(BaseModel):
    content: str
    userLevel: str = Field(default="intermediate", alias="user_level")
    chapterPath: Optional[str] = Field(default=None, alias="chapter_path")
    
    class Config:
        populate_by_name = True

@app.post("/personalize", summary="Personalize content based on user level.")
async def personalize_content(request: PersonalizeRequest):
    """Personalize chapter content based on user experience level (beginner, intermediate, advanced)."""
    try:
        # Validate input
        if not request.content or len(request.content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Content is too short or empty")
        
        # Validate user level
        valid_levels = ["beginner", "intermediate", "advanced"]
        user_level = getattr(request, 'userLevel', None) or getattr(request, 'user_level', None) or "intermediate"
        if user_level not in valid_levels:
            raise HTTPException(status_code=400, detail=f"Invalid user level. Must be one of: {valid_levels}")
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Level-specific instructions
        level_instructions = {
            "beginner": {
                "name": "Beginner",
                "guidance": """
1. Simplify complex concepts - break down technical terms into everyday language
2. Add more context and background information
3. Use analogies and real-world examples
4. Avoid advanced mathematical formulations unless necessary
5. Explain acronyms and technical terms on first use
6. Add more step-by-step explanations
7. Include "Why this matters" sections
8. Use simpler vocabulary while maintaining accuracy
""",
            },
            "intermediate": {
                "name": "Intermediate",
                "guidance": """
1. Provide balanced explanations with both concepts and practical applications
2. Include code examples and technical details
3. Reference related concepts without over-explaining basics
4. Use standard technical terminology
5. Include practical examples and use cases
6. Balance theory with implementation
7. Add comparisons and trade-offs
""",
            },
            "advanced": {
                "name": "Advanced",
                "guidance": """
1. Include advanced technical details and mathematical formulations
2. Reference cutting-edge research and state-of-the-art methods
3. Discuss implementation nuances and edge cases
4. Include performance considerations and optimizations
5. Reference related advanced topics and research papers
6. Provide deeper insights into design decisions
7. Include advanced algorithms and data structures
8. Discuss scalability and production considerations
""",
            },
        }
        
        level_info = level_instructions.get(user_level, level_instructions["intermediate"])
        
        # Remove proxy env vars before importing Gemini
        for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
            os.environ.pop(key, None)
        
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""You are an expert educational content personalization system. Your task is to personalize technical content for a {level_info['name']} level learner.

USER LEVEL: {level_info['name']}

PERSONALIZATION GUIDELINES:
{level_info['guidance']}

CRITICAL REQUIREMENTS:

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
   - Line breaks: Preserve ALL line breaks and paragraph spacing

2. DO NOT change:
   - Markdown syntax symbols (# * - ` > | etc.)
   - Code in code blocks (keep code as-is)
   - URLs in links (keep URLs as-is)
   - Mathematical formulas and equations
   - Technical terms that are standard in the field

3. Personalize by:
   - Adjusting explanations to match the level
   - Adding or removing detail as appropriate
   - Modifying language complexity
   - Adding context or removing redundant explanations
   - Adjusting examples to match the level

4. Maintain the same structure and organization as the original.

5. Keep technical accuracy - only adjust presentation, not facts.

Original Content:
{request.content}

Return ONLY the personalized content with all formatting preserved exactly."""

        result = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 16000
            }
        )
        personalized_content = result.text
        
        return {
            "personalizedContent": personalized_content,
            "userLevel": user_level,
            "chapterPath": request.chapterPath
        }
    except HTTPException:
        raise
    except Exception as e:
        error_detail = str(e)
        if 'GEMINI_API_KEY' in error_detail:
            error_detail = "GEMINI_API_KEY not configured. Please set it in environment variables."
        raise HTTPException(status_code=500, detail=f"Personalization failed: {error_detail}")

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
