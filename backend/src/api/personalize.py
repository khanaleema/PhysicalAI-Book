"""
Personalize router - placeholder module.
This module is kept for backward compatibility.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/personalize", tags=["personalize"])

@router.get("/")
async def personalize_placeholder():
    """Placeholder endpoint for personalize functionality."""
    return {"message": "Personalize endpoint - not yet implemented"}

