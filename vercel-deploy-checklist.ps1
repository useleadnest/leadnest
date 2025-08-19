# PowerShell encoding fix
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "VERCEL DEPLOYMENT CHECKLIST" -ForegroundColor Cyan

Write-Host "`n1. ENVIRONMENT VARIABLES SETUP" -ForegroundColor Yellow
Write-Host "Go to Vercel Dashboard -> Project Settings -> Environment Variables"
Write-Host "Add these for PRODUCTION:" -ForegroundColor Green
Write-Host ""
Write-Host "REACT_APP_API_BASE_URL = https://api.useleadnest.com/api"
Write-Host "REACT_APP_PUBLIC_APP_NAME = LeadNest"
Write-Host "REACT_APP_CALENDLY_URL = https://calendly.com/leadnest-demo"
Write-Host "REACT_APP_STRIPE_PUBLISHABLE_KEY = pk_live_YOUR_KEY_HERE"
Write-Host "REACT_APP_ENV_NAME = production"
Write-Host "REACT_APP_ENABLE_ANALYTICS = true" 
Write-Host "REACT_APP_ENABLE_CHAT_SUPPORT = false"
Write-Host ""

Write-Host "2. DEPLOYMENT SETTINGS" -ForegroundColor Yellow
Write-Host "Framework Preset: Create React App (auto-detected)" -ForegroundColor Green
Write-Host "Build Command: npm run build (auto-detected)" -ForegroundColor Green
Write-Host "Output Directory: build (auto-detected)" -ForegroundColor Green
Write-Host "Install Command: npm install (auto-detected)" -ForegroundColor Green
Write-Host ""

Write-Host "3. DEPLOY STEPS" -ForegroundColor Yellow
Write-Host "1. Set environment variables in Vercel dashboard" -ForegroundColor Green
Write-Host "2. Go to Deployments tab" -ForegroundColor Green
Write-Host "3. Click '...' menu on latest deployment" -ForegroundColor Green
Write-Host "4. Select 'Redeploy'" -ForegroundColor Green
Write-Host "5. UNCHECK 'Use existing Build Cache'" -ForegroundColor Green
Write-Host "6. Click 'Redeploy' and wait 2-3 minutes" -ForegroundColor Green
Write-Host ""

Write-Host "4. POST-DEPLOYMENT VERIFICATION" -ForegroundColor Yellow
Write-Host "After deployment completes, test:" -ForegroundColor Green
Write-Host ""
Write-Host "Site loads: https://useleadnest.com"
Write-Host "Console clean: Open DevTools -> Console (no errors)"
Write-Host "Environment vars: Run in console:"
Write-Host "  console.log('API:', process.env.REACT_APP_API_BASE_URL)"
Write-Host "API calls work: Check Network tab for /api/ requests"
Write-Host "Deep links work: Visit https://useleadnest.com/dashboard directly"
Write-Host "Static assets: All CSS/JS files return 200 OK"
Write-Host ""

Write-Host "5. FUNCTIONAL TESTS" -ForegroundColor Yellow
Write-Host "Test complete user flow:" -ForegroundColor Green
Write-Host "- Home renders with no console errors"
Write-Host "- Login/Signup flow works (JWT stored, /me endpoint OK)"
Write-Host "- Stripe Checkout opens and webhooks succeed" 
Write-Host "- Twilio inbound test reaches /api/twilio/inbound"
Write-Host "- 404 route deep link resolves to app"
Write-Host ""

Write-Host "6. ROLLBACK PLAN" -ForegroundColor Yellow
Write-Host "If issues occur:" -ForegroundColor Red
Write-Host "Vercel -> Deployments -> Promote previous successful build" -ForegroundColor Red
Write-Host "No DNS changes required - instant rollback!" -ForegroundColor Red
Write-Host ""

Write-Host "DEPLOYMENT READY!" -ForegroundColor Green
Write-Host "Frontend is configured and tested for production deployment" -ForegroundColor Green
