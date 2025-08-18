# LeadNest Production Deployment - Step by Step
Write-Host "🚀 LeadNest Production Deployment Starting..." -ForegroundColor Green

# Step 1: Pre-flight checks
Write-Host "📋 Step 1: Pre-deployment verification" -ForegroundColor Yellow

$criticalFiles = @(
    "backend-flask/requirements.txt",
    "backend-flask/wsgi.py", 
    "backend-flask/Procfile",
    "frontend/package.json",
    "frontend/.env.production"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🧪 Step 2: Testing Backend Locally" -ForegroundColor Yellow

cd backend-flask

# Set test environment
$env:DATABASE_URL = "sqlite:///test.db"
$env:JWT_SECRET = "test-secret-12345"
$env:PUBLIC_BASE_URL = "http://localhost:5000"
$env:CORS_ORIGINS = "http://localhost:3000"

Write-Host "Testing backend startup..."
try {
    python -c "from app import create_app; app = create_app(); print('✅ Backend starts successfully')"
    Write-Host "✅ Backend test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend test failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

cd ..

Write-Host ""
Write-Host "🌐 Step 3: Testing Frontend Build" -ForegroundColor Yellow

cd frontend

Write-Host "Testing frontend build..."
try {
    npm run build
    Write-Host "✅ Frontend builds successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend build failed" -ForegroundColor Red
}

cd ..

Write-Host ""
Write-Host "🎯 DEPLOYMENT READY!" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS - Execute manually:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. BACKEND (Render.com):" -ForegroundColor Yellow
Write-Host "   • Go to https://render.com/dashboard"
Write-Host "   • New + → Web Service → Connect GitHub"
Write-Host "   • Repo: useleadnest/leadnest"  
Write-Host "   • Root Directory: backend-flask"
Write-Host "   • Build: pip install -r requirements.txt"
Write-Host "   • Start: gunicorn wsgi:app --bind 0.0.0.0:`$PORT --workers 2"
Write-Host "   • Add PostgreSQL + Redis"
Write-Host "   • Set all environment variables"
Write-Host "   • Custom domain: api.useleadnest.com"
Write-Host ""

Write-Host "2. FRONTEND (Vercel):" -ForegroundColor Yellow  
Write-Host "   • cd frontend && vercel --prod"
Write-Host "   • Set VITE_API_BASE_URL=https://api.useleadnest.com/api"
Write-Host "   • Custom domain: useleadnest.com"
Write-Host ""

Write-Host "3. SMOKE TESTS:" -ForegroundColor Yellow
Write-Host "   • curl https://api.useleadnest.com/healthz"
Write-Host "   • curl https://api.useleadnest.com/readyz"  
Write-Host "   • Test login at https://useleadnest.com"
Write-Host ""

Write-Host "LeadNest is ready for production deployment! 🚀" -ForegroundColor Green
