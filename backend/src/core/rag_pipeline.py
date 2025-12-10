import os
# Remove proxies before any imports
for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
    os.environ.pop(key, None)

from typing import Optional, List
from datetime import datetime
import uuid
from src.data.ingestion import clean_env_var, generate_embedding, VectorDBClient
from src.models.schemas import UserQuery, ChatbotResponse

class LLMProvider:
    """
    LLM provider integration for Physical AI textbook.
    Supports: openai, groq, huggingface, gemini
    """

    def __init__(self):
        self.provider = clean_env_var(os.getenv("LLM_PROVIDER", "gemini")).lower()

        # ------------------ GEMINI ------------------
        if self.provider == "gemini":
            import google.generativeai as genai
            api_key = clean_env_var(os.getenv("GEMINI_API_KEY", ""))
            if not api_key:
                raise ValueError("Missing GEMINI_API_KEY")

            genai.configure(api_key=api_key)
            self.model_name = clean_env_var(os.getenv("LLM_MODEL", "gemini-2.5-flash"))
            self.model = genai.GenerativeModel(self.model_name)

        # ------------------ OPENAI ------------------
        elif self.provider == "openai":
            from openai import OpenAI

            api_key = clean_env_var(os.getenv("OPENAI_API_KEY", ""))
            if not api_key:
                raise ValueError("Missing OPENAI_API_KEY")

            # ❗ FIX: no http_client, no proxies argument
            self.client = OpenAI(api_key=api_key)
            self.model_name = clean_env_var(os.getenv("LLM_MODEL", "gpt-4o-mini"))

        # ------------------ HUGGINGFACE ------------------
        elif self.provider == "huggingface":
            self.hf_token = clean_env_var(os.getenv("HF_API_TOKEN", ""))
            self.model_name = clean_env_var(os.getenv("LLM_MODEL", "google/flan-t5-base"))
            self.api_url = f"https://router.huggingface.co/models/{self.model_name}"

        # ------------------ GROQ ------------------
        elif self.provider == "groq":
            import requests

            api_key = clean_env_var(os.getenv("GROQ_API_KEY", ""))
            if not api_key or not api_key.startswith("gsk_"):
                print("⚠️ Missing or invalid GROQ_API_KEY → will fallback.")
                self.client = None
            else:
                self.api_key = api_key
                self.model_name = clean_env_var(os.getenv("LLM_MODEL", "llama-3.1-8b-instant"))
                self.api_url = "https://api.groq.com/openai/v1/chat/completions"
                self.client = requests.Session()
                self.client.headers.update({
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                })

        else:
            raise ValueError(f"Invalid LLM_PROVIDER: {self.provider}")

    # --------------------------------------------------------
    #  INVOKE LLM
    # --------------------------------------------------------
    def invoke_llm(self, prompt: str, temperature: float = 0.7) -> str:

        system_prompt = (
            "You are a helpful assistant for the Physical AI textbook. "
            "Only use provided context. No external facts."
        )

        # ------------------ GEMINI ------------------
        if self.provider == "gemini":
            result = self.model.generate_content(
                f"{system_prompt}\n\n{prompt}",
                generation_config={"temperature": temperature, "max_output_tokens": 800}
            )
            return result.text

        # ------------------ OPENAI ------------------
        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=800
            )
            return response.choices[0].message.content

        # ------------------ HUGGINGFACE ------------------
        elif self.provider == "huggingface":
            import requests
            headers = {"Content-Type": "application/json"}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}" 
            payload = {
                "inputs": f"{system_prompt}\n\n{prompt}",
                "parameters": {"max_new_tokens": 300, "temperature": temperature}
            }

            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            result = response.json()

            if isinstance(result, list):
                return result[0].get("generated_text", "")
            return result.get("generated_text", "")

        # ------------------ GROQ ------------------
        elif self.provider == "groq":
            if self.client is None:
                raise ValueError("Groq not initialized")

            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": 800
            }

            r = self.client.post(self.api_url, json=payload, timeout=30.0)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

        raise RuntimeError("Invalid LLM provider or missing config")


class RAGPipeline:
    """
    RAG (Retrieval-Augmented Generation) Pipeline for Physical AI textbook.
    Handles query processing, vector search, and response generation.
    """
    
    def __init__(self, vector_db_client: VectorDBClient, llm_provider: LLMProvider):
        self.vector_db = vector_db_client
        self.llm = llm_provider
    
    def process_user_query(self, user_query: UserQuery, selected_text: Optional[str] = None) -> ChatbotResponse:
        """
        Process a user query using RAG pipeline:
        1. Generate embedding for the query
        2. Retrieve relevant chunks from vector DB
        3. Build context prompt
        4. Generate response using LLM
        """
        query_id = user_query.id or str(uuid.uuid4())
        query_text = user_query.text.strip()
        
        # Generate embedding for the query
        try:
            query_embedding = generate_embedding(query_text)
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {str(e)}")
        
        # Retrieve relevant chunks (top 5 by default)
        try:
            relevant_chunks = self.vector_db.retrieve_relevant_chunks(
                query_embedding=query_embedding,
                top_k=5,
                selected_text=selected_text
            )
        except Exception as e:
            raise ValueError(f"Failed to retrieve relevant chunks: {str(e)}")
        
        # Build context from retrieved chunks
        if not relevant_chunks:
            # No relevant chunks found
            response_text = (
                "I couldn't find relevant information in the textbook for your query. "
                "Please try rephrasing your question or check if the topic is covered in the Physical AI & Humanoid Robotics textbook."
            )
            cited_sources = []
        else:
            # Build context from chunks
            context_parts = []
            cited_sources = []
            
            for chunk in relevant_chunks:
                context_parts.append(f"Source: {chunk.source_metadata}\nContent: {chunk.text}\n")
                cited_sources.append({
                    "document_id": chunk.document_id,
                    "source_metadata": chunk.source_metadata,
                    "chunk_id": chunk.id
                })
            
            context = "\n".join(context_parts)
            
            # Build prompt with context
            prompt = f"""Based on the following context from the Physical AI & Humanoid Robotics textbook, answer the user's question.

Context:
{context}

User Question: {query_text}

Instructions:
- Answer the question using ONLY the information provided in the context above
- If the context doesn't contain enough information to answer the question, say so clearly
- Be concise and accurate
- Cite the source when referencing specific information

Answer:"""
            
            # Generate response using LLM
            try:
                response_text = self.llm.invoke_llm(prompt, temperature=0.7)
            except Exception as e:
                raise ValueError(f"Failed to generate LLM response: {str(e)}")
        
        # Create response object
        response = ChatbotResponse(
            id=str(uuid.uuid4()),
            query_id=query_id,
            text=response_text,
            timestamp=datetime.utcnow(),
            constitutional_compliance_status="COMPLIANT",  # Can be enhanced with actual compliance checking
            cited_sources=cited_sources
        )
        
        return response


