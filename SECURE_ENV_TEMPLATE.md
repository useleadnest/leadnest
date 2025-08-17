# 🔐 SECURE ENVIRONMENT VARIABLES

**⚠️ NEVER COMMIT THESE VALUES - USE ONLY IN RENDER/VERCEL DASHBOARDS**

## Render Backend Service Environment Variables

```bash
# Database (from Render Postgres service)
DATABASE_URL=postgresql+psycopg2://NEWUSER:NEWPASS@HOST:5432/leadnest?sslmode=require

# JWT Secret (generated with secrets.token_urlsafe(64))
JWT_SECRET=YOUR_NEW_64_CHAR_JWT_SECRET_HERE

# CORS Origins (adjust domain as needed)
CORS_ORIGINS=https://useleadnest.com,https://*.vercel.app

# Public API URL (your Render service URL)
PUBLIC_BASE_URL=https://leadnest-bulletproof.onrender.com

# Redis (if using)
REDIS_URL=redis://:password@host:6379/0

# Twilio (NEW rotated values)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=NEW_ROTATED_TOKEN_HERE
TWILIO_FROM=+1XXXXXXXXXX

# OpenAI (NEW rotated key)
OPENAI_API_KEY=sk-NEW_ROTATED_KEY_HERE

# Stripe (NEW rotated keys)
STRIPE_SECRET_KEY=sk_live_REDACTED

# App Config
LOG_LEVEL=INFO
PORT=10000
```

## Vercel Frontend Environment Variables

```bash
# API URL (your Render service URL)
VITE_API_BASE_URL=https://leadnest-bulletproof.onrender.com

# App Config
VITE_PUBLIC_APP_NAME=LeadNest
VITE_ENV_NAME=PROD
```

## 🚨 CRITICAL SECURITY STEPS

1. **Rotate ALL the exposed secrets first** (OpenAI, Stripe, Twilio, DB)
2. **Update Render environment variables** with NEW values
3. **Update Vercel environment variables** with NEW API URL
4. **Test thoroughly** before going live
5. **Delete this file** or move outside repo after use

## Twilio Webhook URL
```
https://leadnest-bulletproof.onrender.com/twilio/inbound
```

Set this in Twilio Console → Phone Numbers → Your Number → Messaging
