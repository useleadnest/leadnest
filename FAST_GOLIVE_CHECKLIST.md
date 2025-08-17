# 🚀 LEADNEST FAST GO-LIVE CHECKLIST

## ✅ RENDER SERVICES

### Web Service Status
- [ ] **Web service GREEN** (Render dashboard shows "Live")
- [ ] **Health endpoint works**: `curl https://leadnest-api.onrender.com/healthz` → 200 OK

### Database Migration
- [ ] **DB migrated**: Render shell → `flask db upgrade` → SUCCESS
- [ ] **Database connected**: No connection errors in logs

### Background Worker  
- [ ] **Worker service GREEN** (Render dashboard shows "Live")
- [ ] **REDIS_URL set** in worker environment variables
- [ ] **Worker processing jobs**: Check logs for job activity

## ✅ API FUNCTIONALITY

### Authentication
- [ ] **Auth login works**:
```bash
curl -X POST https://leadnest-api.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@leadnest.com","password":"YOUR_PASSWORD"}'
```
Expected: JWT token returned

### Protected Endpoints
- [ ] **Leads endpoint secure**: `/leads` returns 200 with valid token
- [ ] **Leads endpoint protected**: `/leads` returns 401 without token

## ✅ THIRD-PARTY INTEGRATIONS

### Twilio Setup
- [ ] **Twilio creds set** in Render environment:
  - `TWILIO_ACCOUNT_SID` = Your actual SID
  - `TWILIO_AUTH_TOKEN` = Your actual token  
  - `TWILIO_PHONE_NUMBER` = Your actual number
- [ ] **Inbound webhook configured**: `https://leadnest-api.onrender.com/twilio/inbound`

### Test Twilio Integration
- [ ] **Inbound SMS test**:
```bash
curl -X POST https://leadnest-api.onrender.com/twilio/inbound \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "From=+1234567890" \
  --data-urlencode "Body=TEST" \
  --data-urlencode "MessageSid=SM123456"
```
Expected: 200 OK response

## ✅ FRONTEND DEPLOYMENT

### Vercel Configuration
- [ ] **Frontend deployed** to Vercel
- [ ] **VITE_API_BASE_URL** = `https://leadnest-api.onrender.com`
- [ ] **VITE_ENV_NAME** = `PROD`
- [ ] **Custom domain configured** (if applicable)

### CORS Configuration  
- [ ] **CORS allows Vercel domain** in Render env:
  - `CORS_ORIGINS` = `https://leadnest.vercel.app,https://your-domain.com`

## ✅ AUTOMATED TESTING

### Quick Smoke Test
```powershell
.\QuickSmoke.ps1 -ApiDomain "leadnest-api.onrender.com"
```
- [ ] **All tests PASS**
- [ ] **No 404/500 errors**
- [ ] **Response times < 3 seconds**

### Production Verification
```powershell  
.\ProductionVerify.ps1 -ApiDomain "leadnest-api.onrender.com"
```
- [ ] **Health check: PASS**
- [ ] **Auth endpoints: PASS** 
- [ ] **Protected routes: PASS**
- [ ] **Twilio webhook: PASS**

### Render Verification
```powershell
.\RenderVerify.ps1 -ApiDomain "leadnest-api.onrender.com"  
```
- [ ] **Basic connectivity: PASS**
- [ ] **Flask headers: PASS**
- [ ] **CORS headers: PASS**
- [ ] **Response time: < 1000ms**

## ✅ ENVIRONMENT VARIABLES CHECKLIST

### Render Web Service Required Vars
- [ ] `JWT_SECRET` (auto-generated)
- [ ] `DATABASE_URL` (connected to PostgreSQL) 
- [ ] `REDIS_URL` (connected to Redis)
- [ ] `PUBLIC_BASE_URL` = `https://leadnest-api.onrender.com`
- [ ] `CORS_ORIGINS` = `https://leadnest.vercel.app`
- [ ] `FLASK_ENV` = `production`
- [ ] `FLASK_DEBUG` = `0`
- [ ] `LOG_LEVEL` = `INFO`

### Third-Party Service Vars
- [ ] `TWILIO_ACCOUNT_SID` (your actual SID)
- [ ] `TWILIO_AUTH_TOKEN` (your actual token)
- [ ] `TWILIO_PHONE_NUMBER` (your actual number)
- [ ] `OPENAI_API_KEY` (your actual key)
- [ ] `STRIPE_PUBLISHABLE_KEY` (your actual key)
- [ ] `STRIPE_SECRET_KEY` (your actual key)
- [ ] `STRIPE_WEBHOOK_SECRET` (your actual secret)

## ✅ FINAL GO-LIVE VERIFICATION

### End-to-End Test
1. [ ] **Visit frontend** → Loads without errors
2. [ ] **Register/Login** → Works correctly  
3. [ ] **Create lead search** → Returns results
4. [ ] **Export leads** → CSV downloads
5. [ ] **Send SMS** → Twilio integration works
6. [ ] **Receive SMS** → Webhook processes correctly

### Performance Check
- [ ] **Frontend loads** in < 3 seconds
- [ ] **API responses** in < 1 second
- [ ] **Database queries** optimized
- [ ] **No memory leaks** in logs

### Monitoring Setup
- [ ] **Error tracking** configured (Sentry)
- [ ] **Uptime monitoring** active
- [ ] **Log monitoring** in place
- [ ] **Alert notifications** configured

## 🎯 GO-LIVE COMMANDS

```powershell
# Final verification before go-live
.\DiagnoseApi.ps1 -ApiDomain "leadnest-api.onrender.com"
.\RenderVerify.ps1 -ApiDomain "leadnest-api.onrender.com"  
.\ProductionVerify.ps1 -ApiDomain "leadnest-api.onrender.com"

# If all pass - YOU'RE LIVE! 🚀
Write-Host "🎉 LEADNEST IS LIVE AND READY FOR USERS!" -ForegroundColor Green
```

---

## ⚡ EMERGENCY ROLLBACK (If Issues Found)

1. **Render Dashboard** → Service → **Rollback to Previous Deploy**
2. **Vercel Dashboard** → Project → **Rollback to Previous Deploy**  
3. **Update DNS** → Point to maintenance page
4. **Notify users** → Service status page

---

**📋 STATUS**: Complete this checklist before announcing launch!
**🎯 GOAL**: All checkboxes ✅ = Production ready
**⏱️ TIME**: Should complete in 15-20 minutes

---
*Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")*
