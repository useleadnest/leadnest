# Render Deployment Configuration for LeadNest

## 🚨 CRITICAL: Manual Render Dashboard Configuration Required

The following settings MUST be configured manually in Render Dashboard → leadnest-backend → Settings:

### Service Settings
- **Service Name**: leadnest-backend
- **Environment**: Python 3
- **Root Directory**: `backend-flask`
- **Runtime**: Python (auto-detected from runtime.txt)

### Build Settings
**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
gunicorn app.api:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

### Critical Files Verified ✅

1. **runtime.txt**: `python-3.11.9`
2. **requirements.txt**: Contains `psycopg2-binary==2.9.9` (no plain psycopg2)
3. **wsgi.py**: Proper Flask app export
4. **app/api.py**: Exports `app` instance for Gunicorn access
5. **app/__init__.py**: ProxyFix enabled for HTTPS/signature validation

### Environment Variables Required

Set these in Render Dashboard → Environment:

#### Core Settings
```
DATABASE_URL=(auto-populated by Render Postgres)
JWT_SECRET=your-production-jwt-secret
CORS_ORIGINS=https://useleadnest.com
PUBLIC_BASE_URL=https://api.useleadnest.com
```

#### Twilio Settings
```
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_FROM=your-twilio-phone
```

#### Stripe Settings (Optional for MVP)
```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
```

#### Frontend URL
```
FRONTEND_URL=https://useleadnest.com
```

### Database Migration

After successful deployment, run in Render Shell:
```bash
export FLASK_APP=app.api:app
flask db upgrade
```

## 🔧 Troubleshooting

### If New Endpoints Not Appearing (404):
1. Clear Build Cache in Render Dashboard
2. Verify Root Directory is `backend-flask`
3. Verify Start Command uses `app.api:app` not `wsgi:app`
4. Click "Deploy Latest Commit"

### If Build Fails:
- Check that requirements.txt has `psycopg2-binary` not `psycopg2`
- Verify runtime.txt has `python-3.11.9`
- Check Build logs for specific errors

### If App Won't Start:
- Verify Start Command: `gunicorn app.api:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
- Check that app/api.py exports `app` instance
- Verify all environment variables are set

### If Twilio Returns 403:
- Verify ProxyFix is enabled in app/__init__.py
- Check TWILIO_AUTH_TOKEN is set correctly
- Webhook URL should be: `https://api.useleadnest.com/api/twilio/inbound`

## ✅ Verification Commands

After deployment, run these to verify:

```powershell
# Quick health check
.\quick-health-check.ps1

# Full verification
.\render-deploy-verify.ps1
```

## 🎯 Expected Endpoints

After successful deployment, these should return 200 OK:
- `GET https://api.useleadnest.com/`
- `GET https://api.useleadnest.com/healthz`
- `GET https://api.useleadnest.com/readyz`
- `GET https://api.useleadnest.com/api/deployment-info`
- `GET https://api.useleadnest.com/api/twilio/debug`

These should return appropriate auth/validation errors (not 404):
- `POST https://api.useleadnest.com/api/twilio/inbound` (403 without signature)
- `POST https://api.useleadnest.com/api/stripe/webhook` (400 without payload)
- `POST https://api.useleadnest.com/api/billing/checkout` (401 without auth)

## 🚀 Go-Live Checklist

- [ ] Root Directory set to `backend-flask`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `gunicorn app.api:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
- [ ] All environment variables set
- [ ] Build succeeds without psycopg2 errors
- [ ] All health endpoints return 200
- [ ] Database migration completed
- [ ] Twilio webhook configured and returns 403 (expected without signature)
- [ ] Stripe endpoints return auth errors (not 404)
