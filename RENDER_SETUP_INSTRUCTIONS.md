# 🚀 Render Dashboard Configuration - URGENT SETUP REQUIRED

## ⚠️ CRITICAL: Manual Configuration Needed

The LeadNest backend code is ready and pushed to GitHub, but Render needs manual configuration to deploy correctly. Follow these exact steps:

---

## 📋 Step-by-Step Instructions

### STEP 1: Access Render Dashboard
1. Go to https://render.com/dashboard
2. Find the service named **"leadnest-backend"**
3. Click on it to open the service details

### STEP 2: Go to Settings
1. In the service page, click the **"Settings"** tab
2. You should see various configuration sections

### STEP 3: Configure Build & Deploy Settings

#### A. Root Directory
- Find the **"Root Directory"** field
- Set it to: `backend-flask`
- ✅ This tells Render where our Flask app lives

#### B. Build Command  
- Find the **"Build Command"** field
- Set it to: `pip install -r requirements.txt`
- ✅ This installs our Python dependencies

#### C. Start Command (MOST IMPORTANT)
- Find the **"Start Command"** field  
- **Replace whatever is there** with: `gunicorn app.api:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
- ✅ This is the critical fix - it tells Render how to run our app

### STEP 4: Clear Cache & Deploy
1. Scroll down and click **"Clear build cache"** button
2. Then click **"Deploy latest commit"** button
3. Wait for the build to complete (5-10 minutes)

### STEP 5: Verify Environment Variables
1. Click the **"Environment"** tab
2. Make sure these variables are set:
   - `DATABASE_URL` (should be auto-populated by Render Postgres)
   - `JWT_SECRET` 
   - `CORS_ORIGINS`
   - `PUBLIC_BASE_URL`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN` 
   - `TWILIO_FROM`

---

## 🎯 Expected Results

After completing these steps:

### Build Should Succeed
- No psycopg2 errors (we fixed this)
- All dependencies install cleanly
- Build completes in ~3-5 minutes

### App Should Start
- Gunicorn starts successfully 
- All endpoints become available
- Health checks return 200 OK

### Test These URLs (should work after deploy):
- ✅ https://api.useleadnest.com/healthz
- ✅ https://api.useleadnest.com/readyz  
- ✅ https://api.useleadnest.com/api/deployment-info
- ✅ https://api.useleadnest.com/api/twilio/debug

---

## 🚨 If Build Fails

### Common Issues & Fixes:

**❌ "No module named 'app'"**
- Fix: Make sure Root Directory is set to `backend-flask`

**❌ "psycopg2 compilation error"**  
- Fix: Already solved - we use psycopg2-binary now

**❌ "App failed to start"**
- Fix: Make sure Start Command is exactly: `gunicorn app.api:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`

**❌ "Port binding failed"**
- Fix: Start command must include `--bind 0.0.0.0:$PORT`

---

## ✅ Success Confirmation

Once deployed successfully, run this test:

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri "https://api.useleadnest.com/healthz" -UseBasicParsing
```

**Expected response:** Status 200 with `{"status":"healthy"}`

**If you get this response, the deployment is SUCCESSFUL! 🎉**

---

## 📞 Final Steps After Success

1. **Database Migration**: In Render Shell, run:
   ```bash
   export FLASK_APP=app.api:app
   flask db upgrade
   ```

2. **Twilio Webhook**: Update webhook URL to:
   `https://api.useleadnest.com/api/twilio/inbound`

3. **Full Verification**: Run our verification script:
   ```powershell
   .\render-deploy-verify.ps1
   ```

---

## 🎯 Timeline

- Configuration: **2 minutes**
- Build & Deploy: **5-8 minutes**  
- Testing: **1 minute**
- **Total: ~10 minutes to go live**

---

**The code is 100% ready. Only this Render configuration is needed to launch! 🚀**
