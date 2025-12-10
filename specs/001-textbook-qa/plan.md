# Implementation Plan: Constitution-Aware Textbook QA Bot

**Branch**: `001-textbook-qa` | **Date**: 2025-11-30 | **Spec**: [specs/001-textbook-qa/spec.md](specs/001-textbook-qa/spec.md)
**Input**: Feature specification from `/specs/001-textbook-qa/spec.md`

## Summary

**Primary Requirement:** Develop a chatbot that provides accurate, textbook-sourced answers while strictly adhering to a defined constitution (`constitution.md`), avoiding any form of guessing or external knowledge.

**Technical Approach:** Implement a Retrieval-Augmented Generation (RAG) system. This involves indexing the "Physical AI & Humanoid Robotics Textbook" and `constitution.md` into a vector database. User queries will be embedded, used to retrieve relevant sections from the database, and then combined with constitutional rules to prompt a large language model (LLM) for a constrained, accurate response. Post-processing will validate constitutional adherence and handle out-of-scope queries.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: LangChain/LlamaIndex (for RAG orchestration), a vector database client (e.g., Pinecone/Weaviate client), a powerful LLM client (e.g., OpenAI API, Anthropic API, Gemini API), FastAPI (for API).  
**Storage**: Vector Database (for embeddings and text chunks), potentially a simple file system for source documents.  
**Testing**: pytest (for unit, integration, and end-to-end tests).  
**Target Platform**: Linux server (containerized environment).  
**Project Type**: Web application (API backend).  
**Performance Goals**:
-   P95 latency for query response < 5 seconds.
-   Ability to process 10 concurrent requests without significant degradation.
-   Textbook indexing for 1000 pages within 1 hour.  
**Constraints**:
-   Strict adherence to `constitution.md`.
-   Only uses information from the specified "physical ai & humanoid robotics textbook" and `constitution.md`.
-   No external data fetching during runtime.
-   Scalability for handling multiple users simultaneously.  
**Scale/Scope**:
-   Supports the full "Physical AI & Humanoid Robotics Textbook" (approx. 500-1000 pages).
-   Handles a single `constitution.md` file.
-   Serves 100-500 daily active users.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Exclusive Knowledge Sources (Constitution Section 2)
**Check**: Does the plan ensure the chatbot uses ONLY the textbook, constitution, and approved RAG index materials?
**Evaluation**: PASS. The RAG architecture is explicitly designed for this, by embedding and retrieving solely from these sources. The LLM will be prompted with only retrieved text and constitutional rules.

### Gate 2: No Guessing/External Facts (Constitution Section 2 & 4)
**Check**: Does the plan prevent guessing, external internet facts, speculation, or personal opinions?
**Evaluation**: PASS. RAG architecture limits LLM context. LLM prompting will include explicit instructions against guessing and hallucination prevention. A "not in textbook" fallback response is planned for unknown topics (FR-005, SC-003 in `spec.md`).

### Gate 3: Constitutional Adherence in Responses (Constitution Section 3, 4, 7)
**Check**: Does the plan enforce all behavior rules, safety & accuracy rules, and prohibited actions during response generation?
**Evaluation**: PASS. LLM prompting will embed constitutional rules. A post-processing step for constitutional validation and conflict resolution (FR-003, FR-007, SC-002 in `spec.md`) is planned.

### Gate 4: Source Citation (Constitution Section 4 & 6)
**Check**: Does the plan ensure answers cite the relevant part of the book and follow the specified response format?
**Evaluation**: PASS. RAG architecture will provide source chunks. LLM prompting will instruct on citation (FR-008 in `spec.md`). The response format will be guided by prompt engineering based on Constitution Section 6.

### Gate 5: Chatbot Identity (Constitution Section 5)
**Check**: Does the plan ensure the chatbot identifies correctly as "The Physical AI & Humanoid Robotics Course Assistant" and not as a general-purpose AI?
**Evaluation**: PASS. The LLM's system prompt will explicitly establish this identity and role.

## Project Structure

### Documentation (this feature)

```text
specs/001-textbook-qa/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Structure Decision**: A Python-based backend will provide the core RAG and chatbot API. A separate, simple frontend is out of scope for the planning phase, but the API will be designed for easy integration.

```text
backend/
├── src/
│   ├── api/             # FastAPI application endpoints
│   ├── core/            # Core RAG logic, LLM interaction, constitutional enforcement
│   ├── data/            # Data ingestion, chunking, embedding, vector DB interaction
│   └── models/          # Data models for requests/responses, entities
├── tests/
│   ├── unit/            # Unit tests for core logic
│   ├── integration/     # Integration tests for RAG pipeline, API endpoints
│   └── e2e/             # End-to-end tests for chatbot behavior
└── data/                # Placeholder for textbook and constitution files (raw source)
```

## Complexity Tracking

[None]