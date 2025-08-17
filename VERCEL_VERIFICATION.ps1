# VERCEL DEPLOYMENT VERIFICATION CHECKLIST

Write-Host "🔍 LEADNEST VERCEL DEPLOYMENT VERIFICATION"
Write-Host "==========================================="
Write-Host ""

Write-Host "1. 📋 CHECKING FRONTEND CONFIGURATION..."
Write-Host ""

# Check package.json build script
$packageJson = Get-Content "frontend/package.json" | ConvertFrom-Json
Write-Host "✅ Build Script: $($packageJson.scripts.build)"

# Check environment variables
Write-Host ""
Write-Host "2. 🌍 ENVIRONMENT VARIABLES:"
if (Test-Path "frontend/.env.production") {
    Get-Content "frontend/.env.production" | Where-Object { $_ -match "REACT_APP_API_URL" }
    Write-Host "✅ .env.production file exists"
} else {
    Write-Host "❌ .env.production file missing"
}

Write-Host ""
Write-Host "3. 🏗️ TESTING LOCAL BUILD..."
cd frontend
$env:PATH += ";C:\Program Files\nodejs"
try {
    npm run build 2>&1 | Tee-Object -Variable buildOutput
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Local build successful"
    } else {
        Write-Host "❌ Local build failed"
        Write-Host $buildOutput
    }
} catch {
    Write-Host "❌ Build error: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "4. 🌐 API CONNECTION TEST..."
try {
    $apiTest = Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/health" -TimeoutSec 10
    Write-Host "✅ Backend API responding: $($apiTest.status)"
} catch {
    Write-Host "❌ Backend API issue: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "5. 📝 VERCEL DEPLOYMENT CHECKLIST:"
Write-Host "   □ Check Vercel dashboard for latest build status"
Write-Host "   □ Verify useleadnest.com domain is properly configured"  
Write-Host "   □ Confirm environment variables in Vercel project settings"
Write-Host "   □ Check if REACT_APP_API_URL is set correctly in Vercel"
Write-Host ""

Write-Host "6. 🔗 QUICK LINKS:"
Write-Host "   • Vercel Dashboard: https://vercel.com/dashboard"
Write-Host "   • LeadNest Frontend: https://useleadnest.com"
Write-Host "   • API Health Check: https://leadnest-api-final.onrender.com/health"
Write-Host ""

Write-Host "🚀 NEXT ACTIONS NEEDED:"
Write-Host "1. Open Vercel dashboard and check latest deployment"
Write-Host "2. Verify domain settings for useleadnest.com"
Write-Host "3. Add REACT_APP_API_URL=https://leadnest-api-final.onrender.com to Vercel env vars"
Write-Host "4. Trigger new deployment if needed"
