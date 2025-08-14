from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import csv
import io
from fastapi.responses import StreamingResponse
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
from scraper import LeadScraper
from admin_dashboard import router as admin_router

logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LeadNest API", version="1.0.0")

# Include routers
app.include_router(admin_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.frontend_url, "https://useleadnest.com", "http://localhost:3000", "http://localhost:5173"],  # Production + dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
scraper = LeadScraper()

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

# Search and Lead endpoints
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
        trade=search.trade
    )
    db.add(db_search)
    db.commit()
    db.refresh(db_search)
    
    # Scrape leads
    try:
        # Try Yelp API first, fallback to mock data
        leads_data = scraper.scrape_yelp_businesses(search.location, search.trade, limit=100)
        if not leads_data:
            leads_data = scraper.scrape_mock_data(search.location, search.trade, limit=50)
        
        # Enrich with AI and save to database
        db_leads = []
        for lead_data in leads_data:
            # Enrich with AI
            enriched_data = scraper.enrich_with_ai(lead_data)
            
            # Create lead record
            db_lead = Lead(
                search_id=db_search.id,
                business_name=enriched_data['business_name'],
                phone=enriched_data.get('phone'),
                email=enriched_data.get('email'),
                website=enriched_data.get('website'),
                address=enriched_data.get('address'),
                category=enriched_data.get('category'),
                rating=enriched_data.get('rating'),
                review_count=enriched_data.get('review_count'),
                ai_email_message=enriched_data.get('ai_email_message'),
                ai_sms_message=enriched_data.get('ai_sms_message'),
                quality_score=enriched_data.get('quality_score')
            )
            db.add(db_lead)
            db_leads.append(db_lead)
        
        # Update search results count
        db_search.results_count = len(db_leads)
        db.commit()
        
        # Return search with leads
        db.refresh(db_search)
        return db_search
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error scraping leads: {str(e)}"
        )

@app.get("/searches", response_model=List[SearchSchema])
async def get_searches(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    searches = db.query(Search).filter(Search.user_id == current_user.id).all()
    return searches

@app.get("/searches/{search_id}/leads", response_model=List[LeadSchema])
async def get_search_leads(
    search_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify search belongs to user
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    
    leads = db.query(Lead).filter(Lead.search_id == search_id).all()
    return leads

# Export endpoints
@app.post("/exports", response_model=ExportSchema)
async def create_export(
    export: ExportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify search belongs to user
    search = db.query(Search).filter(
        Search.id == export.search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Get leads count
    leads_count = db.query(Lead).filter(Lead.search_id == export.search_id).count()
    
    # Create export record
    db_export = Export(
        user_id=current_user.id,
        search_id=export.search_id,
        export_type=export.export_type,
        leads_count=leads_count
    )
    db.add(db_export)
    db.commit()
    db.refresh(db_export)
    
    return db_export

@app.get("/exports/{search_id}/csv")
async def export_csv(
    search_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify search belongs to user
    search = db.query(Search).filter(
        Search.id == search_id,
        Search.user_id == current_user.id
    ).first()
    
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    
    # Get leads
    leads = db.query(Lead).filter(Lead.search_id == search_id).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Business Name', 'Phone', 'Email', 'Website', 'Address',
        'Category', 'Rating', 'Review Count', 'Email Message',
        'SMS Message', 'Quality Score'
    ])
    
    # Write leads
    for lead in leads:
        writer.writerow([
            lead.business_name,
            lead.phone or '',
            lead.email or '',
            lead.website or '',
            lead.address or '',
            lead.category or '',
            lead.rating or '',
            lead.review_count or '',
            lead.ai_email_message or '',
            lead.ai_sms_message or '',
            lead.quality_score or ''
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=leads_{search_id}.csv"}
    )

# Dashboard endpoints
@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    total_searches = db.query(Search).filter(Search.user_id == current_user.id).count()
    total_leads = db.query(Lead).join(Search).filter(Search.user_id == current_user.id).count()
    total_exports = db.query(Export).filter(Export.user_id == current_user.id).count()
    
    trial_days_left = None
    if current_user.subscription_status == "trial" and current_user.trial_ends_at:
        days_left = (current_user.trial_ends_at - datetime.utcnow()).days
        trial_days_left = max(0, days_left)
    
    return DashboardStats(
        total_searches=total_searches,
        total_leads=total_leads,
        total_exports=total_exports,
        trial_days_left=trial_days_left
    )

# Admin endpoints
@app.get("/admin/users", response_model=List[UserSchema])
async def get_all_users(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users

@app.get("/admin/stats")
async def get_admin_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    active_trials = db.query(User).filter(
        User.subscription_status == "trial",
        User.trial_ends_at > datetime.utcnow()
    ).count()
    active_subscriptions = db.query(User).filter(
        User.subscription_status == "active"
    ).count()
    total_searches = db.query(Search).count()
    total_leads = db.query(Lead).count()
    
    return {
        "total_users": total_users,
        "active_trials": active_trials,
        "active_subscriptions": active_subscriptions,
        "total_searches": total_searches,
        "total_leads": total_leads
    }

@app.get("/")
async def root():
    return {"message": "LeadNest API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "leadnest-api", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
