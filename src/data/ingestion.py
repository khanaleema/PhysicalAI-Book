import os
import sys
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Query, VectorInput
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.models.schemas import SourceDocument, TextChunk
from dotenv import load_dotenv
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import threading

load_dotenv()

# Determine embedding provider
def clean_env_var(value: str) -> str:
    """Clean environment variable - remove newlines and extra whitespace"""
    if not value:
        return ""
    return value.replace("\n", "").replace("\r", "").strip()

EMBEDDING_PROVIDER = clean_env_var(os.getenv("EMBEDDING_PROVIDER", "huggingface")).lower()  # "openai", "gemini", or "huggingface"
EMBEDDING_MODEL = clean_env_var(os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))  # FastEmbedding default (faster than sentence-transformers)

# Global variable for embedding model
hf_model = None
_model_lock = threading.Lock()  # Thread-safe model loading
_embedding_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="embedding")  # Non-blocking embeddings

# Initialize embedding clients based on provider
if EMBEDDING_PROVIDER == "openai":
    from openai import OpenAI
    openai_client = OpenAI(api_key=clean_env_var(os.getenv("OPENAI_API_KEY", "")))
    EMBEDDING_MODEL = clean_env_var(os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
elif EMBEDDING_PROVIDER == "gemini":
    try:
        import google.generativeai as genai
        genai.configure(api_key=clean_env_var(os.getenv("GEMINI_API_KEY", "")))
        EMBEDDING_MODEL = clean_env_var(os.getenv("EMBEDDING_MODEL", "models/embedding-001"))
    except ImportError:
        print("Warning: google-generativeai not installed. Install with: pip install google-generativeai")
elif EMBEDDING_PROVIDER == "huggingface":
    try:
        from fastembed import TextEmbedding
        model_name = clean_env_var(os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))
        EMBEDDING_MODEL = model_name
        print(f"Loading FastEmbedding model: {EMBEDDING_MODEL}")
        print("FastEmbedding is faster and lighter than sentence-transformers!")
        # FastEmbedding handles caching automatically
        # Don't load model at import time - load lazily
        hf_model = None
        print(f"✅ FastEmbedding will be loaded on first use")
    except ImportError as e:
        print(f"❌ ERROR: fastembed not installed!")
        print(f"Install with: pip install fastembed")
        print(f"Import error details: {e}")
        print(f"Python path: {sys.path}")
        hf_model = None
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize FastEmbedding: {e}")
        import traceback
        traceback.print_exc()
        hf_model = None

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

