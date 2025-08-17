from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os

# Simple models for testing
class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool

# Create app
app = FastAPI(
    title="LeadNest API", 
    version="1.0.5-WORKING",
    description="LeadNest Production API - All Endpoints Active"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "LeadNest API is running!", 
        "version": "1.0.5-WORKING", 
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "deployment": "SUCCESS",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "leadnest-api", 
        "version": "1.0.5-WORKING",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug-info")
async def debug_info():
    return {
        "service": "leadnest-backend",
        "version": "1.0.5-WORKING",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "port": os.getenv("PORT", "not_set"),
        "endpoints_available": True
    }

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user - TEST VERSION"""
    # Simple validation
    if "@" not in user.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Return mock user for testing
    return UserResponse(
        id=1,
        email=user.email,
        is_active=True
    )

@app.post("/auth/login")
async def login(user: UserCreate):
    """Login user - TEST VERSION"""
    return {
        "access_token": "test_token_123",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": user.email,
            "is_active": True
        }
    }

@app.get("/auth/me")
async def get_current_user():
    """Get current user - TEST VERSION"""
    return {
        "id": 1,
        "email": "test@example.com",
        "is_active": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
