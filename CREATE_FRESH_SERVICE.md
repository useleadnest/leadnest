# 🆕 CREATE LEADNEST-API-FINAL - FRESH SERVICE

## 🗑️ STEP 1: Delete Old Service
1. Go to https://render.com/dashboard
2. Find **leadnest-backend-2** service
3. Click on the service
4. Go to **Settings** tab (bottom left)
5. Scroll to **Danger Zone**
6. Click **Delete Service**
7. Type service name to confirm: `leadnest-backend-2`
8. Click **Delete**

## 🆕 STEP 2: Create Fresh Service
1. On dashboard, click **"New +"** → **"Web Service"**
2. Choose **"Build and deploy from a Git repository"**
3. Select **useleadnest/leadnest-backend** repository
4. Click **"Connect"**

## ⚙️ STEP 3: Service Configuration
```
Name: leadnest-api-final
Environment: Python  
Region: Oregon (US West)
Branch: main
Root Directory: (leave blank)
Runtime: Automatic

Build Command: 
pip install --upgrade pip && pip install -r requirements.txt

Start Command:
python -m uvicorn main_perfect:app --host 0.0.0.0 --port $PORT --log-level info

Health Check Path: /health
Auto-Deploy: Yes (should be enabled by default)
```

## 🔐 STEP 4: Environment Variables
**Add these in the Environment tab:**

| Key | Value |
|-----|-------|
| `DATABASE_URL` | (your existing postgres URL) |
| `JWT_SECRET_KEY` | (click "Generate" button) |
| `STRIPE_PUBLISHABLE_KEY` | (your stripe publishable key) |
| `STRIPE_SECRET_KEY` | (your stripe secret key) |
| `STRIPE_WEBHOOK_SECRET` | (your webhook secret) |
| `OPENAI_API_KEY` | (your openai key) |
| `FRONTEND_URL` | https://useleadnest.com |
| `ENVIRONMENT` | production |

## 🚀 STEP 5: Deploy
1. Click **"Create Web Service"**
2. Wait for build and deployment (2-3 minutes)
3. Service will be available at: `https://leadnest-api-final.onrender.com`

---

## 🧪 STEP 6: Immediate Testing (After Deployment)

### Test Basic Endpoints
```powershell
# Root endpoint - should show version 1.0.6-PERFECT
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/"

# Health check
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/health"

# Debug info
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/debug-info"

# Status page
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/status"
```

### Test Auth Endpoints
```powershell
$testUser = @{
    email = "test@example.com"
    password = "testpass123"
} | ConvertTo-Json

# Test registration
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/auth/register" -Method POST -ContentType "application/json" -Body $testUser

# Test login
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/auth/login" -Method POST -ContentType "application/json" -Body $testUser
```

---

## ✅ EXPECTED RESULTS

**Root endpoint should return:**
```json
{
  "message": "LeadNest API is running!",
  "version": "1.0.6-PERFECT",
  "status": "active",
  "timestamp": "2024-...",
  "deployment": "SUCCESS",
  "environment": "production",
  "database_available": true
}
```

**Status endpoint should show:**
```json
{
  "service": "leadnest-api",
  "version": "1.0.6-PERFECT",
  "status": "operational",
  "features": {
    "auth": true,
    "database": true,
    "cors": true,
    "health_check": true
  },
  "endpoints": {
    "root": "/",
    "health": "/health",
    "auth_register": "/auth/register",
    "auth_login": "/auth/login",
    "auth_me": "/auth/me",
    "debug": "/debug-info",
    "status": "/status"
  }
}
```

## 🎯 SUCCESS INDICATORS
- ✅ All endpoints return 200 status (not 404)
- ✅ Version shows "1.0.6-PERFECT"
- ✅ Auth endpoints accept POST requests
- ✅ OpenAPI docs show 7+ endpoints
- ✅ Ready for frontend integration testing

---

## 🔄 STEP 7: Update Frontend (After Backend Success)

Once backend is confirmed working:

```powershell
# Update frontend API URL
# Edit frontend/.env.production:
VITE_API_URL=https://leadnest-api-final.onrender.com

# Rebuild and redeploy frontend
cd frontend
npm run build
npx vercel --prod
```

**This fresh service approach will give us a clean, working deployment in under 10 minutes!**
