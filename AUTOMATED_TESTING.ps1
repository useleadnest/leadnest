# 🚀 AUTOMATED TESTING & FRONTEND UPDATE SCRIPT

# Wait for user to confirm service is deployed
Write-Host "🔄 Waiting for leadnest-api-final service to be deployed..."
Write-Host "Once deployed, I'll run comprehensive testing!"

# Test Backend Function
function Test-Backend {
    $baseUrl = "https://leadnest-api-final.onrender.com"
    
    Write-Host "🧪 Testing Backend Endpoints..."
    
    # Test 1: Root endpoint
    try {
        $root = Invoke-RestMethod -Uri "$baseUrl/"
        if ($root.version -eq "1.0.6-PERFECT") {
            Write-Host "✅ Root endpoint: Version $($root.version) - PERFECT!"
        } else {
            Write-Host "⚠️ Root endpoint: Unexpected version $($root.version)"
        }
    } catch {
        Write-Host "❌ Root endpoint failed: $($_.Exception.Message)"
    }
    
    # Test 2: Health check
    try {
        $health = Invoke-RestMethod -Uri "$baseUrl/health"
        if ($health.status -eq "healthy") {
            Write-Host "✅ Health endpoint: $($health.status)"
        } else {
            Write-Host "⚠️ Health endpoint: $($health.status)"
        }
    } catch {
        Write-Host "❌ Health endpoint failed: $($_.Exception.Message)"
    }
    
    # Test 3: Debug info
    try {
        $debug = Invoke-RestMethod -Uri "$baseUrl/debug-info"
        Write-Host "✅ Debug endpoint: Database available: $($debug.database_available)"
    } catch {
        Write-Host "❌ Debug endpoint failed: $($_.Exception.Message)"
    }
    
    # Test 4: Status page
    try {
        $status = Invoke-RestMethod -Uri "$baseUrl/status"
        $endpointCount = $status.endpoints.PSObject.Properties.Count
        Write-Host "✅ Status endpoint: $endpointCount endpoints available"
    } catch {
        Write-Host "❌ Status endpoint failed: $($_.Exception.Message)"
    }
    
    # Test 5: Auth endpoints
    $testUser = @{
        email = "test@leadnest.com"
        password = "securepass123"
    } | ConvertTo-Json
    
    try {
        $register = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -ContentType "application/json" -Body $testUser
        Write-Host "✅ Registration endpoint: Working (returned user data)"
    } catch {
        if ($_.Exception.Response.StatusCode -eq 400) {
            Write-Host "✅ Registration endpoint: Working (400 = user exists, expected)"
        } else {
            Write-Host "❌ Registration endpoint failed: $($_.Exception.Message)"
        }
    }
    
    try {
        $login = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -ContentType "application/json" -Body $testUser
        Write-Host "✅ Login endpoint: Working (returned token)"
    } catch {
        Write-Host "⚠️ Login endpoint: $($_.Exception.Message)"
    }
}

# Update Frontend Function
function Update-Frontend {
    Write-Host "🔄 Updating Frontend..."
    
    # Update .env.production
    $envPath = "c:\Users\mccab\contractornest\frontend\.env.production"
    $newContent = "VITE_API_URL=https://leadnest-api-final.onrender.com"
    Set-Content -Path $envPath -Value $newContent
    Write-Host "✅ Updated .env.production with new API URL"
    
    # Rebuild frontend
    Set-Location "c:\Users\mccab\contractornest\frontend"
    $env:PATH += ";C:\Program Files\nodejs"
    
    Write-Host "🔧 Building frontend..."
    & npm run build
    
    Write-Host "🚀 Deploying to Vercel..."
    & npx vercel --prod
    
    Write-Host "✅ Frontend updated and deployed!"
}

# Test Registration Flow Function
function Test-RegistrationFlow {
    Write-Host "🧪 Registration Flow Test Instructions:"
    Write-Host ""
    Write-Host "1. Open: https://leadnest-frontend-ocr18jamx-christians-projects-d64cce8f.vercel.app/auth/register"
    Write-Host "2. Fill form:"
    Write-Host "   Email: test@leadnest.com"
    Write-Host "   Password: securepass123"
    Write-Host "   Confirm: securepass123"
    Write-Host "3. Click Register"
    Write-Host "4. Check for:"
    Write-Host "   ✅ No CORS errors in console (F12)"
    Write-Host "   ✅ Success message or redirect"
    Write-Host "   ✅ Network tab shows 200/201 response"
    Write-Host "   ✅ User data returned from backend"
}

Write-Host "Ready to execute all phases once service is deployed!"
Write-Host "Call Test-Backend, Update-Frontend, and Test-RegistrationFlow when ready!"
