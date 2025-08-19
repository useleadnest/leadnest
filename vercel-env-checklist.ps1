#!/usr/bin/env powershell
# Vercel Environment Variables Checklist
# Run this script to verify your setup before and after Vercel deployment

Write-Host "🔍 VERCEL ENVIRONMENT VARIABLES CHECKLIST" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Check local .env.production
Write-Host "1. 📋 Checking local .env.production..." -ForegroundColor Yellow
$envFile = "C:\Users\mccab\contractornest\frontend\.env.production"
if (Test-Path $envFile) {
    Write-Host "   ✅ File exists" -ForegroundColor Green
    $envContent = Get-Content $envFile
    Write-Host "   📄 Current contents:" -ForegroundColor Cyan
    foreach ($line in $envContent) {
        if ($line.Trim() -and !$line.StartsWith("#")) {
            Write-Host "      $line" -ForegroundColor White
        }
    }
    
    # Check for VITE references
    $viteLines = $envContent | Where-Object { $_ -match "VITE_" }
    if ($viteLines.Count -gt 0) {
        Write-Host "   ❌ FOUND VITE_ REFERENCES - THESE NEED TO BE REMOVED!" -ForegroundColor Red
        foreach ($line in $viteLines) {
            Write-Host "      ❌ $line" -ForegroundColor Red
        }
    } else {
        Write-Host "   ✅ No VITE_ references found" -ForegroundColor Green
    }
} else {
    Write-Host "   ❌ .env.production not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "2. 🎯 REQUIRED VERCEL PRODUCTION ENVIRONMENT VARIABLES:" -ForegroundColor Yellow
Write-Host "   Copy these to Vercel Dashboard > Settings > Environment Variables > Production:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   REACT_APP_API_BASE_URL=https://api.useleadnest.com" -ForegroundColor White
Write-Host "   REACT_APP_PUBLIC_APP_NAME=LeadNest" -ForegroundColor White
Write-Host "   REACT_APP_CALENDLY_URL=https://calendly.com/leadnest-demo" -ForegroundColor White
Write-Host "   REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_REPLACE_WITH_ACTUAL_KEY" -ForegroundColor White
Write-Host "   REACT_APP_ENV_NAME=production" -ForegroundColor White
Write-Host "   REACT_APP_ENABLE_ANALYTICS=true" -ForegroundColor White
Write-Host "   REACT_APP_ENABLE_CHAT_SUPPORT=false" -ForegroundColor White
Write-Host ""

Write-Host "3. ❌ DELETE THESE FROM VERCEL (if they exist):" -ForegroundColor Red
Write-Host "   VITE_API_BASE_URL" -ForegroundColor Red
Write-Host "   VITE_STRIPE_PUBLISHABLE_KEY" -ForegroundColor Red
Write-Host "   VITE_PUBLIC_APP_NAME" -ForegroundColor Red
Write-Host "   VITE_CALENDLY_URL" -ForegroundColor Red
Write-Host "   VITE_ENV_NAME" -ForegroundColor Red
Write-Host "   VITE_ENABLE_ANALYTICS" -ForegroundColor Red
Write-Host "   VITE_ENABLE_CHAT_SUPPORT" -ForegroundColor Red
Write-Host ""

Write-Host "4. 🚀 DEPLOYMENT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Go to: https://vercel.com/dashboard" -ForegroundColor Cyan
Write-Host "   2. Find: leadnest-frontend project" -ForegroundColor Cyan
Write-Host "   3. Settings > Environment Variables" -ForegroundColor Cyan
Write-Host "   4. DELETE any VITE_* variables" -ForegroundColor Cyan
Write-Host "   5. ADD the REACT_APP_* variables above" -ForegroundColor Cyan
Write-Host "   6. Go to Deployments tab" -ForegroundColor Cyan
Write-Host "   7. Latest deployment > ... > Redeploy" -ForegroundColor Cyan
Write-Host "   8. UNCHECK 'Use existing Build Cache'" -ForegroundColor Cyan
Write-Host "   9. Click Redeploy" -ForegroundColor Cyan
Write-Host ""

Write-Host "5. 🔍 VERIFICATION AFTER DEPLOYMENT:" -ForegroundColor Yellow
Write-Host "   1. Open: https://useleadnest.com" -ForegroundColor Cyan
Write-Host "   2. Hard refresh: Ctrl+F5 or Ctrl+Shift+R" -ForegroundColor Cyan
Write-Host "   3. DevTools Console: No VITE or import.meta errors" -ForegroundColor Cyan
Write-Host "   4. Network tab: API calls to api.useleadnest.com" -ForegroundColor Cyan
Write-Host "   5. Deep link test: https://useleadnest.com/dashboard" -ForegroundColor Cyan
Write-Host ""

# Check for any remaining VITE references in codebase
Write-Host "6. Scanning codebase for VITE references..." -ForegroundColor Yellow
Set-Location "C:\Users\mccab\contractornest\frontend"
$viteRefs = Get-ChildItem -Recurse -Include "*.ts", "*.tsx", "*.js", "*.jsx" -Path "src" | 
    ForEach-Object { Select-String -Path $_.FullName -Pattern "VITE_|import\.meta\.env" -AllMatches } |
    Select-Object -First 10

if ($viteRefs) {
    Write-Host "   FOUND VITE REFERENCES IN CODE:" -ForegroundColor Red
    $viteRefs | ForEach-Object {
        Write-Host "      $($_.Filename):$($_.LineNumber) - $($_.Line.Trim())" -ForegroundColor Red
    }
} else {
    Write-Host "   No VITE references found in source code" -ForegroundColor Green
}

Write-Host ""
Write-Host "7. FINAL CHECKLIST:" -ForegroundColor Yellow
Write-Host "   [ ] Deleted all VITE_* variables from Vercel" -ForegroundColor White
Write-Host "   [ ] Added all REACT_APP_* variables to Vercel Production" -ForegroundColor White
Write-Host "   [ ] Redeployed with NO build cache" -ForegroundColor White
Write-Host "   [ ] Hard refreshed https://useleadnest.com" -ForegroundColor White
Write-Host "   [ ] No console errors" -ForegroundColor White
Write-Host "   [ ] API calls working" -ForegroundColor White
Write-Host "   [ ] Deep links working" -ForegroundColor White
Write-Host ""

Write-Host "SCREENSHOT REQUIREMENT:" -ForegroundColor Magenta
Write-Host "   Take a screenshot of Vercel Environment Variables Production" -ForegroundColor Magenta
Write-Host "   showing ONLY REACT_APP_* variables (no VITE_*)" -ForegroundColor Magenta
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Ready for Vercel deployment!" -ForegroundColor Green
