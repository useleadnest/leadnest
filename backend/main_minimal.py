from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import logging

from config import config
from database import get_db, User, Search, Lead, Export, engine, Base
from schemas import (
    UserCreate, UserLogin, User as UserSchema, Token,
    SearchCreate, Search as SearchSchema, Lead as LeadSchema,
    ExportCreate, Export as ExportSchema, DashboardStats
)
from auth import (
    authenticate_user, create_access_token, get_current_active_user,
    create_user, get_user_by_email, get_admin_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LeadNest API", 
    version="1.0.2",
    description="LeadNest Backend API - Full Production Version"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        config.frontend_url, 
        "https://useleadnest.com", 
        "https://leadnest-frontend-ocr18jamx-christians-projects-d64cce8f.vercel.app",
        "http://localhost:3000", 
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Basic endpoints
@app.get("/")
async def root():
    return {
        "message": "LeadNest API is running!", 
        "version": "1.0.2", 
        "status": "active",
        "endpoints": "See /docs for full API documentation"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "leadnest-api", 
        "version": "1.0.2",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-deploy")
async def test_deploy():
    return {
        "message": "Deployment test successful", 
        "timestamp": datetime.now().isoformat(),
        "commit": "Full API deployment"
    }

# Auth endpoints
@app.post("/auth/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user
    db_user = create_user(db, email=user.email, password=user.password)
    return db_user

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
