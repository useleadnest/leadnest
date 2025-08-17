from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app first
app = FastAPI(title="LeadNest API", version="1.0.0", description="Production Ready")

# Add CORS middleware immediately
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://useleadnest.com",
        "https://www.useleadnest.com", 
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health endpoints that always work
@app.get("/")
async def root():
    return {
        "message": "LeadNest API is running!",
        "version": "1.0.0-BULLETPROOF",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

# Try to import database and auth components
try:
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
    from scraper import LeadScraper
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    security = HTTPBearer()
    scraper = LeadScraper()
    
    logger.info("✅ All imports successful - Full functionality available")
    
    # Auth endpoints
    @app.post("/auth/register", response_model=UserSchema)
    async def register(user: UserCreate, db: Session = Depends(get_db)):
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
        return current_user

    # Search endpoints
    @app.post("/searches", response_model=SearchSchema)
    async def create_search(
        search: SearchCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        # Check if user is in trial and trial expired
        if current_user.subscription_status == "trial" and current_user.trial_ends_at < datetime.utcnow():
            raise HTTPException(
                status_code=402,
                detail="Trial expired. Please upgrade to continue."
            )
        
        # Create search record
        db_search = Search(
            user_id=current_user.id,
            location=search.location,
            business_type=search.business_type,
            search_radius=search.search_radius,
            max_results=search.max_results
        )
        db.add(db_search)
        db.commit()
        db.refresh(db_search)
        
        # Perform the actual search
        try:
            leads = scraper.search_leads(
                location=search.location,
                business_type=search.business_type,
                radius=search.search_radius,
                max_results=search.max_results
            )
            
            # Save leads to database
            for lead_data in leads:
                db_lead = Lead(
                    search_id=db_search.id,
                    business_name=lead_data.get('name'),
                    phone=lead_data.get('phone'),
                    email=lead_data.get('email'),
                    address=lead_data.get('address'),
                    website=lead_data.get('website'),
                    rating=lead_data.get('rating'),
                    review_count=lead_data.get('review_count')
                )
                db.add(db_lead)
            
            db.commit()
            
            # Update search results count
            db_search.results_count = len(leads)
            db.commit()
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            db_search.status = "failed"
            db.commit()
            raise HTTPException(status_code=500, detail="Search failed")
        
        return db_search

    @app.get("/searches", response_model=List[SearchSchema])
    async def get_searches(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        return db.query(Search).filter(Search.user_id == current_user.id).all()

    @app.get("/leads/{search_id}", response_model=List[LeadSchema])
    async def get_leads(
        search_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        # Verify user owns this search
        search = db.query(Search).filter(
            Search.id == search_id,
            Search.user_id == current_user.id
        ).first()
        
        if not search:
            raise HTTPException(status_code=404, detail="Search not found")
        
        return db.query(Lead).filter(Lead.search_id == search_id).all()

    @app.get("/dashboard/stats", response_model=DashboardStats)
    async def get_dashboard_stats(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        total_searches = db.query(Search).filter(Search.user_id == current_user.id).count()
        total_leads = db.query(Lead).join(Search).filter(Search.user_id == current_user.id).count()
        
        return DashboardStats(
            total_searches=total_searches,
            total_leads=total_leads,
            subscription_status=current_user.subscription_status
        )

except ImportError as e:
    logger.error(f"❌ Import failed: {e}")
    
    # Fallback endpoints when imports fail
    @app.get("/auth/register")
    async def register_fallback():
        return {"error": "Service temporarily unavailable - imports failed", "status": "fallback"}
    
    @app.get("/auth/login") 
    async def login_fallback():
        return {"error": "Service temporarily unavailable - imports failed", "status": "fallback"}
    
    @app.get("/auth/me")
    async def me_fallback():
        return {"error": "Service temporarily unavailable - imports failed", "status": "fallback"}

@app.get("/debug")
async def debug_info():
    return {
        "service": "leadnest-api",
        "version": "1.0.0-BULLETPROOF", 
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "python_path": os.getenv("PYTHONPATH", "not set")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
