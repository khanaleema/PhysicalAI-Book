# Implementation Tasks: Constitution-Aware Textbook QA Bot

**Feature Branch**: `001-textbook-qa` | **Date**: 2025-11-30 | **Spec**: [specs/001-textbook-qa/spec.md](specs/001-textbook-qa/spec.md)
**Plan**: [specs/001-textbook-qa/plan.md](specs/001-textbook-qa/plan.md)

This document breaks down the implementation of the Constitution-Aware Textbook QA Bot into actionable, testable tasks, organized by the proposed project structure and technical components.

## Phase 2: Implementation Tasks

### 1. Project Setup & Infrastructure (backend/)

*   [x] **Task 1.1: Initialize Python Project**
    *   Description: Create a new Python project structure, set up a virtual environment, and initialize a `backend/` directory.
    *   Acceptance Criteria: Python virtual environment created and activated. `backend/` directory exists.
*   **Task 1.2: FastAPI Project Initialization**
    *   Description: Initialize a basic FastAPI application within `backend/src/api/` and configure `uvicorn` for local development.
    *   Acceptance Criteria: FastAPI app runs locally with a minimal endpoint (e.g., `/health`).
*   [x] **Task 1.3: Core Project Structure Setup**
    *   Description: Create the `backend/src/core`, `backend/src/data`, `backend/src/models` directories as defined in `plan.md`.
    *   Acceptance Criteria: All necessary subdirectories are created within `backend/src/`.
*   [x] **Task 1.4: Install Core Dependencies**
    *   Description: Add and install core Python dependencies: `fastapi`, `uvicorn`, `pydantic`, `langchain` (or `llama_index`), `numpy`, and a client for the chosen vector database and LLM.
    *   Acceptance Criteria: `requirements.txt` (or equivalent) is defined and all dependencies are successfully installed.

### 2. Data Ingestion & Indexing (backend/src/data)

*   [x] **Task 2.1: Define Data Models for Documents & Chunks**
    *   Description: Translate `UserQuery`, `SourceDocument`, `TextChunk`, and `ChatbotResponse` from `data-model.md` into Pydantic models in `backend/src/models/`.
    *   Acceptance Criteria: Pydantic models for core entities are created and validated.
*   [x] **Task 2.2: Implement Document Loaders**
    *   Description: Develop modules to load content from `constitution.md` and the "physical ai & humanoid robotics textbook" (supporting Markdown, plain text formats).
    *   Acceptance Criteria: Raw content from source files can be loaded into `SourceDocument` objects.
*   [x] **Task 2.3: Implement Text Chunking Strategy**
    *   Description: Implement `RecursiveCharacterTextSplitter` (or equivalent) to break down `SourceDocument` content into `TextChunk` objects.
    *   Acceptance Criteria: Documents are successfully chunked, respecting `chunk_size` and `chunk_overlap` settings.
*   [x] **Task 2.4: Integrate Embedding Model**
    *   Description: Choose and integrate a suitable embedding model (e.g., from `HuggingFaceTransformersEmbeddings`, `OpenAIEmbeddings`) to generate vector representations for `TextChunk` content.
    *   Acceptance Criteria: `TextChunk` objects can be converted into valid embedding vectors.
*   [x] **Task 2.5: Integrate Vector Database Client**
    *   Description: Integrate the client for the chosen vector database (e.g., Pinecone, Weaviate, ChromaDB) into the `backend/src/data` module.
    *   Acceptance Criteria: Connection to the vector database can be established, and basic client operations (e.g., upsert, query) are functional.
*   [x] **Task 2.6: Implement Indexing Pipeline**
    *   Description: Develop an end-to-end pipeline to load source documents, chunk them, generate embeddings, and store them in the vector database.
    *   Acceptance Criteria: `constitution.md` and dummy textbook content are successfully indexed into the vector database.
*   [x] **Task 2.7: Implement Content Update/Re-indexing Mechanism**
    *   Description: Create a script or function to allow for periodic or triggered re-indexing of source content if `constitution.md` or the textbook changes.
    *   Acceptance Criteria: Content updates are reflected in the vector database after re-indexing.

### 3. Core RAG Logic (backend/src/core)

*   [x] **Task 3.1: Implement Query Embedding Generation**
    *   Description: Use the same embedding model from Task 2.4 to generate embeddings for incoming `UserQuery` objects.
    *   Acceptance Criteria: `UserQuery` text can be converted into valid embedding vectors.
*   [x] **Task 3.2: Implement Contextual Retrieval**
    *   Description: Perform a similarity search in the vector database using the query embedding to retrieve the most relevant `TextChunk`s from both textbook and constitution sources.
    *   Acceptance Criteria: Relevant chunks are returned from the vector database based on the query.
*   [x] **Task 3.3: Implement LLM Prompt Construction**
    *   Description: Formulate a robust LLM prompt that includes the `UserQuery`, retrieved `TextChunk`s, and explicit instructions derived from `constitution.md` (e.g., "answer ONLY from provided text," "do not guess").
    *   Acceptance Criteria: Prompts are well-formed and include all necessary context and constraints.
