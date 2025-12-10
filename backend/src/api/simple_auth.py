"""
Simple Authentication - No Database Dependency
Works with in-memory storage for quick testing
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory storage (for testing - replace with database later)
users_db: Dict[str, dict] = {}
reset_tokens_db: Dict[str, dict] = {}  # Store reset tokens
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", secrets.token_urlsafe(32))

class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    background: dict

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, AUTH_SECRET_KEY, algorithm="HS256")

@router.post("/sign-up")
async def sign_up(request: SignUpRequest):
    """Simple sign up - stores in memory"""
    # Normalize email (lowercase)
    email = request.email.lower().strip()
    
    if email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = secrets.token_urlsafe(16)
    hashed_password = hash_password(request.password)
    
    users_db[email] = {
        "id": user_id,
        "name": request.name,
        "email": email,
        "password": hashed_password,
        "background": request.background
    }
    
    token = create_token(user_id)
    
    return {
        "user": {
            "id": user_id,
            "name": request.name,
            "email": email,
            "background": request.background
        },
        "token": token
    }

@router.post("/sign-in")
async def sign_in(request: SignInRequest):
    """Simple sign in - checks in-memory storage"""
    # Normalize email (lowercase)
    email = request.email.lower().strip()
    
    if email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = users_db[email]
    hashed_password = hash_password(request.password)
    
    if user["password"] != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user["id"])
    
    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "background": user["background"]
        },
        "token": token
    }

@router.post("/forgot-password")
async def forgot_password(request: dict):
    """Request password reset - generates reset token"""
    email = request.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Normalize email (lowercase)
    email = email.lower().strip()
    
    if email not in users_db:
        # For demo: show helpful message
        return {
            "message": "Email not found. Please make sure you have signed up first.",
            "resetToken": None,
            "error": "Email not registered"
        }
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    
    # Store reset token with expiration (24 hours)
    reset_tokens_db[email] = {
        "token": reset_token,
        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }
    
    # In production, send email with reset link
    # For demo, return token (remove in production)
    return {
        "message": "Password reset link sent! Check your email.",
        "resetToken": reset_token,  # For demo only - remove in production
        "email": email
    }

@router.post("/reset-password")
async def reset_password(request: dict):
    """Reset password using reset token"""
    email = request.get("email")
    reset_token = request.get("resetToken")
    new_password = request.get("newPassword")
    
    if not all([email, reset_token, new_password]):
        raise HTTPException(status_code=400, detail="Email, reset token, and new password are required")
    
    # Normalize email
    email = email.lower().strip()
    
    if email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check reset token
    if email not in reset_tokens_db:
        raise HTTPException(status_code=400, detail="No reset request found for this email. Please request a new reset token.")
    
    token_data = reset_tokens_db[email]
    
    # Check if token matches
    if token_data["token"] != reset_token:
        raise HTTPException(status_code=400, detail="Invalid reset token. Please check and try again.")
    
    # Check if token expired
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.utcnow() > expires_at:
        del reset_tokens_db[email]
        raise HTTPException(status_code=400, detail="Reset token has expired. Please request a new one.")
    
    # Validate password length
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    # Update password
    hashed_password = hash_password(new_password)
    users_db[email]["password"] = hashed_password
    
    # Remove used token
    del reset_tokens_db[email]
    
    return {
        "message": "Password reset successfully"
    }

@router.get("/test")
async def test_auth():
    """Test endpoint to verify auth router is working"""
    return {
        "status": "ok",
        "message": "Auth router is working!",
        "users_count": len(users_db)
    }

