"""
Test script to fetch and display data from Qdrant vector database.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Remove proxy env vars before imports
for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
    os.environ.pop(key, None)

def clean_env_var(value: str) -> str:
    """Clean environment variable"""
    if not value:
        return ""
    return value.replace("\n", "").replace("\r", "").strip()

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import ScrollRequest
    
    print("=" * 60)
    print("Qdrant Database Test")
    print("=" * 60)
    
    # Get Qdrant configuration
    qdrant_url = clean_env_var(os.getenv("QDRANT_URL", ""))
    qdrant_api_key_raw = os.getenv("QDRANT_API_KEY", "")
    collection_name = clean_env_var(os.getenv("QDRANT_COLLECTION_NAME", "physical_ai_book"))
    
    # Fix concatenated API keys (if needed)
    if "gsk_" in qdrant_api_key_raw and "eyJ" in qdrant_api_key_raw:
        parts = qdrant_api_key_raw.split("gsk_")
        if len(parts) > 1:
            for part in parts:
                if part.strip().startswith("eyJ"):
                    qdrant_api_key_raw = part.strip()
                    break
    
    qdrant_api_key = clean_env_var(qdrant_api_key_raw)
    
    if not qdrant_url or not qdrant_api_key:
        print("❌ ERROR: QDRANT_URL and QDRANT_API_KEY must be set")
        print(f"   QDRANT_URL: {'SET' if qdrant_url else 'NOT SET'}")
        print(f"   QDRANT_API_KEY: {'SET' if qdrant_api_key else 'NOT SET'}")
        sys.exit(1)
    
    print(f"\n📡 Connecting to Qdrant...")
    print(f"   URL: {qdrant_url}")
    print(f"   Collection: {collection_name}")
    print(f"   API Key: {'SET' if qdrant_api_key else 'NOT SET'} (first 20 chars: {qdrant_api_key[:20]}...)")
    
    # Connect to Qdrant
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
    )
    
    # Check collections
    print(f"\n📦 Checking collections...")
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    print(f"   Found {len(collection_names)} collection(s): {collection_names}")
    
    if collection_name not in collection_names:
        print(f"   ⚠️  Collection '{collection_name}' not found!")
        print(f"   Available collections: {collection_names}")
        sys.exit(1)
    
    # Get collection info
    print(f"\n📊 Collection Info:")
    collection_info = client.get_collection(collection_name)
    print(f"   Name: {collection_name}")
    print(f"   Points Count: {collection_info.points_count}")
    
    # Try to get vector config info
    try:
        if hasattr(collection_info, 'config') and hasattr(collection_info.config, 'params'):
            if hasattr(collection_info.config.params, 'vectors'):
                vectors_config = collection_info.config.params.vectors
                if hasattr(vectors_config, 'size'):
                    print(f"   Vector Size: {vectors_config.size}")
                if hasattr(vectors_config, 'distance'):
                    print(f"   Distance: {vectors_config.distance}")
    except Exception:
        pass
    
    if collection_info.points_count == 0:
        print("\n⚠️  WARNING: Collection is empty! No data indexed.")
        print("   You need to run the indexing script to add content.")
        sys.exit(0)
    
    # Scroll through some points to see the data
    print(f"\n🔍 Fetching sample data (first 5 points)...")
    scroll_result = client.scroll(
        collection_name=collection_name,
        limit=5,
        with_payload=True,
        with_vectors=False  # Don't fetch vectors to save space
    )
    
    points = scroll_result[0]
    print(f"   Retrieved {len(points)} points\n")
    
    for i, point in enumerate(points, 1):
        print(f"   Point {i}:")
        print(f"      ID: {point.id}")
        payload = point.payload
        print(f"      Document ID: {payload.get('document_id', 'N/A')}")
        print(f"      Source: {payload.get('source_metadata', 'N/A')}")
        text = payload.get('text', '')
        text_preview = text[:100] + "..." if len(text) > 100 else text
        print(f"      Text Preview: {text_preview}")
        print()
    
    # Test a search query using VectorDBClient (same as the app uses)
    print(f"\n🔎 Testing search query: 'ROS 2'...")
    try:
        from src.data.ingestion import VectorDBClient, generate_embedding
        
        # Use VectorDBClient which has the working search method
        vector_db = VectorDBClient()
        
        query_text = "ROS 2"
        print(f"   Generating embedding for: '{query_text}'...")
        query_embedding = generate_embedding(query_text)
        print(f"   Embedding dimension: {len(query_embedding)}")
        
        # Use the retrieve_relevant_chunks method (same as RAG pipeline uses)
        print(f"   Searching for relevant chunks...")
        relevant_chunks = vector_db.retrieve_relevant_chunks(
            query_embedding=query_embedding,
            top_k=5
        )
        
        print(f"   Found {len(relevant_chunks)} results:\n")
        for i, chunk in enumerate(relevant_chunks, 1):
            print(f"   Result {i}:")
            print(f"      Source: {chunk.source_metadata}")
            print(f"      Document ID: {chunk.document_id}")
            text_preview = chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
            print(f"      Text: {text_preview}")
            print()
            
    except Exception as e:
        print(f"   ⚠️  Search test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
    print("✅ Test completed!")
    print("=" * 60)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're in the backend directory and dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

