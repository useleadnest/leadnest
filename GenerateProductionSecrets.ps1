param(
    [string]$ApiDomain = "your-api-subdomain.onrender.com",
    [string]$FrontendDomain = "your-frontend.vercel.app"
)

Write-Host "=== LeadNest Production Secrets Generator ===" -ForegroundColor Yellow

# Generate JWT Secret
$jwtSecret = [System.Web.Security.Membership]::GeneratePassword(64, 0)
Write-Host "`nJWT_SECRET=$jwtSecret" -ForegroundColor Green

# Generate Database Password
$dbPassword = [System.Web.Security.Membership]::GeneratePassword(24, 8)
Write-Host "DB_PASSWORD=$dbPassword" -ForegroundColor Green

Write-Host "`n=== RENDER WEB SERVICE ENV VARS ===" -ForegroundColor Cyan
Write-Host "JWT_SECRET=$jwtSecret"
Write-Host "OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY_HERE"
Write-Host "STRIPE_PUBLISHABLE_KEY=pk_live_REDACTED"
Write-Host "STRIPE_SECRET_KEY=sk_live_REDACTED"
Write-Host "STRIPE_WEBHOOK_SECRET=whsec_REDACTED"
Write-Host "TWILIO_ACCOUNT_SID=YOUR_TWILIO_ACCOUNT_SID"
Write-Host "TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN"
Write-Host "TWILIO_PHONE_NUMBER=+1XXXXXXXXXX"
Write-Host "DATABASE_URL=postgresql://leadnest_user:$dbPassword@dpg-XXXXX-a.oregon-postgres.render.com/leadnest_db"
Write-Host "REDIS_URL=redis://red-XXXXX:6379"
Write-Host "FLASK_ENV=production"
Write-Host "FLASK_DEBUG=0"
Write-Host "PUBLIC_BASE_URL=https://$ApiDomain"
Write-Host "CORS_ORIGINS=https://$FrontendDomain"
Write-Host "LOG_LEVEL=INFO"

Write-Host "`n=== RENDER WORKER SERVICE ENV VARS ===" -ForegroundColor Cyan
Write-Host "JWT_SECRET=$jwtSecret"
Write-Host "DATABASE_URL=postgresql://leadnest_user:$dbPassword@dpg-XXXXX-a.oregon-postgres.render.com/leadnest_db"
Write-Host "REDIS_URL=redis://red-XXXXX:6379"
Write-Host "TWILIO_ACCOUNT_SID=YOUR_TWILIO_ACCOUNT_SID"
Write-Host "TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN"
Write-Host "TWILIO_PHONE_NUMBER=+1XXXXXXXXXX"

Write-Host "`n=== VERCEL FRONTEND ENV VARS ===" -ForegroundColor Cyan
Write-Host "VITE_API_BASE_URL=https://$ApiDomain"
Write-Host "VITE_ENV_NAME=PROD"
Write-Host "FRONTEND_PUBLIC_URL=https://$FrontendDomain"

Write-Host "`n=== TWILIO WEBHOOK URL ===" -ForegroundColor Cyan
Write-Host "Set inbound webhook to: https://$ApiDomain/twilio/inbound"

Write-Host "`n=== SMOKE TEST COMMANDS ===" -ForegroundColor Cyan
Write-Host "# Health Check"
Write-Host "curl -X GET https://$ApiDomain/healthz"
Write-Host ""
Write-Host "# Login Test"
Write-Host "curl -X POST https://$ApiDomain/auth/login \"
Write-Host "  -H `"Content-Type: application/json`" \"
Write-Host "  -d '{`"email`":`"admin@leadnest.com`",`"password`":`"YOUR_ADMIN_PASSWORD`"}'"
Write-Host ""
Write-Host "# Twilio Inbound Test (using --data-urlencode to handle &)"
Write-Host "curl -X POST https://$ApiDomain/twilio/inbound \"
Write-Host "  -H `"Content-Type: application/x-www-form-urlencoded`" \"
Write-Host "  --data-urlencode `"From=+1234567890`" \"
Write-Host "  --data-urlencode `"Body=TEST`" \"
Write-Host "  --data-urlencode `"MessageSid=SM123456`""

Write-Host "`n=== PRODUCTION VERIFY SCRIPT ===" -ForegroundColor Cyan
Write-Host ".\ProductionVerify.ps1 -BaseUrl `"https://$ApiDomain`" -Email `"admin@leadnest.com`" -Password `"YOUR_ADMIN_PASSWORD`""
