# Set Vercel Environment Variables for Sentry
# Run this after getting your Sentry DSN

param(
    [Parameter(Mandatory=$true)]
    [string]$SentryDSN
)

Write-Host "🔧 Setting up Sentry environment variables in Vercel..." -ForegroundColor Green

# Check if Vercel CLI is installed
$vercelInstalled = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelInstalled) {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g vercel
}

# Check if logged in to Vercel
try {
    $loginStatus = vercel whoami 2>&1
    if ($loginStatus -like "*Error*" -or $loginStatus -like "*not authenticated*") {
        Write-Host "🔐 Please login to Vercel..." -ForegroundColor Yellow
        vercel login
    }
} catch {
    Write-Host "🔐 Please login to Vercel..." -ForegroundColor Yellow
    vercel login
}

# Navigate to frontend directory
$frontendPath = "C:\Users\mccab\contractornest\frontend"
if (Test-Path $frontendPath) {
    Set-Location $frontendPath
    Write-Host "✅ Changed to frontend directory" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend directory not found at $frontendPath" -ForegroundColor Red
    exit 1
}

# Add Sentry DSN environment variable
Write-Host "📝 Adding REACT_APP_SENTRY_DSN environment variable..." -ForegroundColor Blue

try {
    # Use Write-Output to pipe the DSN to vercel env add
    $env:REACT_APP_SENTRY_DSN = $SentryDSN
    Write-Output $SentryDSN | vercel env add REACT_APP_SENTRY_DSN production
    
    Write-Host "✅ Environment variable added successfully" -ForegroundColor Green
    
    # Also add to preview environment
    Write-Host "📝 Adding to preview environment as well..." -ForegroundColor Blue
    Write-Output $SentryDSN | vercel env add REACT_APP_SENTRY_DSN preview
    
} catch {
    Write-Host "❌ Failed to add environment variable: $_" -ForegroundColor Red
    Write-Host "💡 Try adding manually in Vercel dashboard:" -ForegroundColor Yellow
    Write-Host "   1. Go to https://vercel.com/dashboard" -ForegroundColor Yellow
    Write-Host "   2. Select your project" -ForegroundColor Yellow  
    Write-Host "   3. Settings > Environment Variables" -ForegroundColor Yellow
    Write-Host "   4. Add: REACT_APP_SENTRY_DSN = $SentryDSN" -ForegroundColor Yellow
    exit 1
}

# List environment variables to confirm
Write-Host "📋 Current environment variables:" -ForegroundColor Blue
vercel env ls

# Trigger redeploy
Write-Host "🚀 Triggering production redeploy..." -ForegroundColor Green
try {
    vercel --prod --force
    Write-Host "✅ Deployment triggered successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    Write-Host "💡 You can manually redeploy from Vercel dashboard" -ForegroundColor Yellow
}

Write-Host "`n🎉 Sentry setup complete!" -ForegroundColor Green
Write-Host "📊 Check your Sentry dashboard at https://sentry.io for incoming errors" -ForegroundColor Blue
Write-Host "🔗 Your DSN: $SentryDSN" -ForegroundColor Gray

# Return to original directory
Set-Location "C:\Users\mccab\contractornest"
