#!/usr/bin/env pwsh

Write-Host "🚨 EMERGENCY LEADNEST DEPLOYMENT FIX" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red

# Test backend health
Write-Host "`n1. Testing Backend Health..." -ForegroundColor Yellow
try {
    $health = (Invoke-WebRequest -Uri "https://leadnest-api-final.onrender.com/health" -UseBasicParsing).Content
    Write-Host "✅ Backend Health: $health" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend Health Failed: $_" -ForegroundColor Red
    exit 1
}

# Test backend auth endpoints
Write-Host "`n2. Testing Backend Auth Endpoints..." -ForegroundColor Yellow
try {
    $authTest = Invoke-WebRequest -Uri "https://leadnest-api-final.onrender.com/auth/me" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Auth endpoints working" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq "Unauthorized") {
        Write-Host "✅ Auth endpoints working (got expected 401)" -ForegroundColor Green
    } else {
        Write-Host "❌ Auth endpoints missing (404)" -ForegroundColor Red
        Write-Host "🔧 SOLUTION: Backend needs redeploy with correct main.py" -ForegroundColor Cyan
    }
}

# Test frontend
Write-Host "`n3. Testing Frontend..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "https://useleadnest.com" -UseBasicParsing
    if ($frontendResponse.Content -match "Loading") {
        Write-Host "⚠️ Frontend stuck on Loading - backend connection issue" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Frontend loading properly" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Frontend not accessible: $_" -ForegroundColor Red
}

Write-Host "`n🚨 CRITICAL ACTIONS NEEDED:" -ForegroundColor Red
Write-Host "1. Go to Render service 'leadnest-api-final'" -ForegroundColor White
Write-Host "2. In Settings, set Start Command to: python -m uvicorn main:app --host 0.0.0.0 --port `$PORT --log-level info" -ForegroundColor White
Write-Host "3. Save and wait for redeploy (2-3 minutes)" -ForegroundColor White
Write-Host "4. Re-run this script to verify" -ForegroundColor White

Write-Host "`n🎯 Expected Results After Fix:" -ForegroundColor Cyan
Write-Host "- Backend /auth/me should return 401 (not 404)" -ForegroundColor White
Write-Host "- Frontend should show login page (not Loading...)" -ForegroundColor White
