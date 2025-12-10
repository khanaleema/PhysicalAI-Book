from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter(prefix="/translate", tags=["translate"])

class TranslateRequest(BaseModel):
    content: str
    chapterPath: str
    targetLanguage: str = "urdu"

@router.post("")
def translate_content(request: TranslateRequest):
    """Translate content to Urdu while preserving markdown formatting."""
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Use Gemini API
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""You are an expert translator specializing in translating technical and educational content from English to Urdu (اردو).

Translate the following markdown content from English to Urdu. CRITICAL REQUIREMENTS:

1. Preserve ALL markdown formatting EXACTLY:
   - Headings: Keep # ## ### exactly as they are
   - Code blocks: Keep ```language``` format exactly, preserve code inside
   - Inline code: Keep `code` format exactly
   - Lists: Keep - * 1. 2. format exactly, maintain indentation
   - Links: Keep [text](url) format exactly
   - Bold: Keep **text** format exactly
   - Italic: Keep *text* format exactly
   - Blockquotes: Keep > format exactly
   - Tables: Keep | column | format exactly, preserve table structure
   - Horizontal rules: Keep --- exactly
   - Line breaks: Preserve double line breaks for paragraphs

2. Translate ONLY the text content, NOT:
   - Markdown syntax symbols (# * - ` > | etc.)
   - Code in code blocks (keep code as-is)
   - URLs in links (keep URLs as-is)
   - Technical terms commonly used in English (API, JSON, HTTP, etc.)
   - Variable names, function names, class names in code
   - File paths, commands, or technical identifiers

3. Table formatting: Ensure tables have proper spacing:
   - Use: | Header 1 | Header 2 |
   - Separator: |----------|----------|
   - Rows: | Cell 1   | Cell 2   |
   - Maintain alignment and spacing

4. Code blocks: Keep code language identifiers and all code content unchanged.

5. Use proper Urdu script and maintain readability.

6. Keep technical accuracy - translate concepts clearly.

Original Content:
{request.content}

Return ONLY the translated markdown content with all formatting preserved exactly."""

        # Use Gemini API
        full_prompt = f"You are an expert translator for English to Urdu (اردو) translation, specializing in technical and educational content. Always preserve markdown formatting exactly.\n\n{prompt}"
        result = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 4000
            }
        )
        translated_content = result.text
        
        return {
            "translatedContent": translated_content,
            "chapterPath": request.chapterPath,
            "targetLanguage": request.targetLanguage
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_detail = str(e)
        if 'GEMINI_API_KEY' in error_detail:
            error_detail = "GEMINI_API_KEY not configured. Please set it in environment variables."
        raise HTTPException(status_code=500, detail=f"Translation failed: {error_detail}")
