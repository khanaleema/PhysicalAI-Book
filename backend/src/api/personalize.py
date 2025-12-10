from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import os

router = APIRouter(prefix="/personalize", tags=["personalize"])

class PersonalizeRequest(BaseModel):
    content: str
    userBackground: Dict
    chapterPath: str
    personalizationLevel: Optional[str] = "moderate"

@router.post("")
def personalize_content(request: PersonalizeRequest):
    """Personalize content based on user background."""
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Use Gemini API
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Build personalization prompt based on user background
        background = request.userBackground
        experience_level = background.get('softwareExperience', 'beginner')
        hardware_exp = background.get('hardwareExperience', 'none')
        languages = ', '.join(background.get('programmingLanguages', []))
        robotics_exp = background.get('roboticsExperience', 'none')
        education = background.get('educationLevel', 'bachelor')
        
        # Determine personalization intensity based on level
        level = request.personalizationLevel or "moderate"
        if level == "light":
            intensity_instruction = "Make minor adjustments: add brief context, use simpler terms where appropriate, but keep the structure mostly unchanged."
        elif level == "deep":
            intensity_instruction = "Comprehensively rewrite: deeply adapt the content structure, add extensive examples from their background, use terminology matching their exact level, and reorganize sections for better understanding."
        else:  # moderate
            intensity_instruction = "Make balanced adaptations: adjust technical depth, add relevant examples from their programming languages, provide context for their robotics experience, and use appropriate terminology while maintaining the original structure."
        
        prompt = f"""You are a personalized learning assistant. Adapt the following textbook content to match the user's background.

User Background:
- Software Experience: {experience_level}
- Hardware Experience: {hardware_exp}
- Programming Languages: {languages}
- Robotics Experience: {robotics_exp}
- Education Level: {education}

Personalization Level: {level}

Original Content:
{request.content}

Please personalize this content by:
1. {intensity_instruction}
2. Adjusting technical depth based on experience level ({experience_level})
3. Adding relevant examples from their known programming languages ({languages})
4. Providing context appropriate to their robotics experience ({robotics_exp})
5. Using terminology matching their education level ({education})
6. Keeping all the original information but making it more accessible

Return the personalized content in the same markdown format. Preserve all headings, code blocks, lists, and formatting."""

        # Use Gemini API
        full_prompt = f"You are an expert educational content personalizer.\n\n{prompt}"
        result = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 4000
            }
        )
        personalized_content = result.text
        
        return {
            "personalizedContent": personalized_content,
            "chapterPath": request.chapterPath
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_detail = str(e)
        if 'GEMINI_API_KEY' in error_detail:
            error_detail = "GEMINI_API_KEY not configured. Please set it in environment variables."
        raise HTTPException(status_code=500, detail=f"Personalization failed: {error_detail}")

