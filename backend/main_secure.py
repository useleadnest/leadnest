from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import csv
import io
from fastapi.responses import StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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
from security import (
    SecurityMiddleware, CSRFProtection, SecureHTTPBearer,
    rate_limit_auth, rate_limit_search, rate_limit_export, rate_limit_general
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LeadNest API", 
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.onrender.com", "*.vercel.app", "useleadnest.com", "*.useleadnest.com"]
)

# CORS middleware with strict settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://useleadnest.com",
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://*.vercel.app",
        "https://*.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

security = SecureHTTPBearer()
scraper = LeadScraper()

# Enhanced request validation middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Content-Type validation for POST/PUT requests
    if request.method in ["POST", "PUT"]:
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return HTTPException(status_code=400, detail="Invalid content type")
    
    # Request size limitation (10MB)
    if request.headers.get("content-length"):
        content_length = int(request.headers["content-length"])
        if content_length > 10 * 1024 * 1024:  # 10MB
            return HTTPException(status_code=413, detail="Request too large")
    
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY" 
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Auth endpoints with rate limiting
@app.post("/auth/register", response_model=UserSchema)
@rate_limit_auth()
async def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    # Enhanced input validation
    if not SecurityMiddleware.validate_email(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    is_valid, message = SecurityMiddleware.validate_password(user.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Sanitize input
    user.email = SecurityMiddleware.sanitize_input(user.email)
    
    # Check if user exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    db_user = create_user(db, email=user.email, password=user.password)
    return db_user

@app.post("/auth/login", response_model=Token)
@rate_limit_auth()
async def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
    # Sanitize input
    user.email = SecurityMiddleware.sanitize_input(user.email)
    
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
@rate_limit_general()
async def read_users_me(request: Request, current_user: User = Depends(get_current_active_user)):
    return current_user

# Search and Lead endpoints with enhanced validation
@app.post("/searches", response_model=SearchSchema)
@rate_limit_search()
async def create_search(
    request: Request,
    search: SearchCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Enhanced input validation
    if not SecurityMiddleware.validate_location(search.location):
        raise HTTPException(status_code=400, detail="Invalid location format")
    
    if not SecurityMiddleware.validate_trade(search.trade):
        raise HTTPException(status_code=400, detail="Invalid trade category")
    
    # Sanitize inputs
    search.location = SecurityMiddleware.sanitize_input(search.location)
    search.trade = SecurityMiddleware.sanitize_input(search.trade)
    
    # Check trial status with enhanced validation
    if current_user.subscription_status == "trial":
        if not current_user.trial_ends_at:
            raise HTTPException(status_code=402, detail="Invalid trial status")
        if current_user.trial_ends_at < datetime.utcnow():
            raise HTTPException(status_code=402, detail="Trial expired. Please upgrade to continue.")
    
    # Rate limiting: max 5 searches per hour for trial users
    if current_user.subscription_status == "trial":
        recent_searches = db.query(Search).filter(
            Search.user_id == current_user.id,
            Search.created_at > datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        if recent_searches >= 5:
            raise HTTPException(
                status_code=429,
                detail="Trial users limited to 5 searches per hour"
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
    
    # Scrape leads with error handling
    try:
        leads_data = scraper.scrape_yelp_businesses(search.location, search.trade, limit=100)
        if not leads_data:
            leads_data = scraper.scrape_mock_data(search.location, search.trade, limit=50)
        
        # Limit results for trial users
        if current_user.subscription_status == "trial":
            leads_data = leads_data[:25]  # Limit to 25 leads for trial
        
        # Enrich with AI and save to database
        db_leads = []
        for lead_data in leads_data:
            # Sanitize lead data
            for key, value in lead_data.items():
                if isinstance(value, str):
                    lead_data[key] = SecurityMiddleware.sanitize_input(value)
            
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
        raise HTTPException(status_code=500, detail="Error generating leads. Please try again.")

@app.get("/searches", response_model=List[SearchSchema])
@rate_limit_general()
async def get_searches(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    searches = db.query(Search).filter(Search.user_id == current_user.id).all()
    return searches

@app.get("/searches/{search_id}/leads", response_model=List[LeadSchema])
@rate_limit_general()
async def get_search_leads(
    request: Request,
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

# Export endpoints with enhanced security
@app.post("/exports", response_model=ExportSchema)
@rate_limit_export()
async def create_export(
    request: Request,
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
    
    # Rate limiting: max 10 exports per day for trial users
    if current_user.subscription_status == "trial":
        today_exports = db.query(Export).filter(
            Export.user_id == current_user.id,
            Export.created_at > datetime.utcnow() - timedelta(days=1)
        ).count()
        
        if today_exports >= 10:
            raise HTTPException(
                status_code=429,
                detail="Trial users limited to 10 exports per day"
            )
    
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
@rate_limit_export()
async def export_csv(
    request: Request,
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
    
    # Create CSV with sanitized data
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Business Name', 'Phone', 'Email', 'Website', 'Address',
        'Category', 'Rating', 'Review Count', 'Email Message',
        'SMS Message', 'Quality Score'
    ])
    
    # Write leads with sanitized data
    for lead in leads:
        writer.writerow([
            SecurityMiddleware.sanitize_input(lead.business_name or ''),
            SecurityMiddleware.sanitize_input(lead.phone or ''),
            SecurityMiddleware.sanitize_input(lead.email or ''),
            SecurityMiddleware.sanitize_input(lead.website or ''),
            SecurityMiddleware.sanitize_input(lead.address or ''),
            SecurityMiddleware.sanitize_input(lead.category or ''),
            lead.rating or '',
            lead.review_count or '',
            SecurityMiddleware.sanitize_input(lead.ai_email_message or ''),
            SecurityMiddleware.sanitize_input(lead.ai_sms_message or ''),
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
@rate_limit_general()
async def get_dashboard_stats(
    request: Request,
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

# Admin endpoints with enhanced security
@app.get("/admin/users", response_model=List[UserSchema])
@rate_limit_general()
async def get_all_users(
    request: Request,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users

@app.get("/admin/stats")
@rate_limit_general()
async def get_admin_stats(
    request: Request,
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
    return {"message": "LeadNest API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
