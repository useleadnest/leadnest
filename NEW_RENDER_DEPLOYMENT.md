# 🚀 NEW RENDER SERVICE DEPLOYMENT GUIDE

## The Issue
The current leadnest-backend-2 service appears to have a deployment configuration issue where it's not pulling the latest code from GitHub.

## Solution: Create Fresh Service

### Step 1: Create New Render Service
1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect to GitHub repo: `useleadnest/leadnest-backend`
4. Configure:
   - **Name:** `leadnest-api-v3`
   - **Environment:** `Python`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 2: Environment Variables
Set these in the Render dashboard:
```
DATABASE_URL=<your_postgres_url>
JWT_SECRET_KEY=<auto_generate>
STRIPE_PUBLISHABLE_KEY=<your_stripe_key>
STRIPE_SECRET_KEY=<your_stripe_secret>
STRIPE_WEBHOOK_SECRET=<your_webhook_secret>
OPENAI_API_KEY=<your_openai_key>
FRONTEND_URL=https://useleadnest.com
ENVIRONMENT=production
```

### Step 3: Update Frontend Config
Once the new service is deployed, update the frontend API URL:

```bash
# In frontend/.env.production
VITE_API_URL=https://leadnest-api-v3.onrender.com
```

### Step 4: Test New Service
- Health check: `https://leadnest-api-v3.onrender.com/health`
- Registration: `https://leadnest-api-v3.onrender.com/auth/register`
- Docs: `https://leadnest-api-v3.onrender.com/docs`

## Alternative: Manual Deploy Current Service

If you prefer to fix the current service:

1. Go to Render dashboard → leadnest-backend-2
2. Go to "Settings" tab
3. Check "Auto-Deploy" is enabled for main branch
4. Go to "Manual Deploy" → Deploy latest commit
5. Monitor deployment logs for errors

## Quick Test Commands

Once deployed, test with these commands:

```powershell
# Test health endpoint
Invoke-RestMethod -Uri "https://NEW_SERVICE_URL/health"

# Test registration endpoint  
Invoke-RestMethod -Uri "https://NEW_SERVICE_URL/auth/register" -Method POST -ContentType "application/json" -Body '{"email":"test@example.com","password":"testpass123"}'

# Check all endpoints
Invoke-RestMethod -Uri "https://NEW_SERVICE_URL/openapi.json"
```

The new service should show ~8-10 endpoints instead of just 3.
