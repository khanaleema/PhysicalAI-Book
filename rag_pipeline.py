import os
# Remove proxies before any imports
for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"]:
    os.environ.pop(key, None)

from typing import Optional
from src.data.ingestion import clean_env_var

class LLMProvider:
    """
    LLM provider integration for Physical AI textbook.
    Supports: openai, groq, huggingface, gemini
    """

    def __init__(self):
        self.provider = clean_env_var(os.getenv("LLM_PROVIDER", "openai")).lower()

        # ------------------ GEMINI ------------------
        if self.provider == "gemini":
            import google.generativeai as genai
            api_key = clean_env_var(os.getenv("GEMINI_API_KEY", ""))
            if not api_key:
                raise ValueError("Missing GEMINI_API_KEY")

            genai.configure(api_key=api_key)
            self.model_name = clean_env_var(os.getenv("LLM_MODEL", "gemini-1.5-flash"))
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
