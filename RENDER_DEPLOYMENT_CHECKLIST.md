# ✅ RENDER DEPLOYMENT CHECKLIST

## Before You Start
- [ ] You have access to https://render.com/
- [ ] Your GitHub repository is at useleadnest/leadnest  
- [ ] All code is pushed to the `main` branch

## Step 1: Create Services (If They Don't Exist)

### PostgreSQL Database
- [ ] Go to Render Dashboard → New + → PostgreSQL
- [ ] Name: `leadnest-db`  
- [ ] Plan: Free tier
- [ ] Wait for creation to complete

### Redis Cache  
- [ ] Go to Render Dashboard → New + → Redis
- [ ] Name: `leadnest-redis`
- [ ] Plan: Free tier  
- [ ] Wait for creation to complete

### Web Service
- [ ] Go to Render Dashboard → New + → Web Service
- [ ] Connect GitHub: useleadnest/leadnest
- [ ] Name: `leadnest-api`
- [ ] Branch: `main`
- [ ] Root Directory: `backend-flask`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`

## Step 2: Environment Variables Setup

### In the leadnest-api service Environment tab:

#### Auto-Connected Services
- [ ] `DATABASE_URL` → Connected to leadnest-db PostgreSQL
- [ ] `REDIS_URL` → Connected to leadnest-redis Redis  
- [ ] `JWT_SECRET` → Auto-generate (32+ characters)

#### Manual Configuration  
- [ ] `PUBLIC_BASE_URL` = `https://leadnest-api.onrender.com`
- [ ] `CORS_ORIGINS` = `https://leadnest.vercel.app,https://useleadnest.com`
- [ ] `FLASK_ENV` = `production`
- [ ] `FLASK_DEBUG` = `0`
- [ ] `LOG_LEVEL` = `INFO`

#### Third-Party Services (Add Your Real Values)
- [ ] `TWILIO_ACCOUNT_SID` = Your actual Twilio SID
- [ ] `TWILIO_AUTH_TOKEN` = Your actual Twilio token  
- [ ] `TWILIO_PHONE_NUMBER` = Your actual Twilio number (+1XXXXXXXXXX)
- [ ] `OPENAI_API_KEY` = Your actual OpenAI key (sk-proj-...)
- [ ] `STRIPE_PUBLISHABLE_KEY` = Your actual Stripe publishable key (pk_live_...)
- [ ] `STRIPE_SECRET_KEY` = Your actual Stripe secret key (sk_live_...)  
- [ ] `STRIPE_WEBHOOK_SECRET` = Your actual Stripe webhook secret (whsec_...)

## Step 3: Deploy & Monitor

### Deploy
- [ ] Click "Manual Deploy" → "Deploy latest commit"  
- [ ] OR if new service: Click "Create Web Service"

### Monitor Deployment Logs
Look for these success indicators:
- [ ] ✅ "Installing dependencies"
- [ ] ✅ "Successfully built"  
- [ ] ✅ "Starting gunicorn"
- [ ] ✅ "Listening at: http://0.0.0.0:XXXX"
- [ ] ✅ "Application startup complete"

### Common Error Patterns to Watch For
- [ ] ❌ "ModuleNotFoundError" → Missing dependency
- [ ] ❌ "Failed to bind to port" → Start command issue
- [ ] ❌ "Database connection failed" → DATABASE_URL issue  
- [ ] ❌ "Redis connection failed" → REDIS_URL issue
- [ ] ❌ "ImportError" → Code structure issue

## Step 4: Verification Tests

### Test 1: Basic Health Check
```powershell  
Invoke-WebRequest -Uri "https://leadnest-api.onrender.com/healthz" -UseBasicParsing
```
Expected: Status 200, JSON response

### Test 2: Comprehensive Verification
```powershell
.\RenderVerify.ps1 -ApiDomain "leadnest-api.onrender.com"  
```
Expected: All tests pass

### Test 3: Full Smoke Test
```powershell
.\ProductionVerify.ps1 -ApiDomain "leadnest-api.onrender.com"
```  
Expected: All endpoints responding

## Step 5: Final Production Setup

### Worker Service (Background Jobs)
- [ ] Create second service: New + → Background Worker
- [ ] Name: `leadnest-worker`
- [ ] Same repo: useleadnest/leadnest
- [ ] Root Directory: `backend-flask`  
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python worker.py`
- [ ] Copy same environment variables as web service

### Health Check Configuration  
- [ ] Health Check Path: `/healthz`
- [ ] Health Check Timeout: 30 seconds
- [ ] Auto-Deploy: Enabled

## Troubleshooting Guide

### If Deployment Fails
1. [ ] Check specific error in Logs tab
2. [ ] Verify all environment variables are set  
3. [ ] Test start command locally first
4. [ ] Check file structure matches render.yaml

### If App Won't Start
1. [ ] Verify DATABASE_URL and REDIS_URL are connected
2. [ ] Check if databases are actually running
3. [ ] Look for import errors in logs
4. [ ] Test wsgi.py locally

### If Getting 404 Errors  
1. [ ] Check Root Directory setting
2. [ ] Verify Health Check Path matches code
3. [ ] Ensure files are in correct locations
4. [ ] Check build output for missing files

## Success Criteria

### All Must Be True:
- [ ] Service shows "Live" status in dashboard
- [ ] Health endpoint returns 200 OK
- [ ] No errors in service logs  
- [ ] Response time < 3 seconds
- [ ] Auth endpoints reject invalid requests properly
- [ ] CORS headers present
- [ ] All environment variables populated

### Ready for Production:
- [ ] SSL certificate active (https://)
- [ ] Domain resolves correctly  
- [ ] Database migrations applied
- [ ] Background worker running
- [ ] Monitoring/logging working

---

## 🎯 CURRENT STATUS AFTER COMPLETING THIS CHECKLIST:

**Run this to confirm success:**
```powershell
.\DiagnoseApi.ps1 -ApiDomain "leadnest-api.onrender.com"
```

**Expected result:** No more "x-render-routing: no-server" errors!

---

*This checklist ensures zero deployment issues and production-ready service.*
