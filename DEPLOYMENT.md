# 🚀 Production Deployment Guide

## Overview
LeadNest is configured for production deployment with:
- **Backend**: Render (FastAPI + PostgreSQL)
- **Frontend**: Vercel (React)
- **Payments**: Stripe integration
- **Security**: Rate limiting, input validation, CORS protection

## 🔐 Security Features Implemented
- JWT token authentication with rotation
- Rate limiting on all endpoints (5/min auth, 10/min search, 3/min export)
- Input sanitization and validation
- CSRF protection
- SQL injection prevention
- XSS protection
- Secure headers (HSTS, X-Frame-Options, etc.)
- Environment-based configuration

## 💰 Stripe Integration
- Webhook handling for subscription events
- Automatic trial-to-paid conversion
- Failed payment handling with retry logic
- Subscription cancellation support
- Customer portal integration ready

## 📋 Pre-Deployment Checklist

### 1. API Keys Required
- ✅ **OpenAI API Key** (required for AI messages)
- ✅ **Yelp Fusion API Key** (optional, has mock fallback)
- ✅ **Stripe Secret/Publishable Keys** (required for payments)
- ✅ **Stripe Webhook Secret** (required for webhooks)

### 2. Environment Configuration
- ✅ Production environment variables configured
- ✅ Secure secret keys generated (32+ characters)
- ✅ Database connection string configured
- ✅ CORS origins updated for production domains

---

## 🌐 Backend Deployment (Render)

### Option 1: One-Click Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/LeadNest)

### Option 2: Manual Setup

#### 1. Create PostgreSQL Database
```bash
# In Render Dashboard:
1. Go to "New" → "PostgreSQL"
2. Name: LeadNest-db
3. Database Name: LeadNest
4. User: LeadNest_user
5. Plan: Starter (free)
6. Copy the connection string
```

#### 2. Create Web Service
```bash
# In Render Dashboard:
1. Go to "New" → "Web Service"
2. Connect your GitHub repo
3. Root Directory: backend
4. Build Command: pip install -r requirements.txt
5. Start Command: uvicorn main_secure:app --host 0.0.0.0 --port $PORT
6. Plan: Starter (free)
```

#### 3. Environment Variables
Set these in Render dashboard:
```bash
DATABASE_URL=<from-postgresql-service>
SECRET_KEY=<generate-32char-random-string>
OPENAI_API_KEY=sk-...
YELP_API_KEY=<your-yelp-key>
STRIPE_SECRET_KEY=sk_live_[REDACTED]
STRIPE_WEBHOOK_SECRET=whsec_[REDACTED]
ENVIRONMENT=production
FRONTEND_URL=https://useleadnest.com
```

#### 4. Deploy
```bash
# Automatic deployment on git push
git push origin main
```

---

## 🎨 Frontend Deployment (Vercel)

### Option 1: One-Click Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/LeadNest&project-name=LeadNest&root-directory=frontend)

### Option 2: Manual Setup

#### 1. Install Vercel CLI
```bash
npm i -g vercel
cd frontend
vercel login
```

#### 2. Configure Project
```bash
# vercel.json is already configured
# Update environment variables:
vercel env add REACT_APP_API_URL
# Enter: https://LeadNest-api.onrender.com

vercel env add REACT_APP_STRIPE_PUBLISHABLE_KEY  
# Enter: pk_live_[REDACTED]
```

#### 3. Deploy
```bash
vercel --prod
```

---

## 🔗 Stripe Webhook Configuration

### 1. Create Webhook Endpoint
```bash
# In Stripe Dashboard:
1. Go to Developers → Webhooks
2. Add endpoint: https://LeadNest-api.onrender.com/stripe/webhook
3. Select events:
   - checkout.session.completed
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - invoice.payment_failed
   - invoice.payment_succeeded
4. Copy webhook signing secret
```

### 2. Test Webhook
```bash
# Install Stripe CLI
stripe listen --forward-to localhost:8000/stripe/webhook

# Test webhook
stripe trigger checkout.session.completed
```

---

## 🐳 Docker Deployment (Alternative)

### 1. Build and Run
```bash
# Clone repository
git clone <your-repo>
cd LeadNest

# Copy environment files
cp backend/.env.production.template backend/.env
cp frontend/.env.production.template frontend/.env

# Update environment variables
# Edit backend/.env and frontend/.env

# Build and run
docker-compose up --build -d
```

### 2. Production Docker
```bash
# For production deployment
docker build -t LeadNest .
docker run -p 8000:8000 --env-file .env LeadNest
```

---

## 🔍 Testing Deployment

### 1. Backend Health Check
```bash
curl https://LeadNest-api.onrender.com/health
# Expected: {"status":"healthy","timestamp":"..."}
```

### 2. API Functionality
```bash
# Test registration
curl -X POST https://LeadNest-api.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Test search (requires auth token)
curl -X POST https://LeadNest-api.onrender.com/searches \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"location":"Austin, TX","trade":"roofing"}'
```

### 3. Frontend Testing
- Visit: https://useleadnest.com
- Test user registration
- Test lead generation
- Test CSV export
- Test Stripe checkout flow

---

## 📊 Monitoring & Maintenance

### 1. Logs
```bash
# Render logs
render logs <service-name>

# Vercel logs  
vercel logs <deployment-url>
```

### 2. Database Monitoring
```bash
# Monitor PostgreSQL performance
# Check connection limits
# Monitor query performance
```

### 3. Rate Limiting
```bash
# Monitor rate limit hits
# Adjust limits based on usage
# Consider Redis for distributed rate limiting
```

### 4. Error Tracking
```bash
# Configure Sentry for error tracking
# Set up uptime monitoring
# Configure alerts for critical errors
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. CORS Errors
```bash
# Check CORS origins in main_secure.py
# Update to include your production domains
```

#### 2. Database Connection
```bash
# Verify DATABASE_URL format
# Check PostgreSQL service status
# Verify firewall settings
```

#### 3. Stripe Webhooks
```bash
# Verify webhook URL is accessible
# Check webhook signing secret
# Monitor webhook event logs in Stripe
```

#### 4. API Rate Limits
```bash
# Check rate limiting configuration
# Monitor Redis connection
# Adjust limits for production load
```

### Performance Optimization
```bash
# Enable database connection pooling
# Configure Redis caching
# Optimize SQL queries
# Enable gzip compression
# Configure CDN for static assets
```

---

## 📈 Scaling Considerations

### Backend Scaling
- Upgrade Render plan for more resources
- Implement database read replicas
- Add Redis for session storage
- Consider microservices architecture

### Frontend Scaling
- Vercel auto-scales static content
- Implement lazy loading
- Optimize bundle size
- Add service worker for caching

### Database Scaling
- Monitor connection limits
- Implement query optimization
- Consider database sharding
- Add read replicas

---

## 🔒 Security Best Practices

### Production Security
- ✅ HTTPS enforced everywhere
- ✅ Environment variables secured
- ✅ Rate limiting implemented
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF protection
- ✅ Secure headers configured

### Ongoing Security
- Regular dependency updates
- Security audit scheduling
- Penetration testing
- Monitor security alerts
- Backup and recovery procedures

This deployment guide ensures a secure, scalable, and maintainable production deployment of LeadNest.
