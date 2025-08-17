# 🚀 RENDER DEPLOYMENT FIX - Step by Step Guide

## URGENT: Your Render service is not running. Follow these exact steps:

### Step 1: Access Render Dashboard
1. **Go to**: https://render.com/
2. **Log in** with your account credentials
3. **Find your service**: Look for `leadnest-api` in your services list

### Step 2: Check Service Status & Logs
1. **Click on `leadnest-api`** service
2. **Go to "Logs" tab** - This will show you exactly what's wrong
3. **Look for error messages** - Common errors:
   - `ModuleNotFoundError`
   - `Failed to bind to port` 
   - `Database connection failed`
   - `Redis connection failed`
   - `Import error`

### Step 3: Fix Based on Error Type

#### If you see "ModuleNotFoundError":
The build failed. Your requirements.txt is missing dependencies.

**Action**: The current requirements.txt looks good, but if there are missing modules, add them.

#### If you see "Failed to bind to port" or "Address already in use":
The start command is wrong or PORT variable issue.

**Action**: Verify start command is exactly:
```
gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

#### If you see "Database connection failed":
DATABASE_URL is not set or PostgreSQL service is not running.

**Action**: 
1. Check if you have a PostgreSQL service running
2. Verify DATABASE_URL is connected from the PostgreSQL service

#### If you see "Redis connection failed":
REDIS_URL is not set or Redis service is not running.

**Action**:
1. Check if you have a Redis service running  
2. Verify REDIS_URL is connected from the Redis service

### Step 4: Complete Service Setup

#### A. Create Missing Services (if needed)

**PostgreSQL Database:**
1. In Render dashboard, click "New +"
2. Select "PostgreSQL" 
3. Name: `leadnest-db`
4. Plan: Free tier
5. Create database

**Redis:**
1. In Render dashboard, click "New +"  
2. Select "Redis"
3. Name: `leadnest-redis`
4. Plan: Free tier
5. Create Redis instance

#### B. Configure Environment Variables
In your `leadnest-api` service:

1. **Go to "Environment" tab**
2. **Add/Update these variables:**

```
JWT_SECRET = [Auto-generate a 32+ character secret]
DATABASE_URL = [Link to PostgreSQL service - should auto-populate]
REDIS_URL = [Link to Redis service - should auto-populate] 
PUBLIC_BASE_URL = https://leadnest-api.onrender.com
CORS_ORIGINS = https://leadnest.vercel.app
FLASK_ENV = production
FLASK_DEBUG = 0
LOG_LEVEL = INFO

# Add these manually with your actual values:
TWILIO_ACCOUNT_SID = YOUR_ACTUAL_SID_HERE
TWILIO_AUTH_TOKEN = YOUR_ACTUAL_TOKEN_HERE  
TWILIO_PHONE_NUMBER = +1XXXXXXXXXX
OPENAI_API_KEY = sk-proj-YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY = pk_live_REDACTED
STRIPE_SECRET_KEY = sk_live_REDACTED
STRIPE_WEBHOOK_SECRET = whsec_REDACTED
```

#### C. Verify Configuration Settings
1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
3. **Root Directory**: Leave blank or set to `/`
4. **Health Check Path**: `/healthz`
5. **Auto-Deploy**: Enabled
6. **Branch**: main

### Step 5: Deploy/Redeploy

#### If Service Exists:
1. Click **"Manual Deploy"** at top right
2. Select **"Deploy latest commit"**
3. Click **"Deploy"**

#### If Service Doesn't Exist:
1. Click **"New +"** → **"Web Service"**
2. **Connect GitHub repo**: useleadnest/leadnest
3. **Configure as above**
4. **Create Web Service**

### Step 6: Monitor Deployment
1. **Watch the "Logs" tab** during deployment
2. **Look for**:
   - ✅ `Installing dependencies`
   - ✅ `Starting gunicorn`
   - ✅ `Listening at: http://0.0.0.0:XXXX`
   - ✅ `Application startup complete`

### Step 7: Test Deployment
Once you see "Application startup complete":

1. **Test health endpoint**:
```bash
curl https://leadnest-api.onrender.com/healthz
```

Expected response:
```json
{"status": "ok", "timestamp": "2025-01-17T..."}
```

2. **If still getting 404**: 
   - Check the root directory setting
   - Verify the health check path matches your code
   - Look at logs for any startup errors

### Step 8: Final Verification

Run our diagnosis script:
```powershell
.\DiagnoseApi.ps1 -ApiDomain "leadnest-api.onrender.com"
```

Should show:
- ✅ DNS Resolution: SUCCESS
- ✅ Port 443: OPEN  
- ✅ Health endpoint: Status 200
- ✅ No more "x-render-routing: no-server" header

### Common Issues & Solutions

**Issue**: Build succeeds but app won't start
**Solution**: Check start command and PORT binding

**Issue**: Database errors on startup
**Solution**: Run database migrations manually in Render shell

**Issue**: 502 Bad Gateway  
**Solution**: App is crashing on startup, check logs

**Issue**: Still getting 404 after deployment
**Solution**: Verify file structure and root directory setting

### Emergency Commands (if needed)

**Check what files are actually deployed:**
```bash
# In Render shell
ls -la
ls -la backend-flask/  
```

**Test start command manually:**
```bash  
# In Render shell
cd backend-flask
gunicorn wsgi:app --bind 0.0.0.0:10000
```

**Check Python environment:**
```bash
# In Render shell  
python -c "from app import create_app; print('OK')"
```

## Next Steps After Fix

1. ✅ Verify API is responding
2. ✅ Run full smoke tests
3. ✅ Test all endpoints
4. ✅ Verify database connectivity
5. ✅ Test Twilio webhooks

---

**🎯 ACTION REQUIRED**: Go to Render dashboard NOW and check the service logs. The exact error message will tell us exactly what to fix.
