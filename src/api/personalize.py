from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import os
from groq import Groq

router = APIRouter(prefix="/personalize", tags=["personalize"])

class PersonalizeRequest(BaseModel):
    content: str
    userBackground: Dict
    chapterPath: str
    personalizationLevel: Optional[str] = "moderate"

@router.post("")
async def personalize_content(request: PersonalizeRequest):
    """Personalize content based on user background."""
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
        
        client = Groq(api_key=groq_api_key)
        
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

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert educational content personalizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        personalized_content = response.choices[0].message.content
        
        return {
            "personalizedContent": personalized_content,
            "chapterPath": request.chapterPath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Personalization failed: {str(e)}")

