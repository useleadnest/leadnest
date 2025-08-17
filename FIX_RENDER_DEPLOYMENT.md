# 🔧 FIX LEADNEST-BACKEND-2 RENDER SERVICE

## The Problem
The leadnest-backend-2 service is running but **NOT** deploying the latest code from GitHub. It's stuck on an old version.

## 🎯 SOLUTION: Fix Render Dashboard Settings

### Step 1: Access Render Dashboard
1. Go to https://render.com/dashboard
2. Find and click on **leadnest-backend-2** service

### Step 2: Check Auto-Deploy Settings
1. Go to **Settings** tab
2. Scroll to **Auto-Deploy** section
3. Ensure **Auto-Deploy** is **ENABLED**
4. Verify **Branch** is set to **main**
5. If not enabled, enable it and save

### Step 3: Manual Deploy Latest
1. Go to **Manual Deploy** section (same Settings tab)
2. Click **Deploy latest commit**
3. Select branch: **main**
4. Click **Deploy**

### Step 4: Monitor Deployment
1. Go to **Logs** tab
2. Watch for deployment progress
3. Look for any error messages
4. Wait for "Deploy succeeded" message

### Step 5: Verify Fix
Test these endpoints after deployment:
```
https://leadnest-backend-2.onrender.com/debug-info
https://leadnest-backend-2.onrender.com/test-deploy  
https://leadnest-backend-2.onrender.com/auth/register
```

## 🔍 What Should Happen

**Before Fix:**
- Only 3 endpoints (/, /health, /stripe/webhook)
- Old version deployed

**After Fix:**
- ~10+ endpoints including /auth/register
- New version with debug info
- Registration endpoint working

## ⚡ Alternative: Quick Service Recreation

If the above doesn't work:

1. **Delete** leadnest-backend-2 service
2. **Create new** web service
3. **Connect** to useleadnest/leadnest-backend repo
4. **Configure:**
   - Name: leadnest-backend-3
   - Branch: main
   - Build: `pip install -r requirements.txt`
   - Start: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🧪 Test Commands (After Fix)

```powershell
# Test new endpoints
Invoke-RestMethod -Uri "https://leadnest-backend-2.onrender.com/debug-info"

# Test registration
Invoke-RestMethod -Uri "https://leadnest-backend-2.onrender.com/auth/register" -Method POST -ContentType "application/json" -Body '{"email":"test@example.com","password":"testpass123"}'

# Check all available endpoints
Invoke-RestMethod -Uri "https://leadnest-backend-2.onrender.com/openapi.json"
```

## 📈 Expected Results After Fix

- **debug-info endpoint:** Shows version 1.0.3-debug
- **test-deploy endpoint:** Shows current timestamp
- **auth/register endpoint:** Returns user data or validation error (not 404)
- **OpenAPI spec:** Shows 10+ endpoints instead of 3

**This should fix the deployment and enable full registration testing!**
