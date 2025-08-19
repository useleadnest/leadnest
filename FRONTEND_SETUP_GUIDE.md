# 🔧 FRONTEND ENVIRONMENT SETUP GUIDE

## 🚨 CRITICAL: Vite vs CRA Environment Variables

**Our frontend uses Create React App (CRA), NOT Vite!**

### ✅ CORRECT Environment Variable Format:
```bash
REACT_APP_API_BASE_URL=https://api.useleadnest.com/api
REACT_APP_PUBLIC_APP_NAME=LeadNest
REACT_APP_CALENDLY_URL=https://calendly.com/leadnest-demo
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY_HERE
REACT_APP_ENV_NAME=production
REACT_APP_SENTRY_DSN=
REACT_APP_SENTRY_ENVIRONMENT=production
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_CHAT_SUPPORT=false
```

### ❌ WRONG (would break the app):
```bash
VITE_API_BASE_URL=...  # ← CRA ignores this!
```

---

## 📋 VERCEL DEPLOYMENT STEPS

### 1. Set Environment Variables in Vercel

Go to **Vercel Dashboard → Project → Settings → Environment Variables**

Add these for **Production**:

```
REACT_APP_API_BASE_URL = https://api.useleadnest.com/api
REACT_APP_PUBLIC_APP_NAME = LeadNest  
REACT_APP_CALENDLY_URL = https://calendly.com/leadnest-demo
REACT_APP_STRIPE_PUBLISHABLE_KEY = pk_live_YOUR_ACTUAL_KEY
REACT_APP_ENV_NAME = production
REACT_APP_ENABLE_ANALYTICS = true
REACT_APP_ENABLE_CHAT_SUPPORT = false
```

### 2. Build Configuration

**Vercel will auto-detect Create React App and use:**
- Build Command: `npm run build`
- Output Directory: `build/`
- Install Command: `npm install`

**No manual configuration needed!**

### 3. Deploy Settings

✅ **Framework Preset**: Create React App  
✅ **Root Directory**: `frontend/` (if monorepo)  
✅ **Node.js Version**: 18.x or 20.x  

### 4. SPA Routing Configuration

Our `vercel.json` handles React Router deep links:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ],
  "cleanUrls": true
}
```

---

## 🧪 VERIFICATION CHECKLIST

### After Deploy, Test:

1. **Site loads**: https://useleadnest.com
2. **No console errors**: Open DevTools → Console
3. **API calls work**: Check Network tab for `/api/` requests
4. **Deep links work**: Try https://useleadnest.com/dashboard directly
5. **Static assets load**: All CSS/JS files return 200

### Quick Browser Test:
```javascript
// In DevTools console:
console.log('API Base:', process.env.REACT_APP_API_BASE_URL);
// Should show: "https://api.useleadnest.com/api"
```

---

## 🔍 TROUBLESHOOTING

### ❌ "Blank page" or "import.meta.env is undefined"
**Cause**: Using Vite syntax in CRA  
**Fix**: All env vars must start with `REACT_APP_` and use `process.env.`

### ❌ "404 on deep links" (e.g., /dashboard)
**Cause**: Missing SPA routing config  
**Fix**: Ensure `vercel.json` has rewrites rule ✅

### ❌ "API calls fail" / "CORS errors"
**Cause**: Wrong API base URL  
**Fix**: Verify `REACT_APP_API_BASE_URL=https://api.useleadnest.com/api` (with `/api`)

### ❌ "Build fails with memory error"
**Cause**: Large build  
**Fix**: In Vercel settings, increase Node.js memory limit

---

## 📊 BUILD STATS

**Expected build output:**
```
Creating an optimized production build...
Compiled successfully.

File sizes after gzip:
  47.2 kB  build/static/js/main.abc123.js
  15.8 kB  build/static/css/main.def456.css
```

**Deploy time:** ~2-3 minutes  
**Bundle size:** ~50-60 kB (compressed)

---

## ✅ PRODUCTION READY

Once all environment variables are set and the site deploys without errors:

🎉 **Frontend is live at https://useleadnest.com**  
🎉 **API calls hit https://api.useleadnest.com/api**  
🎉 **Ready for customer traffic!**

---

## 🔗 NEXT STEPS

1. **Test user registration flow**
2. **Verify Stripe checkout works**  
3. **Test SMS functionality**
4. **Set up monitoring/analytics**
5. **Add custom domain SSL (if needed)**

**Frontend deployment complete!** 🚀
