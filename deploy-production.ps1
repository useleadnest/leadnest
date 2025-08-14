# 🚀 LeadNest Production Deployment Script

Write-Host "🚀 Starting LeadNest Production Deployment..." -ForegroundColor Green

# Step 1: Navigate to frontend directory
Write-Host "📁 Navigating to frontend directory..." -ForegroundColor Yellow
Set-Location "c:\Users\mccab\contractornest\frontend"

# Step 2: Set up environment
Write-Host "⚙️ Setting up environment..." -ForegroundColor Yellow
$env:PATH += ";C:\Program Files\nodejs"

# Step 3: Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
& "C:\Program Files\nodejs\npm.cmd" install

# Step 4: Build production version
Write-Host "🔨 Building production version..." -ForegroundColor Yellow
& "C:\Program Files\nodejs\npm.cmd" run build

# Step 5: Check if build was successful
if (Test-Path "build") {
    Write-Host "✅ Build successful! Build folder created." -ForegroundColor Green
} else {
    Write-Host "❌ Build failed! Build folder not found." -ForegroundColor Red
    exit 1
}

# Step 6: Deploy to Vercel
Write-Host "🌐 Deploying to Vercel..." -ForegroundColor Yellow
& "C:\Program Files\nodejs\npx.cmd" vercel --prod

# Step 7: Set custom domain (if needed)
Write-Host "🔗 Setting up custom domain..." -ForegroundColor Yellow
& "C:\Program Files\nodejs\npx.cmd" vercel domains add useleadnest.com

# Step 8: Verification
Write-Host "✅ Deployment commands completed!" -ForegroundColor Green
Write-Host "🌍 Your LeadNest app should be live at: https://useleadnest.com" -ForegroundColor Cyan
Write-Host "📊 API endpoint: https://leadnest-api.onrender.com" -ForegroundColor Cyan

# Step 9: Test URLs
Write-Host "🧪 Testing URLs..." -ForegroundColor Yellow
try {
    $frontendTest = Invoke-WebRequest -Uri "https://useleadnest.com" -Method Head -TimeoutSec 10
    Write-Host "✅ Frontend accessible: $($frontendTest.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "⏳ Frontend not yet accessible (DNS propagation may be pending)" -ForegroundColor Yellow
}

try {
    $apiTest = Invoke-WebRequest -Uri "https://leadnest-api.onrender.com/health" -Method Head -TimeoutSec 10
    Write-Host "✅ API accessible: $($apiTest.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ API not accessible" -ForegroundColor Red
}

Write-Host "🎉 Deployment process complete!" -ForegroundColor Green
