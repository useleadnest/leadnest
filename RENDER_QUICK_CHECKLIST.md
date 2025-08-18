# ✅ RENDER SETUP CHECKLIST - 5 MINUTES TO LAUNCH

## 🎯 Goal: Configure Render to deploy LeadNest correctly

**Current Status:** Code is ready ✅ | Render needs configuration ⏳

---

## 📝 CHECKLIST (Do in order)

### □ 1. Open Render Dashboard
- Go to: https://render.com/dashboard
- Find: **leadnest-backend** service
- Click to open

### □ 2. Go to Settings Tab
- Click **"Settings"** tab
- Look for Build & Deploy section

### □ 3. Set Root Directory
- Field: **Root Directory**
- Value: `backend-flask`

### □ 4. Set Build Command
- Field: **Build Command** 
- Value: `pip install -r requirements.txt`

### □ 5. Set Start Command (CRITICAL!)
- Field: **Start Command**
- Value: `gunicorn app.api:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
- ⚠️ **This is the main fix!**

### □ 6. Clear Cache & Deploy
- Click: **"Clear build cache"**
- Click: **"Deploy latest commit"** 
- Wait: 5-10 minutes for completion

### □ 7. Test Success
- Test URL: https://api.useleadnest.com/healthz
- Expected: `{"status":"healthy"}`
- ✅ **SUCCESS = READY FOR LAUNCH!**

---

## 🚨 CRITICAL SETTINGS SUMMARY

```
Root Directory: backend-flask
Build Command: pip install -r requirements.txt  
Start Command: gunicorn app.api:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

**That's it! The code is already perfect - just need these 3 settings.**

---

## 📞 VERIFICATION COMMAND

After deploy completes, test with:
```powershell
Invoke-WebRequest -Uri "https://api.useleadnest.com/healthz" -UseBasicParsing
```

**Success = Status 200 + `{"status":"healthy"}`**

---

**ETA: 10 minutes to live production system! 🚀**
