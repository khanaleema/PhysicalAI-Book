from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field
import os
import uuid
import time
import asyncio
import json
from src.models.schemas import UserQuery, ChatbotResponse
from src.core.rag_pipeline import RAGPipeline, LLMProvider
from src.data.ingestion import VectorDBClient
from src.core.database import Database
# Always use database-based authentication
from src.api.auth import router as auth_router
print("✅ Using database-based authentication")
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
        # Validate input - reduce minimum length for testing
        if not request.content or len(request.content.strip()) < 5:
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
        
        # Try multiple model names in order of preference
        # gemini-2.5-flash is the primary model
        model_names = ["gemini-2.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash"]
        model = None
        model_name_used = None
        
        for model_name in model_names:
            try:
                test_model = genai.GenerativeModel(model_name)
                # Quick test to verify model works (skip if quota exceeded)
                try:
                    test_model.generate_content("test", generation_config={"max_output_tokens": 1})
                except Exception as test_error:
                    error_str = str(test_error).lower()
                    if "429" in error_str or "quota" in error_str:
                        # Quota issue, but model name is valid - use it anyway
                        model = test_model
                        model_name_used = model_name
                        break
                    else:
                        # Other error, try next model
                        continue
                
                # If we get here, model works!
                model = test_model
                model_name_used = model_name
                break
            except Exception as e:
                error_str = str(e).lower()
                if "404" in error_str or "not found" in error_str:
                    # Model doesn't exist, try next
                    continue
                else:
                    # Other error, try next model
                    continue
        
        if model is None:
            # Fallback to gemini-2.5-flash if all else fails
            model = genai.GenerativeModel("gemini-2.5-flash")
            model_name_used = "gemini-2.5-flash"
        
        # Simplified, shorter prompt to reduce processing time
        prompt = f"""Personalize this content for {level_info['name']} level learners.

Guidelines:
{level_info['guidance']}

Rules:
- Keep ALL markdown formatting (# * ` [] etc.)
- Keep code blocks unchanged
- Keep URLs unchanged
- Adjust explanations for {level_info['name']} level
- Maintain structure and accuracy

Content:
{request.content}

Return personalized content with formatting preserved."""

        # Use generate_content with timeout handling and retry
        try:
            # Limit content length to avoid timeout (max 4000 chars for input)
            # This is more conservative to ensure it works within timeout limits
            content_to_personalize = request.content
            MAX_INPUT_LENGTH = 4000
            if len(content_to_personalize) > MAX_INPUT_LENGTH:
                # For very long content, take first part
                content_to_personalize = content_to_personalize[:MAX_INPUT_LENGTH]
            
            # Simplified, shorter prompt to reduce processing time
            prompt = f"""Personalize this content for {level_info['name']} level learners.

Guidelines:
{level_info['guidance']}

Rules:
- Keep ALL markdown formatting (# * ` [] etc.)
- Keep code blocks unchanged
- Keep URLs unchanged
- Adjust explanations for {level_info['name']} level
- Maintain structure and accuracy

Content:
{content_to_personalize}

Return personalized content with formatting preserved."""
            
            # Retry logic for rate limiting
            max_retries = 3
            retry_delay = 2  # Start with 2 seconds
            last_error = None
            personalized_content = None
            
            for attempt in range(max_retries):
                try:
                    # Use faster generation config with reduced tokens
                    result = model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": 0.3,  # Lower temperature for faster, more consistent output
                            "max_output_tokens": 6000,  # Reduced to speed up generation
                            "top_p": 0.95,
                            "top_k": 40,
                        }
                    )
                    
                    if not result or not result.text:
                        raise HTTPException(status_code=500, detail="Empty response from AI model")
                    
                    personalized_content = result.text
                    
                    # Validate response
                    if not personalized_content or len(personalized_content.strip()) < 10:
                        raise HTTPException(status_code=500, detail="Generated content is too short or invalid")
                    
                    # Success, break out of retry loop
                    break
                    
                except Exception as gen_error:
                    error_msg = str(gen_error).lower()
                    last_error = gen_error
                    
                    # Check for quota/rate limit errors
                    if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg:
                        # Extract retry delay from error if available
                        if "retry in" in error_msg or "retry_delay" in error_msg:
                            # Try to extract seconds from error message
                            import re
                            delay_match = re.search(r'retry in ([\d.]+)s', error_msg, re.IGNORECASE)
                            if delay_match:
                                retry_delay = float(delay_match.group(1)) + 1  # Add 1 second buffer
                            else:
                                retry_delay = retry_delay * (2 ** attempt)  # Exponential backoff
                        
                        if attempt < max_retries - 1:
                            print(f"⚠️ Rate limit hit, retrying in {retry_delay:.1f} seconds (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            # Final attempt failed
                            raise HTTPException(
                                status_code=429,
                                detail="API quota exceeded. Free tier allows 20 requests per day per model. Please wait or upgrade your API plan. Retry after some time."
                            )
                    elif "timeout" in error_msg or "504" in error_msg or "timed out" in error_msg:
                        raise HTTPException(
                            status_code=504, 
                            detail="The request timed out. Please try again with shorter content or try again later."
                        )
                    elif "invalid" in error_msg or "empty" in error_msg:
                        raise HTTPException(
                            status_code=500, 
                            detail="Failed to generate personalized content. Please try again."
                        )
                    else:
                        # Other errors, don't retry
                        raise
            
            # Check if we got content
            if not personalized_content:
                if last_error:
                    raise last_error
                else:
                    raise HTTPException(status_code=500, detail="Failed to generate personalized content")
                
        except HTTPException:
            raise
        except Exception as gen_error:
            error_msg = str(gen_error).lower()
            if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg:
                raise HTTPException(
                    status_code=429,
                    detail="API quota exceeded. Free tier allows 20 requests per day per model. Please wait or upgrade your API plan."
                )
            elif "timeout" in error_msg or "504" in error_msg:
                raise HTTPException(
                    status_code=504, 
                    detail="The request timed out. Please try again with shorter content or try again later."
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Personalization failed: {str(gen_error)[:200]}"
                )
        
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
        
        # Try multiple model names in order of preference
        # gemini-2.5-flash is the primary model
        model_names = ["gemini-2.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash"]
        model = None
        model_name_used = None
        
        for model_name in model_names:
            try:
                test_model = genai.GenerativeModel(model_name)
                # Quick test to verify model works (skip if quota exceeded)
                try:
                    test_model.generate_content("test", generation_config={"max_output_tokens": 1})
                except Exception as test_error:
                    error_str = str(test_error).lower()
                    if "429" in error_str or "quota" in error_str:
                        # Quota issue, but model name is valid - use it anyway
                        model = test_model
                        model_name_used = model_name
                        break
                    else:
                        # Other error, try next model
                        continue
                
                # If we get here, model works!
                model = test_model
                model_name_used = model_name
                break
            except Exception as e:
                error_str = str(e).lower()
                if "404" in error_str or "not found" in error_str:
                    # Model doesn't exist, try next
                    continue
                else:
                    # Other error, try next model
                    continue
        
        if model is None:
            # Fallback to gemini-2.5-flash if all else fails
            model = genai.GenerativeModel("gemini-2.5-flash")
            model_name_used = "gemini-2.5-flash"
        
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

        # Retry logic for rate limiting
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds
        last_error = None
        
        for attempt in range(max_retries):
            try:
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
            except Exception as gen_error:
                error_str = str(gen_error).lower()
                last_error = gen_error
                
                # Check for quota/rate limit errors
                if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
                    # Extract retry delay from error if available
                    if "retry in" in error_str or "retry_delay" in error_str:
                        # Try to extract seconds from error message
                        import re
                        delay_match = re.search(r'retry in ([\d.]+)s', error_str, re.IGNORECASE)
                        if delay_match:
                            retry_delay = float(delay_match.group(1)) + 1  # Add 1 second buffer
                        else:
                            retry_delay = retry_delay * (2 ** attempt)  # Exponential backoff
                    
                    if attempt < max_retries - 1:
                        print(f"⚠️ Rate limit hit, retrying in {retry_delay:.1f} seconds (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        # Final attempt failed
                        raise HTTPException(
                            status_code=429,
                            detail="API quota exceeded. Free tier allows 20 requests per day per model. Please wait or upgrade your API plan. Retry after some time."
                        )
                else:
                    # Other errors, don't retry
                    raise
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
            
    except HTTPException:
        raise
    except Exception as e:
        error_detail = str(e)
        error_lower = error_detail.lower()
        
        # Handle specific error types
        if '429' in error_lower or 'quota' in error_lower or 'rate limit' in error_lower:
            raise HTTPException(
                status_code=429,
                detail="API quota exceeded. Free tier allows 20 requests per day per model. Please wait or upgrade your API plan."
            )
        elif 'GEMINI_API_KEY' in error_detail:
            error_detail = "GEMINI_API_KEY not configured. Please set it in environment variables."
        elif 'timeout' in error_lower or '504' in error_lower:
            raise HTTPException(
                status_code=504,
                detail="Translation request timed out. Please try again with shorter content."
            )
        
        raise HTTPException(status_code=500, detail=f"Translation failed: {error_detail[:500]}")


# Quiz Generation endpoint - using quiz-generator skill
class GenerateQuizRequest(BaseModel):
    chapterContent: str = Field(..., description="Chapter content to generate quiz from")
    chapterNumber: int = Field(..., description="Chapter number")
    lessonCount: int = Field(default=4, description="Number of lessons in chapter")
    difficulty: str = Field(default="intermediate", description="Difficulty level: beginner, intermediate, advanced")
    
@app.post("/generate-quiz", summary="Generate 50-question quiz using quiz-generator skill.")
async def generate_quiz(request: GenerateQuizRequest):
    """
    Generate a comprehensive 50-question quiz from chapter content.
    Based on .gemini/skills/quiz-generator skill patterns.
    Returns quiz in Quiz component format with immediate feedback.
    """
    try:
        if not request.chapterContent or len(request.chapterContent.strip()) < 100:
            raise HTTPException(status_code=400, detail="Chapter content is too short (minimum 100 characters)")
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Remove proxy env vars before importing Gemini
        for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
            os.environ.pop(key, None)
        
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        
        # Use gemini-2.5-flash for quiz generation
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Truncate content if too long (keep first 8000 chars to avoid timeouts)
        content_preview = request.chapterContent[:8000]
        if len(request.chapterContent) > 8000:
            content_preview += "\n\n[Content truncated for processing...]"
        
        quiz_prompt = f"""You are an expert educational content creator. Generate a comprehensive 50-question quiz based on the following chapter content.

CRITICAL REQUIREMENTS (from quiz-generator skill):
1. Generate exactly 50 conceptual questions (not recall/memorization)
2. Each question must have exactly 4 options
3. Use correctOption indices 0-3 (not 1-4)
4. Distribute correct answers evenly: ~12-13 per index (0, 1, 2, 3)
5. All options must be within ±3 words of each other in length
6. Each explanation must be 100-150 words addressing:
   - Why the correct answer is right (2-3 sentences)
   - Why EACH distractor is wrong (1-2 sentences each)
   - Real-world connection or misconception clarification
7. Questions should test understanding/application, not memorization
8. Use "source" field: "Lesson N: [Lesson Title]" format

Chapter Number: {request.chapterNumber}
Number of Lessons: {request.lessonCount}
Difficulty: {request.difficulty}

Chapter Content:
{content_preview}

Generate the quiz as a JSON array of questions. Each question must have:
- question: string
- options: array of 4 strings (all within ±3 words length)
- correctOption: integer (0-3)
- explanation: string (100-150 words addressing all 4 options)
- source: string ("Lesson N: [Title]")

Return ONLY the JSON array, no markdown formatting.
"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(
                    quiz_prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 16000,  # Large output for 50 questions
                        "top_p": 0.95,
                    }
                )
                
                quiz_text = response.text.strip()
                
                # Extract JSON from response (might be wrapped in markdown)
                if "```json" in quiz_text:
                    quiz_text = quiz_text.split("```json")[1].split("```")[0].strip()
                elif "```" in quiz_text:
                    quiz_text = quiz_text.split("```")[1].split("```")[0].strip()
                
                import json
                quiz_data = json.loads(quiz_text)
                
                # Validate structure
                if not isinstance(quiz_data, list):
                    raise ValueError("Quiz data must be an array")
                
                if len(quiz_data) != 50:
                    raise ValueError(f"Expected 50 questions, got {len(quiz_data)}")
                
                # Validate each question
                for i, q in enumerate(quiz_data):
                    if "question" not in q or "options" not in q or "correctOption" not in q or "explanation" not in q:
                        raise ValueError(f"Question {i+1} missing required fields")
                    if len(q["options"]) != 4:
                        raise ValueError(f"Question {i+1} must have exactly 4 options")
                    if q["correctOption"] not in [0, 1, 2, 3]:
                        raise ValueError(f"Question {i+1} correctOption must be 0-3")
                
                # Count distribution of correctOption
                distribution = {0: 0, 1: 0, 2: 0, 3: 0}
                for q in quiz_data:
                    distribution[q["correctOption"]] += 1
                
                return {
                    "success": True,
                    "quiz": quiz_data,
                    "metadata": {
                        "questionCount": len(quiz_data),
                        "chapterNumber": request.chapterNumber,
                        "distribution": distribution,
                        "format": "Quiz component (JSON array)"
                    }
                }
                
            except Exception as e:
                error_detail = str(e)
                error_lower = error_detail.lower()
                
                # Handle quota errors with retry
                if '429' in error_lower or 'quota' in error_lower or 'rate limit' in error_lower:
                    if attempt < max_retries - 1:
                        # Extract retry delay if provided
                        retry_delay = 30  # Default 30 seconds
                        if 'retry in' in error_detail.lower():
                            try:
                                import re
                                delay_match = re.search(r'retry in ([\d.]+)s?', error_detail.lower())
                                if delay_match:
                                    retry_delay = int(float(delay_match.group(1))) + 5
                            except:
                                pass
                        
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        raise HTTPException(
                            status_code=429,
                            detail="API quota exceeded. Please wait before retrying."
                        )
                
                # Handle timeout
                if 'timeout' in error_lower or '504' in error_lower:
                    raise HTTPException(
                        status_code=504,
                        detail="Quiz generation timed out. Content might be too long."
                    )
                
                # Re-raise on last attempt
                if attempt == max_retries - 1:
                    raise
                
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse quiz JSON: {str(e)}")
    except Exception as e:
        error_detail = str(e)
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {error_detail[:500]}")


# Content Evaluation endpoint - using content-evaluation-framework skill
class EvaluateContentRequest(BaseModel):
    content: str = Field(..., description="Content to evaluate")
    contentType: str = Field(default="lesson", description="Type: lesson, chapter, section")
    targetAudience: str = Field(default="intermediate", description="Target audience level")
    
@app.post("/evaluate-content", summary="Evaluate content quality using content-evaluation-framework skill.")
async def evaluate_content(request: EvaluateContentRequest):
    """
    Evaluate educational content quality across 6 weighted categories.
    Based on .gemini/skills/content-evaluation-framework skill.
    Returns comprehensive evaluation report with scores and recommendations.
    """
    try:
        if not request.content or len(request.content.strip()) < 50:
            raise HTTPException(status_code=400, detail="Content is too short (minimum 50 characters)")
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Remove proxy env vars before importing Gemini
        for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
            os.environ.pop(key, None)
        
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        
        # Use gemini-2.5-flash for evaluation
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Truncate content if too long (keep first 6000 chars)
        content_preview = request.content[:6000]
        if len(request.content) > 6000:
            content_preview += "\n\n[Content truncated for evaluation...]"
        
        evaluation_prompt = f"""You are an expert educational content evaluator. Evaluate the following content using the content-evaluation-framework rubric.

EVALUATION CRITERIA (6 weighted categories):

1. Technical Accuracy (30% weight):
   - Code correctness, type hints, explanations accuracy
   - Examples work as stated
   - Technical concepts explained correctly

2. Pedagogical Effectiveness (25% weight):
   - Show-then-explain pattern followed
   - Progressive complexity maintained
   - Quality exercises and learning activities
   - Concept scaffolding appropriate

3. Writing Quality (20% weight):
   - Readability (target: Flesch-Kincaid 8-10)
   - Clear, accessible language
   - Grade-level appropriateness
   - Voice and tone consistent

4. Structure & Organization (15% weight):
   - Learning objectives met
   - Logical flow and progression
   - Appropriate length
   - Smooth transitions

5. AI-First Teaching (10% weight):
   - Co-learning partnership demonstrated
   - Three Roles Framework shown (AI as Teacher/Student/Co-Worker)
   - Appropriate AI integration

6. Constitution Compliance (Pass/Fail gate):
   - Non-negotiable principles followed
   - Must pass to proceed

SCORING TIERS:
- Excellent: 90-100%
- Good: 75-89%
- Needs Work: 50-74%
- Insufficient: <50%

Content Type: {request.contentType}
Target Audience: {request.targetAudience}

Content to Evaluate:
{content_preview}

Provide evaluation as JSON with this structure:
{{
  "constitutionCompliance": "Pass" or "Fail" (with reason),
  "categories": {{
    "technicalAccuracy": {{"score": 0-100, "tier": "Excellent|Good|Needs Work|Insufficient", "evidence": "specific examples", "recommendations": "actionable feedback"}},
    "pedagogicalEffectiveness": {{"score": 0-100, "tier": "...", "evidence": "...", "recommendations": "..."}},
    "writingQuality": {{"score": 0-100, "tier": "...", "evidence": "...", "recommendations": "..."}},
    "structureOrganization": {{"score": 0-100, "tier": "...", "evidence": "...", "recommendations": "..."}},
    "aiFirstTeaching": {{"score": 0-100, "tier": "...", "evidence": "...", "recommendations": "..."}}
  }},
  "overallScore": 0-100,
  "overallTier": "Excellent|Good|Needs Work|Insufficient",
  "strengths": ["list of strengths"],
  "priorityImprovements": ["top 3-5 improvements needed"],
  "recommendation": "Ready for publication|Needs revision|Requires major rework"
}}

Return ONLY valid JSON, no markdown formatting.
"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(
                    evaluation_prompt,
                    generation_config={
                        "temperature": 0.3,  # Lower temp for more consistent evaluation
                        "max_output_tokens": 4000,
                        "top_p": 0.95,
                    }
                )
                
                eval_text = response.text.strip()
                
                # Extract JSON from response
                if "```json" in eval_text:
                    eval_text = eval_text.split("```json")[1].split("```")[0].strip()
                elif "```" in eval_text:
                    eval_text = eval_text.split("```")[1].split("```")[0].strip()
                
                import json
                evaluation_data = json.loads(eval_text)
                
                # Calculate weighted score
                weights = {
                    "technicalAccuracy": 0.30,
                    "pedagogicalEffectiveness": 0.25,
                    "writingQuality": 0.20,
                    "structureOrganization": 0.15,
                    "aiFirstTeaching": 0.10
                }
                
                weighted_score = sum(
                    evaluation_data["categories"][cat]["score"] * weights[cat]
                    for cat in weights.keys()
                )
                
                evaluation_data["calculatedWeightedScore"] = round(weighted_score, 2)
                
                return {
                    "success": True,
                    "evaluation": evaluation_data,
                    "metadata": {
                        "contentType": request.contentType,
                        "targetAudience": request.targetAudience,
                        "evaluationFramework": "content-evaluation-framework v2.1.0"
                    }
                }
                
            except Exception as e:
                error_detail = str(e)
                error_lower = error_detail.lower()
                
                # Handle quota errors with retry
                if '429' in error_lower or 'quota' in error_lower or 'rate limit' in error_lower:
                    if attempt < max_retries - 1:
                        retry_delay = 30
                        if 'retry in' in error_detail.lower():
                            try:
                                import re
                                delay_match = re.search(r'retry in ([\d.]+)s?', error_detail.lower())
                                if delay_match:
                                    retry_delay = int(float(delay_match.group(1))) + 5
                            except:
                                pass
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        raise HTTPException(
                            status_code=429,
                            detail="API quota exceeded. Please wait before retrying."
                        )
                
                if 'timeout' in error_lower or '504' in error_lower:
                    raise HTTPException(
                        status_code=504,
                        detail="Content evaluation timed out."
                    )
                
                if attempt == max_retries - 1:
                    raise
                
                await asyncio.sleep(2 ** attempt)
        
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse evaluation JSON: {str(e)}")
    except Exception as e:
        error_detail = str(e)
        raise HTTPException(status_code=500, detail=f"Content evaluation failed: {error_detail[:500]}")
