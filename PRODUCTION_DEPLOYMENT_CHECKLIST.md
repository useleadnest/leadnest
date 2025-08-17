# 🔐 LeadNest Production Deployment Checklist

## ✅ Current Status
- [x] Git history cleaned and secrets purged
- [x] Clean repository pushed to GitHub  
- [x] render.yaml configuration ready
- [x] Production verification script created

## 🚨 IMMEDIATE ACTION REQUIRED

### 1. Secret Rotation (Do This First!)

#### OpenAI
- [ ] Go to https://platform.openai.com/api-keys
- [ ] Create new API key → **Copy immediately**
- [ ] Delete old key: `sk-proj-3dqSSGubvE_PHCcZotqy30r...`

#### Stripe  
- [ ] Go to https://dashboard.stripe.com/apikeys
- [ ] Create new Secret Key → **Copy immediately**
- [ ] Delete old key: `sk_live_REDACTED...`

#### Twilio
- [ ] Go to https://console.twilio.com/us1/develop/api-keys/manage
- [ ] Create new Auth Token → **Copy immediately**
- [ ] Delete old token after updating services

#### Database
- [ ] Render Dashboard → Database → Create new user/password
- [ ] **Copy new DATABASE_URL immediately**

#### JWT Secret (Generated)
```
Use this new JWT secret: [Generated from secrets.token_urlsafe(64)]
```

### 2. Render Environment Variables

Go to Render Dashboard → leadnest-api → Environment:

**Add/Update these variables:**
```
DATABASE_URL=postgresql+psycopg2://NEWUSER:NEWPASS@HOST:5432/leadnest?sslmode=require
JWT_SECRET=[NEW_JWT_SECRET_FROM_ABOVE]
CORS_ORIGINS=https://useleadnest.com,https://*.vercel.app
PUBLIC_BASE_URL=https://leadnest-bulletproof.onrender.com
TWILIO_ACCOUNT_SID=[YOUR_TWILIO_SID]
TWILIO_AUTH_TOKEN=[NEW_TWILIO_TOKEN]
TWILIO_FROM=[YOUR_TWILIO_PHONE]
OPENAI_API_KEY=[NEW_OPENAI_KEY]
STRIPE_SECRET_KEY=[NEW_STRIPE_KEY]
LOG_LEVEL=INFO
PORT=10000
```

**For leadnest-worker service, add same variables**

### 3. Vercel Frontend Environment

Go to Vercel → Settings → Environment Variables:
```
VITE_API_BASE_URL=https://leadnest-bulletproof.onrender.com
VITE_PUBLIC_APP_NAME=LeadNest
VITE_ENV_NAME=PROD
```

### 4. Twilio Webhook Configuration

In Twilio Console → Phone Numbers → Your Number → Messaging:
```
Webhook URL: https://leadnest-bulletproof.onrender.com/twilio/inbound
HTTP Method: POST
```

### 5. Deploy & Test

#### Deploy
- [ ] Git push triggers Render auto-deploy
- [ ] Wait for deployment to complete
- [ ] Run database migration: `flask db upgrade` in Render Shell

#### Verify
```powershell
.\ProductionVerify.ps1 -BaseUrl "https://leadnest-bulletproof.onrender.com"
```

Expected results:
- [ ] ✅ /healthz → 200
- [ ] ✅ /readyz → 200  
- [ ] ✅ /auth/login returns JWT
- [ ] ✅ /leads returns data
- [ ] ✅ /twilio/send responds (503 OK if not configured)
- [ ] ✅ /twilio/inbound responds with TwiML
- [ ] ✅ /openapi.json available

### 6. Final Production Setup

- [ ] Enable Render database backups
- [ ] Configure auto-scaling if needed
- [ ] Monitor logs for first 24 hours
- [ ] Test Stripe webhooks if applicable
- [ ] Verify Twilio SMS flow end-to-end

### 7. Security Confirmation

- [ ] All old secrets rotated and deleted
- [ ] No secrets in git history (verified by successful push)
- [ ] All environment variables stored securely in Render/Vercel
- [ ] HTTPS enforced on all endpoints
- [ ] CORS properly configured

## 🎯 Success Criteria

✅ **LeadNest is production-ready when:**
- All secrets rotated and old ones deleted
- All services deployed and health checks passing
- Twilio SMS integration working
- Frontend connects to API successfully
- Database migrations applied
- No security vulnerabilities remain

## 🚨 Remember
- **NEVER commit the SECURE_ENV_TEMPLATE.md file**  
- **Delete local .env files after deployment**
- **Monitor your API quotas/usage for the first week**

---

**Next Step:** Start with secret rotation, then deploy! 🚀
