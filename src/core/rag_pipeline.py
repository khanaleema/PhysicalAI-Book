import os
from typing import List, Optional
from src.models.schemas import UserQuery, ChatbotResponse, TextChunk
from src.data.ingestion import generate_embedding, VectorDBClient
from dotenv import load_dotenv

load_dotenv()

class LLMProvider:
    """LLM provider integration - supports OpenAI, Google Gemini, Hugging Face, and Groq (FREE & FAST)."""
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "groq").lower()  # "openai", "gemini", "huggingface", or "groq"
        
        if self.provider == "gemini":
            try:
                import google.generativeai as genai
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY must be set in environment variables")
                
                # Debug: Show API key info (first 10 and last 4 chars only for security)
                api_key_preview = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
                print(f"🔑 Using API key: {api_key_preview}")
                
                # Verify API key format
                if not api_key.startswith("AIzaSy"):
                    print(f"⚠️ WARNING: API key format may be incorrect (expected: AIzaSy...)")
                    print(f"   Current format: {api_key[:10]}...")
                
                genai.configure(api_key=api_key)
                print(f"✅ Gemini API configured")
                
                # SIMPLE APPROACH: Just try the most common working models one by one
                # Test each model with actual API call before accepting
                # Updated to use current valid Gemini model names
                working_models = [
                    "gemini-1.5-flash-latest",  # Latest version of 1.5-flash
                    "gemini-1.5-flash",        # Fallback to specific version
                    "gemini-1.5-pro-latest",   # Latest version of 1.5-pro
                    "gemini-1.5-pro"           # Fallback to specific version
                ]
                
                # Add env model to front if specified
                env_model = os.getenv("LLM_MODEL", "").strip()
                if env_model:
                    if env_model.endswith("-latest"):
                        env_model = env_model[:-7]
                    if env_model not in working_models:
                        working_models.insert(0, env_model)
                
                print(f"🔍 Testing Gemini API with {len(working_models)} models...")
                model_found = False
                
                for model_name in working_models:
                    try:
                        # Create model
                        test_model = genai.GenerativeModel(model_name)
                        # ACTUALLY TEST IT with a real API call
                        test_result = test_model.generate_content(
                            "Hi", 
                            generation_config={"max_output_tokens": 5}
                        )
                        # If we get here, model works!
                        self.model = test_model
                        self.model_name = model_name
                        print(f"✅ SUCCESS! Using Gemini model: {self.model_name}")
                        model_found = True
                        break
                    except Exception as e:
                        error_msg = str(e)
                        # Show all errors for debugging
                        print(f"   ❌ {model_name} failed: {error_msg[:100]}")
                        continue
                
                if not model_found:
                    api_key_debug = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
                    print(f"\n❌ ERROR: All Gemini models failed!")
                    print(f"   API Key used: {api_key_debug}")
                    print(f"   This usually means:")
                    print(f"   1. API key is invalid/expired/revoked")
                    print(f"   2. API key doesn't have access to Gemini models")
                    print(f"   3. API key format is wrong")
                    print(f"   4. Network/firewall blocking API calls")
                    print(f"   \n   SOLUTION:")
                    print(f"   1. Go to: https://aistudio.google.com/app/apikey")
                    print(f"   2. Create a NEW API key")
                    print(f"   3. Copy the FULL key (starts with AIzaSy...)")
                    print(f"   4. Update backend/.env file: GEMINI_API_KEY=your-new-key")
                    print(f"   5. Restart backend server")
                    print(f"\n   Backend will start but LLM responses will fail")
                    self.model = None
                    self.model_name = None
            except ImportError:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY must be set in environment variables")
                self.client = OpenAI(api_key=api_key)
                self.model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")
                print(f"LLMProvider initialized with OpenAI model: {self.model_name}")
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        elif self.provider == "huggingface":
            # Hugging Face Inference API - FREE!
            try:
                import requests
                self.hf_token = os.getenv("HF_API_TOKEN", "")  # Optional, but recommended for rate limits
                # Use a good free model for text generation
                self.model_name = os.getenv("LLM_MODEL", "google/flan-t5-base")
                # Use new router endpoint
                self.api_url = f"https://router.huggingface.co/models/{self.model_name}"
                print(f"LLMProvider initialized with Hugging Face model: {self.model_name}")
                print("Using FREE Hugging Face Inference API (no API key required!)")
            except ImportError:
                raise ImportError("requests package not installed. Run: pip install requests")
        elif self.provider == "groq":
            # Groq API - FREE & FAST!
            try:
                from groq import Groq
                api_key = os.getenv("GROQ_API_KEY", "")
                if not api_key:
                    print("⚠️ WARNING: GROQ_API_KEY not set. Get free API key from: https://console.groq.com/keys")
                    print("   Backend will use fallback mode")
                    self.client = None
                    self.model_name = None
                else:
                    self.client = Groq(api_key=api_key)
                    self.model_name = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")  # Fast free model
                    print(f"LLMProvider initialized with Groq model: {self.model_name}")
                    print("Using FREE & FAST Groq API!")
            except ImportError:
                print("⚠️ groq package not installed. Run: pip install groq")
                print("   Backend will use fallback mode")
                self.client = None
                self.model_name = None

    def invoke_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """Invokes the LLM with a given prompt."""
        system_prompt = "You are a helpful assistant for the Physical AI & Humanoid Robotics textbook. Answer questions based only on the provided context."
        
        try:
            if self.provider == "gemini":
                if self.model is None:
                    error_msg = (
                        "Gemini LLM is not available. "
                        "Please check your GEMINI_API_KEY at https://aistudio.google.com/app/apikey. "
                        "The API key should start with 'AIzaSy...' and have access to Gemini models."
                    )
                    raise ValueError(error_msg)
                
                full_prompt = f"{system_prompt}\n\n{prompt}"
                response = self.model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": 1000,
                    }
                )
                return response.text
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            elif self.provider == "huggingface":
                # Hugging Face Inference API - FREE!
                import requests
                headers = {"Content-Type": "application/json"}
                if self.hf_token:
                    headers["Authorization"] = f"Bearer {self.hf_token}"
                
                # Combine system prompt and user prompt
                full_prompt = f"{system_prompt}\n\n{prompt}"
                
                # For text generation models
                payload = {
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": 300,
                        "temperature": temperature,
                        "return_full_text": False,
                        "do_sample": True
                    }
                }
                
                try:
                    response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        # Handle different response formats
                        if isinstance(result, list) and len(result) > 0:
                            generated = result[0].get("generated_text", "")
                            # Remove the original prompt from generated text
                            if full_prompt in generated:
                                generated = generated.replace(full_prompt, "").strip()
                            return generated if generated else "I found relevant information but couldn't generate a response. Please check the retrieved content."
                        elif isinstance(result, dict):
                            generated = result.get("generated_text", "")
                            if full_prompt in generated:
                                generated = generated.replace(full_prompt, "").strip()
                            return generated if generated else str(result)
                        else:
                            return str(result)
                    elif response.status_code == 503:
                        # Model is loading, return a simple response
                        return "The AI model is currently loading. Please try again in a few seconds."
                    elif response.status_code == 410:
                        # Old endpoint deprecated, try alternative approach
                        raise Exception("Hugging Face API endpoint changed. Using fallback mode.")
                    else:
                        error_msg = response.text[:200] if response.text else "Unknown error"
                        raise Exception(f"Hugging Face API error ({response.status_code}): {error_msg}")
                except requests.exceptions.Timeout:
                    raise Exception("Request timed out. The model might be busy.")
                except Exception as e:
                    # If Hugging Face fails, raise to trigger fallback
                    raise Exception(f"Hugging Face API error: {str(e)}")
            elif self.provider == "groq":
                if self.client is None:
                    raise ValueError("Groq API not initialized. Please set GROQ_API_KEY in .env file. Get free key from: https://console.groq.com/keys")
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=1000
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"Error invoking LLM: {e}")
            raise

