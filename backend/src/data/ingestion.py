import os
import sys
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.models.schemas import SourceDocument, TextChunk
from dotenv import load_dotenv
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import threading

# Load environment variables first
load_dotenv()

# CRITICAL: Remove proxy env vars BEFORE any imports that might use them (re-run as a safeguard)
# Some libraries (like requests/huggingface) can auto-detect proxies and fail in restrictive environments.
for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
    os.environ.pop(key, None)

# --- Configuration Helpers ---
def clean_env_var(value: str) -> str:
    """Clean environment variable - remove newlines and extra whitespace"""
    if not value:
        return ""
    return value.replace("\n", "").replace("\r", "").strip()

EMBEDDING_PROVIDER = clean_env_var(os.getenv("EMBEDDING_PROVIDER", "huggingface")).lower()
EMBEDDING_MODEL = clean_env_var(os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))

# --- Global Embedding State ---
hf_model = None
_model_lock = threading.Lock()
_embedding_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="embedding")

# --- Initialize Embedding Clients ---
if EMBEDDING_PROVIDER == "gemini":
    try:
        import google.generativeai as genai
        # Ensure GEMINI_API_KEY is available and configured
        gemini_api_key = clean_env_var(os.getenv("GEMINI_API_KEY", ""))
        if not gemini_api_key:
            print("❌ ERROR: GEMINI_API_KEY is not set for gemini provider.")
            sys.exit(1)
        genai.configure(api_key=gemini_api_key)
        EMBEDDING_MODEL = clean_env_var(os.getenv("EMBEDDING_MODEL", "models/embedding-001"))
    except ImportError:
        print("Warning: google-generativeai not installed. Install with: pip install google-generativeai")
elif EMBEDDING_PROVIDER == "huggingface":
    try:
        # Fastembed import is here to check if the library is available
        from fastembed import TextEmbedding
        # Model loading is lazy, so hf_model is kept None here
        print(f"Loading FastEmbedding model: {EMBEDDING_MODEL}")
        print("FastEmbedding is faster and lighter than sentence-transformers!")
        print(f"✅ FastEmbedding will be loaded on first use")
    except ImportError as e:
        print(f"❌ ERROR: fastembed not installed! Install with: pip install fastembed")
        print(f"Import error details: {e}")
        hf_model = None
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize FastEmbedding: {e}")
        import traceback
        traceback.print_exc()
        hf_model = None

# --- Text Splitting Configuration ---
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# --- Document Loading and Chunking ---
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
                # Use os.path.join for path construction consistency
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

# --- Embedding Generation ---
def _load_fastembed_model():
    """Load FastEmbedding model in a thread-safe way."""
    global hf_model
    with _model_lock:
        if hf_model is None:
            from fastembed import TextEmbedding
            model_name = clean_env_var(os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))
            print(f"Loading FastEmbedding model on-demand: {model_name}")
            try:
                # FastEmbedding caches models, so this is fast after the first time
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
            # Attempt to load if it's still None (should be handled by executor before)
            _load_fastembed_model() 
        if hf_model is None:
            raise ValueError("FastEmbedding model failed to load.")
        
        # FastEmbedding returns an iterator, get first result
        embeddings = list(hf_model.embed([text]))
        if not embeddings:
            raise ValueError("FastEmbedding returned empty embedding")
        return embeddings[0].tolist()
    except ImportError as e:
        raise ValueError(f"FastEmbedding not installed: {str(e)}. Install with: pip install fastembed")
    except Exception as e:
        # Catch any internal embedding errors (e.g., OOM, bad model download)
        raise ValueError(f"FastEmbedding error during embedding: {str(e)}")

def generate_embedding(text: str, timeout: float = 10.0) -> List[float]:
    """
    Generates a vector embedding for a given text using Gemini or FastEmbedding.
    Uses thread pool for non-blocking FastEmbedding and includes timeout protection.
    """
    if not text:
        # Return a zero vector or handle as error if text is empty
        # For BAAI/bge-small-en-v1.5 dimension is 384
        return [0.0] * 384 

    try:
        if EMBEDDING_PROVIDER == "gemini":
            import google.generativeai as genai
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        
        elif EMBEDDING_PROVIDER == "huggingface":
            # Load model if not loaded (with a long timeout, as this is a one-time operation)
            global hf_model
            if hf_model is None:
                try:
                    future = _embedding_executor.submit(_load_fastembed_model)
                    # Use a longer timeout for the initial model download/load
                    future.result(timeout=60.0) 
                except FutureTimeoutError:
                    raise ValueError("FastEmbedding model loading timed out after 60 seconds.")
                except Exception as e:
                    raise ValueError(f"Failed to load FastEmbedding model: {str(e)}")

            # Generate embedding with standard timeout
            try:
                future = _embedding_executor.submit(_embed_text_fastembed, text)
                embedding = future.result(timeout=timeout)
                return embedding
            except FutureTimeoutError:
                raise ValueError(f"Embedding generation timed out after {timeout} seconds")
            except Exception as e:
                # Re-raise the error caught in _embed_text_fastembed
                raise
        
        else:
            raise ValueError(f"Unknown embedding provider: {EMBEDDING_PROVIDER}")
            
    except Exception as e:
        error_msg = f"Error generating embedding: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        raise ValueError(error_msg)

