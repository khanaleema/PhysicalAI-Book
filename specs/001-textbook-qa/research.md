# Research Plan: Constitution-Aware Textbook QA Bot

**Feature Branch**: `001-textbook-qa` | **Date**: 2025-11-30 | **Spec**: [specs/001-textbook-qa/spec.md](specs/001-textbook-qa/spec.md)
**Plan**: [specs/001-textbook-qa/plan.md](specs/001-textbook-qa/plan.md)

## Phase 0: Research Questions & Areas

This document outlines key research areas to resolve technical uncertainties and guide optimal design decisions for the Constitution-Aware Textbook QA Bot.

### 1. RAG System Architecture Best Practices for Educational Chatbots

*   **Decision**: To be made after research on optimal RAG design for question-answering over structured educational content.
*   **Rationale**: Ensure an efficient, scalable, and accurate retrieval process tailored for a textbook-specific knowledge base, supporting deep understanding and precise answers.
*   **Alternatives Considered**:
    *   Simple keyword matching: Rejected for lack of semantic understanding.
    *   Direct LLM prompting without retrieval: Rejected due to hallucination risk and inability to cite sources reliably.
    *   Fine-tuning LLM directly on textbook: Rejected due to cost, difficulty in updating, and hallucination risk without retrieval.

### 2. Strategies for Controlling LLM Output for Strict Adherence

*   **Decision**: To be made after research on advanced prompting techniques, guardrail implementation, and potential post-processing.
*   **Rationale**: Crucial for enforcing the "no guessing" and "textbook-only" constitutional rules, minimizing hallucinations, and maintaining factual integrity.
*   **Alternatives Considered**:
    *   Basic system prompts: Might not be sufficient for strict control.
    *   Only using smaller, less capable LLMs: Might limit reasoning capabilities.

### 3. Comparison of Vector Databases for Efficient Content Storage and Retrieval

*   **Decision**: Selection of a vector database (e.g., Pinecone, Weaviate, Milvus, FAISS, ChromaDB, Elasticsearch with vector capabilities).
*   **Rationale**: Optimize for fast, accurate semantic search over textbook and constitution embeddings, ensuring low-latency retrieval for real-time QA. Consider factors like scalability, cost, ease of deployment, and integration with Python RAG frameworks.
*   **Alternatives Considered**:
    *   Relational databases with vector extensions: Potentially slower for high-dimensional vector search.
    *   In-memory vector stores: Not suitable for persistence and large scale.

### 4. Methods for Reliable Source Citation from Retrieved Chunks

*   **Decision**: To be made after research on techniques to robustly link LLM-generated answers back to specific textbook pages or sections from retrieved chunks.
*   **Rationale**: Essential for meeting the constitutional requirement (Section 4, Rule 3) to "Always cite which part of the book the answer is based on" and for building user trust.
*   **Alternatives Considered**:
    *   Simple chunk ID tracking: May not provide granular enough citation (e.g., page number vs. entire chapter).
    *   LLM-generated citations: Prone to hallucination if not carefully managed.

### 5. Techniques for Validating LLM Responses Against Constitutional Rules

*   **Decision**: To be made after research on automated or semi-automated methods for evaluating LLM outputs against a predefined set of constitutional constraints.
*   **Rationale**: Implement a robust post-processing layer to ensure 100% compliance with `constitution.md` (SC-002 in `spec.md`), catching any potential violations before the response is delivered to the user.
*   **Alternatives Considered**:
    *   Manual review: Not scalable or efficient.
    *   LLM self-correction: Can be unreliable without external validation.

## Next Steps

-   Conduct in-depth research for each of the areas identified above.
-   Document findings and proposed solutions to resolve each research question.
-   Update `plan.md` with resolved technical decisions.