class RAGPipeline:
    """Orchestrates the RAG process."""
    def __init__(self, vector_db_client: VectorDBClient, llm_provider: LLMProvider):
        self.vector_db_client = vector_db_client
        self.llm_provider = llm_provider

    # Task 3.1: Implement Query Embedding Generation
    def generate_query_embedding(self, query_text: str) -> List[float]:
        return generate_embedding(query_text)

    # Task 3.2: Implement Contextual Retrieval
    def retrieve_context(self, query_embedding: List[float], top_k: int = 5, selected_text: Optional[str] = None) -> List[TextChunk]:
        return self.vector_db_client.retrieve_relevant_chunks(query_embedding, top_k, selected_text)

    # Task 3.3: Implement LLM Prompt Construction
    def construct_llm_prompt(self, user_query: UserQuery, retrieved_chunks: List[TextChunk]) -> str:
        constitution_rules = """
        Constitution Rule: The chatbot is allowed to use ONLY the Textbook and this Constitution.
        Constitution Rule: If information is not in the textbook, reply: "This topic is not in the textbook, so I cannot answer it."
        Constitution Rule: No guessing or external internet facts.
        """
        
        # Check if first chunk is user selected text
        has_selected_text = retrieved_chunks and retrieved_chunks[0].source_metadata == "User Selected Text"
        
        if has_selected_text:
            # Prioritize selected text - put it first and make it clear
            selected_text = retrieved_chunks[0].text
            other_chunks = retrieved_chunks[1:] if len(retrieved_chunks) > 1 else []
            
            context_text = f"""**USER SELECTED TEXT (HIGHEST PRIORITY - USE THIS FIRST):**
{selected_text}

**Additional Textbook Context:**
{chr(10).join([f"[From: {chunk.source_metadata}]{chr(10)}{chunk.text}" for chunk in other_chunks]) if other_chunks else "None"}
"""
        else:
            context_text = "\n\n".join([f"[From: {chunk.source_metadata}]\n{chunk.text}" for chunk in retrieved_chunks])
        
        prompt = f"""You are "The Physical AI & Humanoid Robotics Course Assistant."

Rules:
{constitution_rules}

IMPORTANT: 
- If the user has selected text (marked as "USER SELECTED TEXT"), you MUST prioritize and use that text to answer the question.
- If you found relevant information in the context below, you MUST answer the question using that information.
- Only say "not in textbook" if the context is completely unrelated to the question.

Relevant textbook content:
---
{context_text}
---

Question: {user_query.text}

Instructions:
1. **If user selected text is present, use it as the primary source for your answer**
2. If the context contains relevant information, provide a clear, helpful answer based on it
3. Use the information from the context to answer the question
4. If the context is completely unrelated or empty, then say the topic is not in the textbook
5. Be helpful and informative when you have relevant content

Answer:"""
        return prompt

    # Task 3.5: Implement Initial LLM Response Generation (Task 3.4 is integration, handled by llm_provider)
    def generate_llm_response(self, prompt: str) -> str:
        return self.llm_provider.invoke_llm(prompt)

    # Task 3.6: Develop Constitutional Compliance Post-Processing
    def constitutional_compliance_check(self, llm_response: str) -> str:
        # Conceptual check for compliance
        if "I cannot answer it" in llm_response:
            return "COMPLIANT"
        if "external" in llm_response.lower() or "guess" in llm_response.lower():
             return "FLAGGED" # Or NON_COMPLIANT based on strictness
        return "COMPLIANT"

    # Task 3.7: Implement Source Citation Extraction
    def extract_citations(self, response_text: str, retrieved_chunks: List[TextChunk]) -> List[dict]:
        citations = []
        # Extract citations from retrieved chunks
        for chunk in retrieved_chunks[:3]:  # Top 3 chunks
            citations.append({
                "document_id": chunk.document_id,
                "source_metadata": chunk.source_metadata
            })
        return citations

    # Task 3.8: Implement "Not in Textbook" Handling
    def handle_out_of_scope(self, llm_response: str, user_query_text: str) -> str:
        if "cannot answer" in llm_response.lower() and "textbook" in llm_response.lower():
            return "COMPLIANT"
        # More sophisticated logic would go here to detect if LLM truly couldn't find answer
        return "COMPLIANT" # Default if not explicitly out of scope

    def process_user_query(self, user_query: UserQuery, selected_text: Optional[str] = None) -> ChatbotResponse:
        query_embedding = self.generate_query_embedding(user_query.text)
        retrieved_chunks = self.retrieve_context(query_embedding, selected_text=selected_text)
        
        # If selected text is provided, prioritize it in the context
        if selected_text and retrieved_chunks:
            # Add selected text as the first chunk
            selected_chunk = TextChunk(
                document_id="selected_text",
                text=selected_text,
                source_metadata="User Selected Text",
                order_in_document=0
            )
            retrieved_chunks = [selected_chunk] + retrieved_chunks[:4]  # Keep top 4 from DB + selected text
        
        # Try to use LLM, but fallback to smart response if LLM not available
        try:
            llm_prompt = self.construct_llm_prompt(user_query, retrieved_chunks)
            llm_raw_response = self.llm_provider.invoke_llm(llm_prompt)
            final_response_text = llm_raw_response
            compliance_status = self.constitutional_compliance_check(llm_raw_response)
        except Exception as e:
            # LLM not available - provide smart fallback response from retrieved chunks
            print(f"⚠️ Using fallback response (LLM unavailable): {str(e)[:100]}")
            
            if retrieved_chunks:
                # Smart fallback: Create a well-formatted response from retrieved chunks
                import re
                
                # Prioritize selected text if available
                best_chunk = retrieved_chunks[0]
                if best_chunk.source_metadata == "User Selected Text":
                    # Use selected text as primary response
                    chunk_text = best_chunk.text.strip()
                    response_prefix = "Based on the text you selected from the Physical AI & Humanoid Robotics textbook"
                else:
                    # Use best retrieved chunk
                    chunk_text = best_chunk.text.strip()
                    response_prefix = "According to the Physical AI & Humanoid Robotics textbook"
                
                # Remove markdown artifacts
                # Remove sidebar_position
                chunk_text = re.sub(r'^---\s*$', '', chunk_text, flags=re.MULTILINE)
                chunk_text = re.sub(r'sidebar_position:\s*\d+', '', chunk_text)
                
                # Remove excessive markdown headers (keep content)
                lines = chunk_text.split('\n')
                cleaned_lines = []
                skip_next = False
                for i, line in enumerate(lines):
                    # Skip standalone --- lines
                    if line.strip() == '---' and (i == 0 or i == len(lines) - 1 or lines[i-1].strip() == ''):
                        continue
                    # Skip markdown headers at start
                    if line.strip().startswith('#') and i < 3:
                        continue
                    # Skip empty lines at start
                    if not cleaned_lines and not line.strip():
                        continue
                    cleaned_lines.append(line)
                
                chunk_text = '\n'.join(cleaned_lines).strip()
                
                # Remove code blocks if they're incomplete
                if chunk_text.count('```') % 2 != 0:
                    # Unmatched code block, remove it
                    chunk_text = re.sub(r'```[^`]*$', '', chunk_text, flags=re.MULTILINE)
                
                # Truncate to reasonable length (500 chars for main response)
                if len(chunk_text) > 500:
                    # Try to cut at sentence boundary
                    truncated = chunk_text[:500]
                    last_period = truncated.rfind('.')
                    last_newline = truncated.rfind('\n')
                    cut_point = max(last_period, last_newline)
                    if cut_point > 300:
                        chunk_text = chunk_text[:cut_point + 1]
                    else:
                        chunk_text = chunk_text[:500] + "..."
                
                # Create a natural, conversational response
                final_response_text = f"{response_prefix}:\n\n{chunk_text}"
                
                # Add additional context if available
                if len(retrieved_chunks) > 1:
                    additional_info = "\n\n[Additional information is available in the textbook. Check the citations for more details.]"
                    final_response_text += additional_info
            else:
                final_response_text = "I couldn't find relevant information in the textbook for your query. Please try rephrasing your question or check if the topic is covered in the Physical AI & Humanoid Robotics textbook."
            
            compliance_status = "COMPLIANT"
        
        citations = self.extract_citations(final_response_text, retrieved_chunks)
        
        return ChatbotResponse(
            query_id=user_query.id,
            text=final_response_text,
            constitutional_compliance_status=compliance_status,
            cited_sources=citations
        )
