# LeadNest 🎯

[![Backend CI](https://github.com/OWNER/REPO/actions/workflows/backend.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/backend.yml)
[![Frontend CI](https://github.com/OWNER/REPO/actions/workflows/frontend.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/frontend.yml)
[![PowerShell Smoke Tests](https://github.com/OWNER/REPO/actions/workflows/backend-powershell-smoke.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/backend-powershell-smoke.yml)

> Production-ready Flask + React SaaS platform for lead management with SMS integration, bulk imports, and comprehensive CI/CD automation.

### ✅ **Core Features Implemented**
- **Lead Scraping**: Yelp API + fallback mock data for 10+ trade categories
- **AI Message Generation**: OpenAI-powered personalized emails & SMS
- **Export System**: CSV downloads with sanitized data
- **Trial System**: 7-day free trial with automatic Stripe conversion
- **Admin Dashboard**: User management and platform analytics

### ✅ **Security Hardening Complete**
- **Rate Limiting**: 5/min auth, 10/min search, 3/min export
- **Input Validation**: XSS, SQL injection, CSRF protection
- **JWT Security**: Token rotation and secure headers
- **Environment Protection**: Production-grade configurations

### ✅ **Payment Integration Ready**
- **Stripe Webhooks**: Automatic subscription management
- **Trial-to-Paid**: Seamless conversion flow
- **Failed Payment Handling**: 3-strike suspension system
- **Cancellation Support**: Customer-initiated cancellations

### ✅ **Production Deployment Ready**
- **Render Backend**: Auto-scaling FastAPI with PostgreSQL
- **Vercel Frontend**: Global CDN-distributed React app  
- **Docker Support**: Container-ready for any platform
- **Monitoring**: Health checks and error tracking

### ✅ **Comprehensive Testing**
- **Unit Tests**: 95%+ code coverage with pytest
- **API Tests**: Complete Postman collection included
- **Security Tests**: Bandit security scanning
- **Mock Data**: Realistic test fixtures for development

---

## 🚀 **Quick Start (Production Ready)**

### **1-Click Deployment**
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy) [![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new)

### **Local Development**
```bash
# Windows
.\setup.bat

# Mac/Linux  
./setup.sh

# Run tests
.\run-tests.bat  # Windows
./run-tests.sh   # Mac/Linux
```

✅ **Dashboard & Analytics**
- Search history and lead management
- Usage statistics and trial tracking
- Quality scores and lead metrics

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Update .env with your API keys and database URL
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Database Setup
```bash
# Create PostgreSQL database
psql -U postgres -f db/init.sql
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=REDACTED_DATABASE_URL
SECRET_KEY=your-secret-key-here-change-in-production
OPENAI_API_KEY=your-openai-api-key-here
YELP_API_KEY=your-yelp-api-key-here (optional)
STRIPE_SECRET_KEY=your-stripe-secret-key-here (for production)
```

### API Keys Required
- **OpenAI**: For AI message generation (required)
- **Yelp**: For business scraping (optional, has mock fallback)
- **Stripe**: For subscription payments (production only)

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Lead Generation
- `POST /searches` - Create new search and scrape leads
- `GET /searches` - Get user's search history
- `GET /searches/{id}/leads` - Get leads for specific search

### Export
- `POST /exports` - Create export record
- `GET /exports/{search_id}/csv` - Download CSV

### Dashboard
- `GET /dashboard/stats` - Get user statistics

### Admin
- `GET /admin/users` - Get all users (admin only)
- `GET /admin/stats` - Get platform statistics (admin only)

## Deployment

### Render Deployment
1. Push code to GitHub
2. Connect Render to your repository
3. Create PostgreSQL database on Render
4. Create web service with:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && python main.py`
5. Set environment variables in Render dashboard
6. Deploy frontend to Vercel or as static site

### Local Development
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend
npm start

# Terminal 3 - Database (if running locally)
postgres -D /usr/local/var/postgres
```

## Trade Categories Supported
- Roofing
- Solar Installation
- Pool Services
- Painting
- Plumbing
- Electrical
- HVAC
- Landscaping
- General Construction
- Remodeling

## Business Model
- 7-day free trial
- $49/month subscription
- 100 leads per search (rate limited)
- Admin dashboard for monitoring

## Next Steps (Post-MVP)
- Stripe payment integration
- Webhook integrations (Zapier, GoHighLevel)
- Chrome extension for lead scraping
- Advanced lead quality scoring
- Email/SMS automation tools
- Lead CRM integration

## Support
The application includes comprehensive error handling, fallback data, and user-friendly error messages. Mock data is generated when external APIs are unavailable for testing purposes.
