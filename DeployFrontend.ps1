# LeadNest Frontend Deployment Script
# Updates environment variables and triggers Vercel deployment

Write-Host "=== LEADNEST FRONTEND DEPLOYMENT ===" -ForegroundColor Green
Write-Host "Date: $(Get-Date)" -ForegroundColor Yellow

# Step 1: Verify environment variables
Write-Host "`n1. VERIFYING ENVIRONMENT VARIABLES" -ForegroundColor Cyan

$envFile = "frontend\.env.production"
if (Test-Path $envFile) {
    Write-Host "✅ Found production environment file" -ForegroundColor Green
    Get-Content $envFile | Write-Host -ForegroundColor Gray
} else {
    Write-Host "❌ Production environment file not found" -ForegroundColor Red
    exit 1
}

# Step 2: Check if Vercel CLI is available
Write-Host "`n2. CHECKING VERCEL CLI" -ForegroundColor Cyan
try {
    $vercelVersion = vercel --version 2>$null
    if ($vercelVersion) {
        Write-Host "✅ Vercel CLI available: $vercelVersion" -ForegroundColor Green
    } else {
        throw "Vercel CLI not found"
    }
} catch {
    Write-Host "❌ Vercel CLI not found. Install with: npm install -g vercel" -ForegroundColor Red
    Write-Host "   Alternative: Deploy manually via Vercel dashboard" -ForegroundColor Yellow
}

# Step 3: Build frontend locally to verify
Write-Host "`n3. TESTING LOCAL BUILD" -ForegroundColor Cyan
try {
    Set-Location "frontend"
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    # Test build
    Write-Host "Building frontend..." -ForegroundColor Yellow
    $env:VITE_API_BASE_URL = "https://api.useleadnest.com/api"
    $env:VITE_ENV_NAME = "PROD"  
    $env:VITE_CALENDLY_URL = "https://calendly.com/leadnest-demo"
    
    npm run build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend build successful" -ForegroundColor Green
    } else {
        throw "Build failed"
    }
} catch {
    Write-Host "❌ Frontend build failed: $($_.Exception.Message)" -ForegroundColor Red
    Set-Location ".."
    exit 1
} finally {
    Set-Location ".."
}

# Step 4: Deployment instructions
Write-Host "`n4. DEPLOYMENT OPTIONS" -ForegroundColor Cyan

Write-Host "`n📋 OPTION A: Vercel CLI Deployment (Recommended)" -ForegroundColor Yellow
Write-Host "cd frontend" -ForegroundColor Gray
Write-Host "vercel --prod" -ForegroundColor Gray

Write-Host "`n📋 OPTION B: Manual Vercel Dashboard Deployment" -ForegroundColor Yellow
Write-Host "1. Go to vercel.com dashboard" -ForegroundColor Gray
Write-Host "2. Find your LeadNest project" -ForegroundColor Gray
Write-Host "3. Go to Settings > Environment Variables" -ForegroundColor Gray
Write-Host "4. Set these variables for Production:" -ForegroundColor Gray
Write-Host "   VITE_API_BASE_URL = https://api.useleadnest.com/api" -ForegroundColor Gray
Write-Host "   VITE_ENV_NAME = PROD" -ForegroundColor Gray
Write-Host "   VITE_CALENDLY_URL = https://calendly.com/leadnest-demo" -ForegroundColor Gray
Write-Host "5. Go to Deployments tab and click 'Redeploy'" -ForegroundColor Gray

# Step 5: Verification checklist
Write-Host "`n5. POST-DEPLOYMENT VERIFICATION" -ForegroundColor Cyan
Write-Host "After deployment, verify these items:" -ForegroundColor Yellow
Write-Host "✅ Homepage loads at https://useleadnest.com" -ForegroundColor Gray
Write-Host "✅ 'Book a Demo' button opens Calendly in new tab" -ForegroundColor Gray  
Write-Host "✅ 'Get Started' button goes to signup page" -ForegroundColor Gray
Write-Host "✅ Login/signup forms connect to API" -ForegroundColor Gray
Write-Host "✅ Hero message shows '24/7 AI Receptionist' copy" -ForegroundColor Gray
Write-Host "✅ Founders' discount messaging visible" -ForegroundColor Gray

Write-Host "`n🚀 FRONTEND READY FOR DEPLOYMENT!" -ForegroundColor Green
Write-Host "Choose Option A or B above to deploy to production" -ForegroundColor Yellow

# Additional verification
Write-Host "`nQUICK API TEST" -ForegroundColor Cyan
try {
    $healthCheck = Invoke-RestMethod -Uri "https://api.useleadnest.com/healthz" -TimeoutSec 10
    Write-Host "SUCCESS: API is healthy - $($healthCheck.status)" -ForegroundColor Green
} catch {
    Write-Host "WARNING: API health check failed - verify backend is running" -ForegroundColor Red
}
