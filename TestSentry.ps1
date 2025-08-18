# Test Sentry Integration Script
# This script will help you test Sentry integration locally

param(
    [string]$SentryDSN = ""
)

Write-Host "🐛 Sentry Integration Test Script" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

$frontendPath = "C:\Users\mccab\contractornest\frontend"
$envLocalPath = "$frontendPath\.env.local"

if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ Frontend directory not found at $frontendPath" -ForegroundColor Red
    exit 1
}

# Check if Sentry DSN is provided
if ([string]::IsNullOrEmpty($SentryDSN)) {
    Write-Host "`n⚠️  No Sentry DSN provided." -ForegroundColor Yellow
    Write-Host "📋 To test Sentry integration:" -ForegroundColor Blue
    Write-Host "   1. Create a Sentry account at https://sentry.io" -ForegroundColor Gray
    Write-Host "   2. Create a new React project" -ForegroundColor Gray
    Write-Host "   3. Copy your DSN (looks like: https://abc123@sentry.io/456789)" -ForegroundColor Gray
    Write-Host "   4. Run this script again with: .\TestSentry.ps1 -SentryDSN 'your-dsn'" -ForegroundColor Gray
    Write-Host "`n💡 Or manually edit $envLocalPath" -ForegroundColor Blue
    Write-Host "   Uncomment and set: REACT_APP_SENTRY_DSN=your-dsn" -ForegroundColor Gray
} else {
    # Update .env.local with Sentry DSN
    Write-Host "📝 Setting Sentry DSN in .env.local..." -ForegroundColor Blue
    
    if (Test-Path $envLocalPath) {
        $envContent = Get-Content $envLocalPath -Raw
        
        # Remove existing REACT_APP_SENTRY_DSN line if exists
        $envContent = $envContent -replace "REACT_APP_SENTRY_DSN=.*`n", ""
        
        # Add new Sentry DSN
        $envContent += "`nREACT_APP_SENTRY_DSN=$SentryDSN`n"
        
        $envContent | Set-Content $envLocalPath -NoNewline
        Write-Host "✅ Sentry DSN added to .env.local" -ForegroundColor Green
    } else {
        Write-Host "❌ .env.local file not found" -ForegroundColor Red
        exit 1
    }
}

# Check if dependencies are installed
Write-Host "`n📦 Checking Sentry dependencies..." -ForegroundColor Blue
Set-Location $frontendPath

$packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
$sentryInstalled = $packageJson.dependencies.'@sentry/react' -or $packageJson.devDependencies.'@sentry/react'

if ($sentryInstalled) {
    Write-Host "✅ @sentry/react is installed" -ForegroundColor Green
} else {
    Write-Host "❌ @sentry/react not found in package.json" -ForegroundColor Red
    Write-Host "💡 Run: npm install @sentry/react @sentry/integrations @sentry/tracing" -ForegroundColor Yellow
}

# Start development server
Write-Host "`n🚀 Starting development server..." -ForegroundColor Green
Write-Host "📱 Once started, visit: http://localhost:3000/sentry-test" -ForegroundColor Blue
Write-Host "🐛 Click the error buttons to test Sentry integration" -ForegroundColor Yellow
Write-Host "📊 Check your Sentry dashboard for incoming errors" -ForegroundColor Cyan

Write-Host "`n🔍 What to look for:" -ForegroundColor Blue
Write-Host "   • Browser console should show: '🐛 Sentry initialized successfully!'" -ForegroundColor Gray
Write-Host "   • Errors should appear in Sentry dashboard within seconds" -ForegroundColor Gray
Write-Host "   • Network errors should be filtered out (won't appear)" -ForegroundColor Gray

Write-Host "`nPress any key to start the development server..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

try {
    npm start
} catch {
    Write-Host "`n❌ Failed to start development server" -ForegroundColor Red
    Write-Host "💡 Make sure you're in the frontend directory and run: npm install" -ForegroundColor Yellow
}

# Return to original directory
Set-Location "C:\Users\mccab\contractornest"
