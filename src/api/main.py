from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import uuid
from src.models.schemas import UserQuery, ChatbotResponse
from src.core.rag_pipeline import RAGPipeline, LLMProvider
from src.data.ingestion import VectorDBClient
from src.core.database import Database
from src.api.translate import router as translate_router
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
app.include_router(translate_router)

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
