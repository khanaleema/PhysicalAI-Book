# Quickstart Guide: Constitution-Aware Textbook QA Bot (Local Development)

**Feature Branch**: `001-textbook-qa` | **Date**: 2025-11-30 | **Spec**: [specs/001-textbook-qa/spec.md](specs/001-textbook-qa/spec.md)
**Plan**: [specs/001-textbook-qa/plan.md](specs/001-textbook-qa/plan.md)

This guide provides a basic overview to get a local development environment for the Constitution-Aware Textbook QA Bot backend up and running with dummy data.

## Prerequisites

*   Python 3.10+ installed
*   `pip` (Python package installer)
*   `git` (optional, for cloning the repository if not already done)
*   A text editor/IDE (e.g., VS Code)

## 1. Setup Project Structure (Manual for now)

Assuming you have the basic project structure:

```
.
└── backend/
    ├── src/
    │   ├── api/
    │   ├── core/
    │   ├── data/
    │   └── models/
    └── data/
        └── dummy_textbook_content.txt
        └── dummy_constitution.md
```

## 2. Prepare Dummy Data

Create placeholder files in `backend/data/`:

**`backend/data/dummy_textbook_content.txt`**:

```text
# Physical AI & Humanoid Robotics Textbook - Dummy Content

## Chapter 1: Introduction to Physical AI
Physical AI refers to intelligent systems that interact with the physical world. Unlike purely software-based AI, physical AI systems, such as robots, have a body and sensors that allow them to perceive and act in their environment.

## Chapter 2: Basics of Humanoid Robotics
Humanoid robots are robots with their overall body shape built to resemble the human body. They typically have a torso, a head, two arms, and two legs. They are designed to mimic human movements and interactions.
```

**`backend/data/dummy_constitution.md`**:

```markdown
# Chatbot Constitution - Dummy

## 2. Allowed Knowledge Sources
The chatbot is allowed to use ONLY:
1. The Textbook
2. This Constitution
❌ Not allowed: Guessing or external internet facts.

## 4. Safety & Accuracy Rules
1. No hallucinations.
2. If information is not in the textbook -> reply: "This topic is not in the textbook, so I cannot answer it."
```

## 3. Install Dependencies (Example)

Navigate to the `backend/` directory and create a `requirements.txt` (or `pyproject.toml`) for your Python dependencies.

Example `backend/requirements.txt`:

```
fastapi
uvicorn
langchain
pydantic
numpy
# Add chosen vector database client (e.g., pinecone-client)
# Add chosen LLM client (e.g., openai)
```

Then install:

```bash
cd backend/
pip install -r requirements.txt
```

## 4. Basic RAG Indexing Script (Conceptual)

Create a conceptual Python script (e.g., `backend/src/data/index_data.py`) to process and index your dummy data:

```python
# backend/src/data/index_data.py (Conceptual)
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SomeEmbeddingsModel # Replace with actual
from langchain_community.vectorstores import SomeVectorStore # Replace with actual

def index_dummy_data():
    # Load documents
    textbook_path = os.path.join("..", "..", "data", "dummy_textbook_content.txt")
    constitution_path = os.path.join("..", "..", "data", "dummy_constitution.md")

    textbook_loader = TextLoader(textbook_path)
    constitution_loader = TextLoader(constitution_path)

    documents = textbook_loader.load() + constitution_loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    # Generate embeddings and store in vector database
    # embeddings = SomeEmbeddingsModel() # Initialize your embedding model
    # vector_store = SomeVectorStore()   # Initialize your vector store
    # vector_store.add_documents(chunks, embeddings)

    print("Dummy data indexed (conceptual).")

if __name__ == "__main__":
    index_dummy_data()
```

Run this script:

```bash
python backend/src/data/index_data.py
```

## 5. Basic API Server (Conceptual)

Create a conceptual FastAPI application (e.g., `backend/src/api/main.py`) to expose the `/query` endpoint:

```python
# backend/src/api/main.py (Conceptual)
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class UserQuery(BaseModel):
    text: str
    session_id: Optional[str] = None

class CitedSource(BaseModel):
    document_id: str
    source_metadata: str

class ChatbotResponse(BaseModel):
    text: str
    constitutional_compliance_status: str
    cited_sources: List[CitedSource]
    query_id: Optional[str] = None

# Conceptual RAG processing function
def process_query_with_rag(query_text: str) -> ChatbotResponse:
    # In a real implementation:
    # 1. Embed query_text
    # 2. Retrieve relevant chunks from vector DB (textbook & constitution)
    # 3. Formulate LLM prompt with query, chunks, and constitutional rules
    # 4. Invoke LLM
    # 5. Post-process LLM response for constitutional compliance and citation
    
    # Dummy response for quickstart
    if "physical ai" in query_text.lower():
        return ChatbotResponse(
            text="Physical AI involves intelligent systems interacting with the physical world, often through robots.",
            constitutional_compliance_status="COMPLIANT",
            cited_sources=[{"document_id": "dummy_textbook", "source_metadata": "Chapter 1: Introduction to Physical AI"}]
        )
    elif "constitution" in query_text.lower():
        return ChatbotResponse(
            text="The chatbot is only allowed to use the textbook and constitution as knowledge sources.",
            constitutional_compliance_status="COMPLIANT",
            cited_sources=[{"document_id": "dummy_constitution", "source_metadata": "Section 2: Allowed Knowledge Sources"}]
        )
    else:
        return ChatbotResponse(
            text="This topic is not in the textbook, so I cannot answer it.",
            constitutional_compliance_status="COMPLIANT",
            cited_sources=[]
        )

@app.post("/query", response_model=ChatbotResponse)
async def query_chatbot(query: UserQuery):
    response = process_query_with_rag(query.text)
    # Assign query_id if needed, for this quickstart we'll omit
    return response

```

Run the API server:

```bash
uvicorn backend.src.api.main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`. You can test it using `curl` or a tool like Postman/Insomnia.

## 6. Testing (Conceptual)

While the server is running, send a POST request:

```bash
curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"text": "What is physical AI?"}'
```

Expected (example) response:

```json
{
  "text": "Physical AI involves intelligent systems interacting with the physical world, often through robots.",
  "constitutional_compliance_status": "COMPLIANT",
  "cited_sources": [
    {
      "document_id": "dummy_textbook",
      "source_metadata": "Chapter 1: Introduction to Physical AI"
    }
  ],
  "query_id": null
}
```