def load_document(file_path: str, doc_type: str) -> SourceDocument:
    """Loads a document from a given file path."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    file_name = os.path.basename(file_path)
    return SourceDocument(name=file_name, type=doc_type, content_raw=content)

def load_markdown_documents(docs_dir: str) -> List[SourceDocument]:
    """Loads all markdown documents from the docs directory."""
    documents = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                # Extract part/chapter info from path
                rel_path = os.path.relpath(file_path, docs_dir)
                doc_type = f"TEXTBOOK_{rel_path.replace(os.sep, '_')}"
                documents.append(load_document(file_path, doc_type))
    return documents

def chunk_document(document: SourceDocument, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[TextChunk]:
    """Splits a source document into smaller text chunks using LangChain."""
    chunks = []
    text_chunks = text_splitter.split_text(document.content_raw)
    
    for order, text in enumerate(text_chunks):
        # Extract metadata from document name/path
        source_metadata = f"{document.name} | Chunk {order + 1}"
        chunks.append(TextChunk(
            document_id=document.id,
            text=text,
            source_metadata=source_metadata,
            order_in_document=order
        ))
    return chunks

def _load_fastembed_model():
    """Load FastEmbedding model in a thread-safe way."""
    global hf_model
    with _model_lock:
        if hf_model is None:
            from fastembed import TextEmbedding
            model_name = clean_env_var(os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))
            print(f"Loading FastEmbedding model on-demand: {model_name}")
            try:
                hf_model = TextEmbedding(model_name=model_name)
                print(f"✅ FastEmbedding model loaded on-demand!")
            except Exception as e:
                print(f"❌ Failed to load FastEmbedding model: {e}")
                import traceback
                traceback.print_exc()
                raise
    return hf_model

def _embed_text_fastembed(text: str):
    """Generate embedding using FastEmbedding (non-blocking)."""
    global hf_model
    try:
        if hf_model is None:
            _load_fastembed_model()
        if hf_model is None:
            raise ValueError("FastEmbedding model failed to load. Check logs for details.")
        # FastEmbedding returns an iterator, get first result
        embeddings = list(hf_model.embed([text]))
        if len(embeddings) == 0:
            raise ValueError("FastEmbedding returned empty embedding")
        return embeddings[0].tolist()
    except ImportError as e:
        raise ValueError(f"FastEmbedding not installed: {str(e)}. Install with: pip install fastembed")
    except Exception as e:
        raise ValueError(f"FastEmbedding error: {str(e)}")

def generate_embedding(text: str, timeout: float = 10.0) -> List[float]:
    """
    Generates a vector embedding for a given text using OpenAI, Gemini, or FastEmbedding.
    Uses thread pool to prevent blocking and includes timeout protection.
    """
    try:
        if EMBEDDING_PROVIDER == "openai":
            response = openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        elif EMBEDDING_PROVIDER == "gemini":
            import google.generativeai as genai
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        elif EMBEDDING_PROVIDER == "huggingface":
            # Use thread pool for non-blocking embedding generation
            if hf_model is None:
                # Load model in background thread with timeout
                try:
                    future = _embedding_executor.submit(_load_fastembed_model)
                    future.result(timeout=30.0)  # 30s timeout for model loading
                except FutureTimeoutError:
                    raise ValueError("FastEmbedding model loading timed out after 30 seconds. Please check logs.")
                except Exception as e:
                    error_msg = f"Failed to load FastEmbedding model: {str(e)}. Install with: pip install fastembed"
                    print(f"❌ {error_msg}")
                    raise ValueError(error_msg)
            
            # Generate embedding in thread pool with timeout
            try:
                future = _embedding_executor.submit(_embed_text_fastembed, text)
                embedding = future.result(timeout=timeout)
                return embedding
            except FutureTimeoutError:
                raise ValueError(f"Embedding generation timed out after {timeout} seconds")
            except Exception as e:
                error_msg = f"Failed to generate embedding with FastEmbedding: {str(e)}"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
        else:
            raise ValueError(f"Unknown embedding provider: {EMBEDDING_PROVIDER}")
    except ValueError as ve:
        # Re-raise ValueError with clear message
        raise ve
    except ImportError as ie:
        error_msg = f"FastEmbedding not installed: {str(ie)}. Install with: pip install fastembed"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Error generating embedding with FastEmbedding: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        raise ValueError(error_msg)

class VectorDBClient:
    """Client for interacting with Qdrant vector database."""
    def __init__(self):
        def clean_env_var(value: str) -> str:
            """Clean environment variable - remove newlines and extra whitespace"""
            if not value:
                return ""
            return value.replace("\n", "").replace("\r", "").strip()
        
        qdrant_url = clean_env_var(os.getenv("QDRANT_URL", ""))
        qdrant_api_key_raw = os.getenv("QDRANT_API_KEY", "")
        qdrant_api_key = clean_env_var(qdrant_api_key_raw)
        self.collection_name = clean_env_var(os.getenv("QDRANT_COLLECTION_NAME", "physical_ai_book"))
        
        if not qdrant_url or not qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in environment variables")
        
        # Basic validation for Qdrant API key format (JWT)
        if not qdrant_api_key.startswith("ey") and len(qdrant_api_key) > 30: # JWTs start with ey
            print(f"⚠️ WARNING: QDRANT_API_KEY doesn't look like a JWT token. First 20 chars: {qdrant_api_key[:20]}")
        
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
        )
        self._ensure_collection()

    def _ensure_collection(self):
        """Creates the collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                print(f"📦 Collection '{self.collection_name}' not found. Creating...")
                # Get embedding dimension - use default if embedding fails
                try:
                    test_embedding = generate_embedding("test")
                    dimension = len(test_embedding)
                    print(f"✅ Embedding dimension detected: {dimension}")
                except Exception as e:
                    print(f"⚠️ Could not generate test embedding: {e}")
                    print("⚠️ Using default dimension: 384 (BAAI/bge-small-en-v1.5)")
                    dimension = 384  # Default for BAAI/bge-small-en-v1.5
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=dimension,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring collection: {e}")
            raise

    def upsert_chunks(self, chunks: List[TextChunk]):
        """Upserts text chunks into the vector database."""
        points = []
        for chunk in chunks:
            if not chunk.embedding:
                chunk.embedding = generate_embedding(chunk.text)
            
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=chunk.embedding,
                    payload={
                        "text": chunk.text,
                        "document_id": chunk.document_id,
                        "source_metadata": chunk.source_metadata,
                        "order_in_document": chunk.order_in_document,
                        "chunk_id": chunk.id
                    }
                )
            )
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Upserted {len(points)} chunks into vector DB")

    def retrieve_relevant_chunks(self, query_embedding: List[float], top_k: int = 5, selected_text: Optional[str] = None) -> List[TextChunk]:
        """Retrieves relevant chunks based on a query embedding using Qdrant Universal Query API."""
        try:
            # If selected text is provided, search only in that context
            query_filter = None
            if selected_text:
                # For selected text, we'll use a text-based filter
                # This is a simplified approach - in production, you might want more sophisticated filtering
                pass
            
            # Use Qdrant Query API - query() method (introduced in version 1.10.0)
            # This is the primary endpoint for retrieving points based on a query
            # For vector queries, construct a Query object with VectorInput
            query_result = self.client.query(
                collection_name=self.collection_name,
                query=Query(
                    vector=VectorInput(vector=query_embedding)
                ),
                limit=top_k,
                query_filter=query_filter,
                with_payload=True
            )
            
            # query() returns a QueryResponse object with .points attribute
            results = query_result.points if hasattr(query_result, 'points') else []
            
            chunks = []
            for result in results:
                # Handle both new and old API response formats
                if hasattr(result, 'payload'):
                    payload = result.payload
                elif isinstance(result, dict):
                    payload = result.get('payload', result)
                else:
                    payload = {}
                
                chunk = TextChunk(
                    id=payload.get("chunk_id", str(uuid.uuid4())),
                    document_id=payload.get("document_id", ""),
                    text=payload.get("text", ""),
                    embedding=None,  # Vector is not returned in query results
                    source_metadata=payload.get("source_metadata", ""),
                    order_in_document=payload.get("order_in_document", 0)
                )
                chunks.append(chunk)
            
            return chunks
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            import traceback
            traceback.print_exc()
            return []

def run_indexing_pipeline(docs_dir: str, vector_db_client: VectorDBClient):
    """Runs the full data ingestion and indexing pipeline."""
    print("Running indexing pipeline...")
    
    # Load all markdown documents
    documents = load_markdown_documents(docs_dir)
    print(f"Loaded {len(documents)} documents")
    
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
    
    print(f"Created {len(all_chunks)} chunks")
    
    # Upsert chunks in batches
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        vector_db_client.upsert_chunks(batch)
        print(f"Indexed batch {i//batch_size + 1}/{(len(all_chunks) + batch_size - 1)//batch_size}")
    
    print("Indexing pipeline completed.")

def reindex_content(vector_db_client: VectorDBClient, docs_dir: str):
    """Mechanisms to re-index content."""
    print("Re-indexing content...")
    run_indexing_pipeline(docs_dir, vector_db_client)
    print("Content re-indexed.")
