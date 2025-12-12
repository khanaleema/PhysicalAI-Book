from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
import json
import os
from src.core.database import Database

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", secrets.token_urlsafe(32))

class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    background: dict

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    background: Optional[dict] = None

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@router.post("/sign-up")
async def sign_up(request: SignUpRequest):
    db = Database()
    
    # Get database connection - returns None if fails (graceful degradation)
    conn = db._get_connection()
    if not conn:
        raise HTTPException(
            status_code=503, 
            detail="Database service is currently unavailable. This might be due to network connectivity issues. Please try again later or contact support."
        )
    
    try:
        with conn.cursor() as cur:
            # Normalize email
            email = request.email.lower().strip()
            
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Create user
            user_id = secrets.token_urlsafe(16)
            hashed_password = hash_password(request.password)
            
            cur.execute("""
                INSERT INTO users (id, name, email, password, background, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                request.name,
                email,
                hashed_password,
                json.dumps(request.background),
                datetime.utcnow()
            ))
            
            conn.commit()
            
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Sign-up error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create account: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.post("/sign-in")
async def sign_in(request: SignInRequest):
    db = Database()
    
    conn = db._get_connection()
    if not conn:
        raise HTTPException(
            status_code=503, 
            detail="Database service is currently unavailable. This might be due to network connectivity issues. Please try again later or contact support."
        )
    
    try:
        with conn.cursor() as cur:
            # Normalize email
            email = request.email.lower().strip()
            
            cur.execute("""
                SELECT id, name, email, password, background 
                FROM users WHERE email = %s
            """, (email,))
            user = cur.fetchone()
            
            if not user or not verify_password(request.password, user[3]):
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            token = create_token(user[0])
            background = json.loads(user[4]) if user[4] else {}
            
            return {
                "user": {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "background": background
                },
                "token": token
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Sign-in error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sign in: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]
        
        db = Database()
        conn = db._get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, email, background 
                    FROM users WHERE id = %s
                """, (user_id,))
                user = cur.fetchone()
                
                if not user:
                    raise HTTPException(status_code=401, detail="User not found")
                
                background = json.loads(user[3]) if user[3] else {}
                
                return {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "background": background
                }
        finally:
            conn.close()
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    background: Optional[dict] = None

@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]
        
        db = Database()
        conn = db._get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed. Please try again later.")
        
        try:
            with conn.cursor() as cur:
                # Build update query dynamically
                updates = []
                values = []
                
                if request.name is not None:
                    updates.append("name = %s")
                    values.append(request.name)
                
                if request.background is not None:
                    updates.append("background = %s")
                    values.append(json.dumps(request.background))
                
                if not updates:
                    raise HTTPException(status_code=400, detail="No fields to update")
                
                updates.append("updated_at = %s")
                values.append(datetime.utcnow())
                values.append(user_id)
                
                query = f"""
                    UPDATE users 
                    SET {', '.join(updates)}
                    WHERE id = %s
                """
                
                cur.execute(query, values)
                conn.commit()
                
                # Fetch updated user
                cur.execute("""
                    SELECT id, name, email, background 
                    FROM users WHERE id = %s
                """, (user_id,))
                user = cur.fetchone()
                
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                
                background = json.loads(user[3]) if user[3] else {}
                
                return {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "background": background
                }
        finally:
            conn.close()
    except HTTPException:
        raise
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        print(f"❌ Update profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

