# 🖼️ RENDER DASHBOARD VISUAL GUIDE

## Where to Find Each Setting

```
🌐 Render Dashboard (render.com/dashboard)
  └── 📁 leadnest-backend (click this service)
      └── ⚙️ Settings Tab (click this tab)
          └── 🔧 Build & Deploy Section
              ├── 📂 Root Directory: "backend-flask"
              ├── 🔨 Build Command: "pip install -r requirements.txt"  
              └── ▶️ Start Command: "gunicorn app.api:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120"
          
          └── 🧹 Advanced Section (scroll down)
              └── 🗑️ "Clear build cache" (click this button)
              └── 🚀 "Deploy latest commit" (click this button)
```

## Screenshot Guide

### 1. Dashboard View
```
[Services List]
┌─────────────────────────┐
│ 🔍 Search services...   │
├─────────────────────────┤
│ 📊 leadnest-backend     │ ← CLICK THIS
│ 🌐 Web Service          │
│ 🟢 Deploy succeeded     │
└─────────────────────────┘
```

### 2. Service Settings View  
```
[Service: leadnest-backend]
┌─────┬─────────┬────────┬─────────┐
│ 📊  │ ⚙️      │ 🌍     │ 📊      │
│ Overview│Settings│Environment│Events│
└─────┴─────────┴────────┴─────────┘
              ↑ CLICK HERE

[Settings Content - Scroll to find:]
📂 Root Directory: [backend-flask        ] 
🔨 Build Command:  [pip install -r requirements.txt]
▶️ Start Command:  [gunicorn app.api:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120]

[Scroll down for:]
🗑️ [Clear build cache]  🚀 [Deploy latest commit]
```

### 3. Build Logs (after clicking deploy)
```
[Build Output - Should show:]
✅ Installing dependencies...
✅ pip install -r requirements.txt  
✅ psycopg[binary]==3.2.3 installed successfully
✅ Build completed successfully

[Deploy Output - Should show:]
✅ Starting with: gunicorn app.api:app --bind 0.0.0.0:10000 --workers 2...
✅ Application started successfully
✅ Health check passed
```

## 🎯 Visual Success Indicators

### ✅ GOOD - Build Logs
```
Installing dependencies from requirements.txt...
✅ psycopg[binary]==3.2.3
✅ flask==3.0.3  
✅ gunicorn==22.0.0
Build completed in 3m 42s
```

### ✅ GOOD - Start Logs  
```
Starting command: gunicorn app.api:app --bind 0.0.0.0:10000...
[INFO] Starting gunicorn 22.0.0
[INFO] Listening at: http://0.0.0.0:10000
[INFO] Application started successfully
```

### ❌ BAD - Error Examples
```
❌ ModuleNotFoundError: No module named 'app'
   → Fix: Set Root Directory to "backend-flask"

❌ Error: Could not find application 'wsgi:app'  
   → Fix: Set Start Command to "gunicorn app.api:app..."

❌ psycopg2 compilation failed
   → Fix: Switched to psycopg[binary]==3.2.3 ✅

❌ ModuleNotFoundError: No module named 'psycopg2'
   → Fix: Updated settings.py to force psycopg3 ✅
```

---

## 🎯 FINAL TEST

After successful deploy, this URL should work:
**https://api.useleadnest.com/healthz**

**Expected Response:**
```json
{"status":"healthy"}
```

**Status Code: 200 OK**

---

## ✅ **DEPLOYMENT SUCCESSFUL!**

**LeadNest is now LIVE at https://api.useleadnest.com! 🎉🚀**

### **Next Steps:**
1. **Configure Twilio webhook**: `https://api.useleadnest.com/api/twilio/inbound`
2. **Configure Stripe webhook**: `https://api.useleadnest.com/api/stripe/webhook`  
3. **Update frontend**: `API_BASE_URL = 'https://api.useleadnest.com'`
4. **Set up monitoring**: See `monitoring-setup.md`

**Ready for customers! 🚀**
