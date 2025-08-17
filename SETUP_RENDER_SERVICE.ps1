# RENDER SERVICE CREATION ASSISTANT

Write-Host "🚀 LEADNEST RENDER SERVICE SETUP"
Write-Host "=================================="
Write-Host ""

# Open Render dashboard
Write-Host "1. Opening Render dashboard..."
Start-Process "https://render.com/dashboard"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ FOLLOW THESE STEPS IN YOUR BROWSER:"
Write-Host ""

Write-Host "📝 SERVICE CONFIGURATION:"
Write-Host "  Name: leadnest-api-final"
Write-Host "  Environment: Python"
Write-Host "  Region: Oregon (US West)"
Write-Host "  Branch: main"
Write-Host "  Root Directory: (leave blank)"
Write-Host ""

Write-Host "🔧 BUILD & START COMMANDS:"
Write-Host "  Build Command:"
Write-Host "    pip install --upgrade pip && pip install -r requirements.txt"
Write-Host ""
Write-Host "  Start Command:"
Write-Host "    python -m uvicorn main_perfect:app --host 0.0.0.0 --port `$PORT --log-level info"
Write-Host ""

Write-Host "🏥 HEALTH CHECK:"
Write-Host "  Health Check Path: /health"
Write-Host ""

Write-Host "🔐 ENVIRONMENT VARIABLES:"
Write-Host "  - DATABASE_URL (copy from old service)"
Write-Host "  - JWT_SECRET_KEY (generate new)"
Write-Host "  - STRIPE_PUBLISHABLE_KEY"
Write-Host "  - STRIPE_SECRET_KEY"  
Write-Host "  - STRIPE_WEBHOOK_SECRET"
Write-Host "  - OPENAI_API_KEY"
Write-Host "  - FRONTEND_URL: https://useleadnest.com"
Write-Host "  - ENVIRONMENT: production"
Write-Host ""

Write-Host "⏱️ WHEN DONE:"
Write-Host "  Press ENTER here to start monitoring deployment..."
Read-Host

# Start monitoring
Write-Host ""
Write-Host "🔍 Starting deployment monitor..."
powershell -ExecutionPolicy Bypass .\MONITOR_DEPLOYMENT.ps1
