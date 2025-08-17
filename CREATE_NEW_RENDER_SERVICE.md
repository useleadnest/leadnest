# 🆕 CREATE NEW RENDER SERVICE - LEADNEST-API-V3

## Step-by-Step Instructions

### 1. Create New Service
1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Connect to GitHub: **useleadnest/leadnest-backend**
5. Click **"Connect"**

### 2. Service Configuration
```
Name: leadnest-api-v3
Environment: Python
Region: Oregon (US West)
Branch: main
Root Directory: (leave blank)
Runtime: Automatic
Build Command: pip install -r requirements.txt
Start Command: python -m uvicorn main_working:app --host 0.0.0.0 --port $PORT
```

### 3. Environment Variables
Add these in the Environment tab:
```
DATABASE_URL = <your_postgres_url>
JWT_SECRET_KEY = <auto_generate>
STRIPE_PUBLISHABLE_KEY = <your_stripe_key>
STRIPE_SECRET_KEY = <your_stripe_secret>  
STRIPE_WEBHOOK_SECRET = <your_webhook_secret>
OPENAI_API_KEY = <your_openai_key>
FRONTEND_URL = https://useleadnest.com
ENVIRONMENT = production
```

### 4. Advanced Settings
```
Auto-Deploy: Yes
Instance Type: Free
Health Check Path: /health
```

### 5. Deploy
Click **"Create Web Service"**

---

## 🧪 Testing the New Service

Once deployed, test these endpoints:

### Basic Endpoints
```bash
# Root endpoint
curl https://leadnest-api-v3.onrender.com/

# Health check  
curl https://leadnest-api-v3.onrender.com/health

# Debug info
curl https://leadnest-api-v3.onrender.com/debug-info
```

### Auth Endpoints (PowerShell)
```powershell
# Test registration
$body = @{
    email = "test@example.com"
    password = "testpass123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://leadnest-api-v3.onrender.com/auth/register" -Method POST -ContentType "application/json" -Body $body

# Test login
Invoke-RestMethod -Uri "https://leadnest-api-v3.onrender.com/auth/login" -Method POST -ContentType "application/json" -Body $body
```

---

## 🔄 Update Frontend

Once the new service is working, update frontend config:

```bash
# Edit frontend/.env.production
VITE_API_URL=https://leadnest-api-v3.onrender.com
```

Then redeploy frontend:
```bash
cd frontend
npm run build
npx vercel --prod
```

---

## ✅ Expected Results

**New service should show:**
- ✅ Version: "1.0.5-WORKING"
- ✅ Registration endpoint returning user data
- ✅ Login endpoint returning token
- ✅ All endpoints documented in /docs
- ✅ No 404 errors

**Frontend integration:**
- ✅ Registration form submits successfully
- ✅ User gets success/error feedback
- ✅ Auto-redirect to dashboard

---

## 🎯 Next Steps After New Service

1. **Verify all endpoints work**
2. **Test registration flow end-to-end**
3. **Update DNS if needed**
4. **Delete old leadnest-backend-2 service**
5. **Complete E2E testing**

This fresh service should solve all deployment issues!
