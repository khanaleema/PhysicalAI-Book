#!/usr/bin/env python3
"""
Script to index the book content into Qdrant vector database.
Run this script after setting up your .env file with API credentials.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.ingestion import VectorDBClient, run_indexing_pipeline
from dotenv import load_dotenv

load_dotenv()

def main():
    # Path to book docs directory
    # Adjust this path based on your project structure
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    book_docs_dir = project_root / "book" / "docs"
    book_docs_dir = str(book_docs_dir)
    
    if not os.path.exists(book_docs_dir):
        print(f"Error: Book docs directory not found at {book_docs_dir}")
        print("Please ensure the book/docs directory exists.")
        sys.exit(1)
    
    print(f"Indexing book content from: {book_docs_dir}")
    
    try:
        # Initialize vector DB client
        vector_db_client = VectorDBClient()
        
        # Run indexing pipeline
        run_indexing_pipeline(book_docs_dir, vector_db_client)
        
        print("\n✅ Book indexing completed successfully!")
        print("You can now start the FastAPI server and use the chatbot.")
        
    except Exception as e:
        print(f"\n❌ Error during indexing: {e}")
        print("\nPlease check:")
        print("1. Your .env file has correct QDRANT_URL and QDRANT_API_KEY")
        print("2. Your .env file has correct OPENAI_API_KEY")
        print("3. The book/docs directory exists and contains markdown files")
        sys.exit(1)

if __name__ == "__main__":
    main()

