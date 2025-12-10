#!/usr/bin/env python3
"""Check if book content is properly indexed."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

from src.data.ingestion import VectorDBClient

try:
    client = VectorDBClient()
    
    # Check collection info
    collection_info = client.client.get_collection("physical_ai_book")
    print(f"Collection: physical_ai_book")
    print(f"Points count: {collection_info.points_count}")
    if hasattr(collection_info.config, 'params') and hasattr(collection_info.config.params, 'vectors'):
        print(f"Vector size: {collection_info.config.params.vectors.size}")
    
    # Get sample points
    print("\nFetching sample points...")
    result = client.client.scroll(
        collection_name="physical_ai_book",
        limit=10
    )
    
    points = result[0]
    print(f"\nFound {len(points)} points in collection")
    
    if points:
        print("\nSample points:")
        for i, point in enumerate(points[:5], 1):
            payload = point.payload
            text_preview = payload.get("text", "")[:100]
            source = payload.get("source_metadata", "unknown")
            print(f"{i}. Source: {source}")
            print(f"   Text: {text_preview}...")
            print()
    else:
        print("\n❌ NO POINTS FOUND! Book content is NOT indexed.")
        print("   Run: python scripts/index_book.py")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

