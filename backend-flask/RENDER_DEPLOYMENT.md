# LeadNest Backend Deployment Guide for Render.com

## Quick Deploy to Render

### 1. Create New Web Service
1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect GitHub repository: `useleadnest/leadnest`
4. Configure deployment:

**Basic Settings:**
- Name: `leadnest-api`
- Environment: `Python 3`
- Region: `US West (Oregon)` or closest to your users
- Branch: `main`
- Root Directory: `backend-flask`

**Build & Deploy:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`

### 2. Environment Variables (Set in Render Dashboard)

**Required Variables:**
```
DATABASE_URL=<Render will provide PostgreSQL URL>
JWT_SECRET=<Generate 64-character secret>
PUBLIC_BASE_URL=https://api.useleadnest.com
CORS_ORIGINS=https://useleadnest.com,https://*.vercel.app,https://docs.useleadnest.com
REDIS_URL=<Render will provide Redis URL>
FLASK_ENV=production
```

**Stripe Variables:**
```
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PRICE_STARTER=price_xxx_starter
STRIPE_PRICE_PRO=price_xxx_pro
STRIPE_PRICE_ENTERPRISE=price_xxx_enterprise
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

**Twilio Variables:**
```
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_FROM=+1234567890
```

### 3. Add Database & Redis
1. In Render Dashboard → "New +" → "PostgreSQL"
   - Name: `leadnest-db`
   - Copy DATABASE_URL to environment variables
2. In Render Dashboard → "New +" → "Redis" 
   - Name: `leadnest-redis`
   - Copy REDIS_URL to environment variables

### 4. Custom Domain Setup
1. In Web Service → Settings → "Custom Domains"
2. Add domain: `api.useleadnest.com`
3. Configure DNS:
   - Type: CNAME
   - Name: api
   - Value: leadnest-api.onrender.com

### 5. Health Check Configuration
**Health Check Path:** `/healthz`
**Expected Status:** 200

### 6. Deployment Verification

Test these endpoints after deployment:
```bash
curl https://api.useleadnest.com/healthz
curl https://api.useleadnest.com/readyz
curl https://api.useleadnest.com/api/auth/login -X POST -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password"}'
```

## Production Checklist

- [ ] PostgreSQL database connected
- [ ] Redis cache connected
- [ ] All environment variables set
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] Health checks passing
- [ ] Database migrations run
- [ ] Stripe webhooks configured
- [ ] Twilio webhooks configured

## Post-Deployment Steps

1. **Run Database Migrations:**
   ```bash
   # This should happen automatically, but verify in logs
   flask db upgrade
   ```

2. **Configure Stripe Webhooks:**
   - Go to Stripe Dashboard → Webhooks
   - Add endpoint: `https://api.useleadnest.com/api/stripe/webhook`
   - Events: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_succeeded`, `invoice.payment_failed`

3. **Configure Twilio Webhooks:**
   - Go to Twilio Console → Phone Numbers
   - Set webhook URL: `https://api.useleadnest.com/api/twilio/inbound`
   - Method: POST

4. **Test Critical Paths:**
   - User registration/login
   - Lead creation and AI scoring
   - Stripe subscription flow
   - Twilio message handling
   - CSV bulk import

## Monitoring & Logs

- **Render Logs:** Available in dashboard
- **Application Logs:** Check for startup errors
- **Database Logs:** Monitor connection issues
- **Redis Logs:** Verify cache functionality

## Scaling Configuration

**Initial Setup (Suitable for 100+ concurrent users):**
- Plan: Starter ($7/month)
- RAM: 512 MB
- CPU: 0.1 vCPU
- Workers: 2
- Threads: 4

**Scale Up When Needed:**
- Plan: Standard ($25/month) 
- RAM: 2 GB
- CPU: 1 vCPU
- Workers: 4
- Threads: 8

Your LeadNest backend will be production-ready and scalable!