# --- Qdrant Vector DB Client ---
class VectorDBClient:
    """Client for interacting with Qdrant vector database."""
    def __init__(self):
        # Nested clean_env_var to ensure it's available
        def clean_env_var(value: str) -> str:
            if not value:
                return ""
            return value.replace("\n", "").replace("\r", "").strip()
        
        qdrant_url = clean_env_var(os.getenv("QDRANT_URL", ""))
        qdrant_api_key_raw = os.getenv("QDRANT_API_KEY", "")
        
        # NOTE: Keeping the API key cleaning logic as it addresses a specific HF Spaces issue
        if "gsk_" in qdrant_api_key_raw and "eyJ" in qdrant_api_key_raw:
            parts = qdrant_api_key_raw.split("gsk_")
            for part in parts:
                if part.strip().startswith("eyJ"):
                    qdrant_api_key_raw = part.strip()
                    break
        
        qdrant_api_key = clean_env_var(qdrant_api_key_raw)
        self.collection_name = clean_env_var(os.getenv("QDRANT_COLLECTION_NAME", "physical_ai_book"))
        
        if not qdrant_url or not qdrant_api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in environment variables")
        
        if not qdrant_api_key.startswith("eyJ"):
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
                # Assuming BAAI/bge-small-en-v1.5 dimension (384)
                dimension = 384
                print(f"✅ Using FastEmbedding dimension: {dimension} (BAAI/bge-small-en-v1.5)")
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=dimension,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created collection: {self.collection_name} with dimension {dimension}")
            else:
                print(f"✅ Collection '{self.collection_name}' already exists")
        except Exception as e:
            print(f"❌ Error ensuring collection: {e}")
            import traceback
            traceback.print_exc()
            print("⚠️ Continuing without collection creation...")

    def upsert_chunks(self, chunks: List[TextChunk]):
        """Upserts text chunks into the vector database."""
        points = []
        for chunk in chunks:
            try:
                if not chunk.embedding:
                    # Generate embedding only if not already present
                    chunk.embedding = generate_embedding(chunk.text)
            except ValueError as e:
                print(f"⚠️ Skipping chunk due to embedding error: {e}")
                continue # Skip this chunk if embedding fails
            
            points.append(
                PointStruct(
                    # Use a unique ID (UUID is safe)
                    id=str(uuid.uuid4()), 
                    vector=chunk.embedding,
                    payload={
                        "text": chunk.text,
                        "document_id": chunk.document_id,
                        "source_metadata": chunk.source_metadata,
                        "order_in_document": chunk.order_in_document,
                        # Store chunk.id if TextChunk schema has one, otherwise remove
                        "chunk_id": chunk.id if hasattr(chunk, 'id') and chunk.id else str(uuid.uuid4())
                    }
                )
            )
        
        if points:
            # Use points_count for better logging
            points_count = len(points)
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True # Wait for the operation to complete
            )
            print(f"Upserted {points_count} chunks into vector DB")
        else:
            print("No points to upsert.")

    def retrieve_relevant_chunks(self, query_embedding: List[float], top_k: int = 5, selected_text: Optional[str] = None) -> List[TextChunk]:
        """Retrieves relevant chunks based on a query embedding using Qdrant search API."""
        try:
            query_filter = None
            # Note: For filtering by text content like 'selected_text', you would need 
            # to implement a `FieldCondition` or `TextIndex` filter in Qdrant,
            # which is complex and outside the scope of the basic fix. 
            # We keep query_filter simple/None for pure vector search.

            # CRITICAL FIX: The use of self.client.search() requires qdrant-client >= 1.1.0.
            # If your environment uses an older version, you must update the library.
            # If you are stuck on an old version, change .search to .search_points
            query_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter,
                with_payload=True,
                # Optionally add: with_vectors=False to save bandwidth
            )
            
            # The result is a list of ScoredPoint objects
            results = query_result if isinstance(query_result, list) else []
            
            chunks = []
            for result in results:
                payload = result.payload
                
                chunk = TextChunk(
                    # Use payload data
                    id=payload.get("chunk_id", str(uuid.uuid4())),
                    document_id=payload.get("document_id", ""),
                    text=payload.get("text", ""),
                    embedding=None, # Embedding is not needed for the final answer, so we don't retrieve it
                    source_metadata=payload.get("source_metadata", ""),
                    order_in_document=payload.get("order_in_document", 0),
                    # Add the relevance score for debugging/ranking (optional)
                    score=result.score
                )
                chunks.append(chunk)
            
            return chunks
        except AttributeError as ae:
            # Specific error handling for the missing attribute
            print(f"Error retrieving chunks: 'QdrantClient' object has no attribute 'search'")
            print(f"This typically means your 'qdrant-client' package is too old.")
            print(f"Please update your 'qdrant-client' dependency to version 1.1.0 or newer.")
            import traceback
            traceback.print_exc()
            return []
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            import traceback
            traceback.print_exc()
            return []

# --- Indexing Pipeline ---
def run_indexing_pipeline(docs_dir: str, vector_db_client: VectorDBClient):
    """Runs the full data ingestion and indexing pipeline."""
    print("Running indexing pipeline...")
    
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