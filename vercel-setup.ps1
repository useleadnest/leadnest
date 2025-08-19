# Vercel Environment Variables Setup
Write-Host "VERCEL ENVIRONMENT VARIABLES CHECKLIST" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

# Check local env file
Write-Host "1. Checking local .env.production..." -ForegroundColor Yellow
$envFile = "C:\Users\mccab\contractornest\frontend\.env.production"
if (Test-Path $envFile) {
    Write-Host "   File exists" -ForegroundColor Green
    $envContent = Get-Content $envFile
    Write-Host "   Current contents:" -ForegroundColor Cyan
    foreach ($line in $envContent) {
        if ($line.Trim() -and !$line.StartsWith("#")) {
            Write-Host "      $line" -ForegroundColor White
        }
    }
} else {
    Write-Host "   .env.production not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "2. REQUIRED VERCEL PRODUCTION VARIABLES:" -ForegroundColor Yellow
Write-Host "   REACT_APP_API_BASE_URL=https://api.useleadnest.com" -ForegroundColor White
Write-Host "   REACT_APP_PUBLIC_APP_NAME=LeadNest" -ForegroundColor White
Write-Host "   REACT_APP_CALENDLY_URL=https://calendly.com/leadnest-demo" -ForegroundColor White
Write-Host "   REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_REPLACE_WITH_ACTUAL_KEY" -ForegroundColor White
Write-Host "   REACT_APP_ENV_NAME=production" -ForegroundColor White
Write-Host "   REACT_APP_ENABLE_ANALYTICS=true" -ForegroundColor White
Write-Host "   REACT_APP_ENABLE_CHAT_SUPPORT=false" -ForegroundColor White
Write-Host ""

Write-Host "3. DELETE THESE FROM VERCEL (if they exist):" -ForegroundColor Red
Write-Host "   Any VITE_* variables" -ForegroundColor Red
Write-Host ""

# Check for VITE references in code
Write-Host "4. Scanning for VITE references..." -ForegroundColor Yellow
Set-Location "C:\Users\mccab\contractornest\frontend"
$viteCount = 0
$files = Get-ChildItem -Recurse -Include "*.ts", "*.tsx", "*.js", "*.jsx" -Path "src"
foreach ($file in $files) {
    $matches = Select-String -Path $file.FullName -Pattern "VITE_|import\.meta\.env" -SimpleMatch
    if ($matches) {
        $viteCount += $matches.Count
        foreach ($match in $matches) {
            Write-Host "   FOUND: $($file.Name):$($match.LineNumber) - $($match.Line.Trim())" -ForegroundColor Red
        }
    }
}
if ($viteCount -eq 0) {
    Write-Host "   No VITE references found in source code" -ForegroundColor Green
}

Write-Host ""
Write-Host "5. DEPLOYMENT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Go to Vercel Dashboard" -ForegroundColor Cyan
Write-Host "   2. Settings > Environment Variables" -ForegroundColor Cyan
Write-Host "   3. DELETE any VITE_* variables" -ForegroundColor Cyan
Write-Host "   4. ADD the REACT_APP_* variables above" -ForegroundColor Cyan
Write-Host "   5. Deployments > ... > Redeploy (NO cache)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ready!" -ForegroundColor Green