*   [x] **Task 3.4: Integrate LLM Provider**
    *   Description: Integrate with the chosen LLM API (e.g., OpenAI, Anthropic, Gemini) for invoking the large language model.
    *   Acceptance Criteria: LLM can be successfully invoked with a prompt and returns a response.
*   [x] **Task 3.5: Implement Initial LLM Response Generation**
    *   Description: Send the constructed prompt to the LLM and capture its raw response.
    *   Acceptance Criteria: Raw LLM response is received for a given prompt.
*   [x] **Task 3.6: Develop Constitutional Compliance Post-Processing**
    *   Description: Implement a module to analyze the LLM's raw response and validate its adherence to rules in `constitution.md` (e.g., neutrality, no harmful speech, no guessing). Set `constitutional_compliance_status`.
    *   Acceptance Criteria: LLM responses are checked against constitutional rules, and a compliance status is assigned.
*   [x] **Task 3.7: Implement Source Citation Extraction**
    *   Description: From the retrieved `TextChunk`s and the LLM's response, extract and format accurate `cited_sources` metadata (`document_id`, `source_metadata`) for `FR-008`.
    *   Acceptance Criteria: Chatbot responses include correct and traceable source citations.
*   [x] **Task 3.8: Implement "Not in Textbook" Handling**
    *   Description: Develop logic to detect if the LLM cannot find an answer within the provided context and trigger the appropriate "This topic is not in the textbook, so I cannot answer it" response (`FR-005`, `Constitution Section 4`).
    *   Acceptance Criteria: When a query is demonstrably outside the knowledge base, the correct fallback message is returned.

### 4. API Endpoints (backend/src/api)

*   [x] **Task 4.1: Implement `POST /query` Endpoint**
    *   Description: Create the FastAPI endpoint `/query` that accepts a `UserQuery` and returns a `ChatbotResponse`, as defined in `contracts/query_api.yaml`.
    *   Acceptance Criteria: API endpoint is accessible and correctly processes `UserQuery` requests.
*   [x] **Task 4.2: Integrate Core RAG Logic into API**
    *   Description: Connect the `/query` endpoint to the `backend/src/core` RAG pipeline to process user queries.
    *   Acceptance Criteria: API endpoint successfully calls the core RAG logic and receives responses.
*   [x] **Task 4.3: Implement Request/Response Serialization**
    *   Description: Ensure proper serialization of incoming `UserQuery` and outgoing `ChatbotResponse` using Pydantic models.
    *   Acceptance Criteria: API handles valid JSON requests and returns valid JSON responses according to `query_api.yaml`.
*   [x] **Task 4.4: Implement API Error Handling**
    *   Description: Add error handling for common API issues (e.g., invalid input -> 400 Bad Request, internal processing errors -> 500 Internal Server Error).
    *   Acceptance Criteria: API returns appropriate HTTP status codes and error messages for invalid requests or failures.

### 5. Testing (backend/tests)

*   [x] **Task 5.1: Setup Pytest Framework**
    *   Description: Configure `pytest` for the `backend/` project, including test discovery and basic fixtures.
    *   Acceptance Criteria: `pytest` runs successfully, discovering any placeholder tests.
*   [x] **Task 5.2: Unit Tests for Data Ingestion**
    *   Description: Write unit tests for document loaders, chunking logic, and embedding generation modules.
    *   Acceptance Criteria: All data ingestion utility functions have comprehensive unit test coverage.
*   [x] **Task 5.3: Unit Tests for Core RAG Components**
    *   Description: Write unit tests for prompt construction, LLM invocation (mocked), response post-processing, and source citation extraction.
    *   Acceptance Criteria: Core RAG logic components are thoroughly unit tested.
*   [x] **Task 5.4: Integration Tests for RAG Pipeline**
    *   Description: Write integration tests to verify the flow from raw document to indexed vector store, and from query to retrieved chunks.
    *   Acceptance Criteria: The RAG pipeline components work together correctly.
*   [x] **Task 5.5: API Integration Tests**
    *   Description: Write tests for the `POST /query` endpoint, verifying request handling, response formatting, and error cases.
    *   Acceptance Criteria: API endpoints function as expected under various valid and invalid inputs.
*   [x] **Task 5.6: End-to-End Tests for User Scenarios**
    *   Description: Implement end-to-end tests covering `User Story 1 (Textbook Q&A)`, `User Story 2 (Constitutional Adherence)`, and `User Story 3 (Out-of-Scope Question)` from `spec.md`.
    *   Acceptance Criteria: All primary user stories are validated through automated E2E tests, including edge cases (e.g., unclear queries, no information, constitutional conflict).

### 6. Deployment & Monitoring (Future)

*   [x] **Task 6.1: Dockerize FastAPI Application**
    *   Description: Create a `Dockerfile` to containerize the `backend` FastAPI application for consistent deployment.
    *   Acceptance Criteria: Docker image builds successfully and the container runs.
*   [x] **Task 6.2: Basic Logging & Metrics**
    *   Description: Implement basic application logging (e.g., `logging` module) and integrate a simple metrics collection mechanism (e.g., Prometheus client) for key performance indicators.
    *   Acceptance Criteria: Application logs are generated, and basic metrics can be exposed.
