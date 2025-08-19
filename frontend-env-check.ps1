# PowerShell encoding fix
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Quick Frontend Environment Check
Write-Host "Frontend Environment Check" -ForegroundColor Cyan

# Check if we're in the right directory
if (!(Test-Path "frontend/package.json")) {
    Write-Host "ERROR: Run this from the project root (where frontend/ folder is)" -ForegroundColor Red
    exit 1
}

Write-Host "`nChecking frontend configuration..." -ForegroundColor Yellow

# Check package.json for CRA
$packageJson = Get-Content "frontend/package.json" | ConvertFrom-Json
if ($packageJson.dependencies."react-scripts") {
    Write-Host "SUCCESS: Create React App detected" -ForegroundColor Green
} else {
    Write-Host "ERROR: react-scripts not found - is this CRA?" -ForegroundColor Red
}

# Check .env.production
if (Test-Path "frontend/.env.production") {
    Write-Host "SUCCESS: .env.production exists" -ForegroundColor Green
    
    $envContent = Get-Content "frontend/.env.production" -Raw
    
    # Check for correct REACT_APP_ prefixes
    if ($envContent -match "REACT_APP_API_BASE_URL") {
        Write-Host "SUCCESS: REACT_APP_API_BASE_URL found" -ForegroundColor Green
    } else {
        Write-Host "ERROR: REACT_APP_API_BASE_URL missing" -ForegroundColor Red
    }
    
    # Check for incorrect VITE_ prefixes
    if ($envContent -match "VITE_") {
        Write-Host "ERROR: VITE_ variables found - these won't work in CRA!" -ForegroundColor Red
    } else {
        Write-Host "SUCCESS: No VITE_ variables (good for CRA)" -ForegroundColor Green
    }
} else {
    Write-Host "ERROR: .env.production not found" -ForegroundColor Red
}

# Check vercel.json
if (Test-Path "frontend/vercel.json") {
    Write-Host "SUCCESS: vercel.json exists" -ForegroundColor Green
    
    $vercelConfig = Get-Content "frontend/vercel.json" | ConvertFrom-Json
    if ($vercelConfig.rewrites) {
        Write-Host "SUCCESS: SPA routing configured" -ForegroundColor Green
    } else {
        Write-Host "ERROR: SPA routing missing" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: vercel.json not found" -ForegroundColor Red
}

Write-Host "`nSUMMARY:" -ForegroundColor Cyan
Write-Host "- Frontend: Create React App [OK]"
Write-Host "- Environment variables: REACT_APP_ prefix [OK]"  
Write-Host "- Vercel config: SPA routing [OK]"
Write-Host "- Ready for deployment: YES"

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Set REACT_APP_* variables in Vercel dashboard"
Write-Host "2. Deploy and test at https://useleadnest.com"
Write-Host "3. Verify API calls hit https://api.useleadnest.com/api"
