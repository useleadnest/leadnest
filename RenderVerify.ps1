# Render Deployment Verification Script
param(
    [string]$ApiDomain = "leadnest-api.onrender.com"
)

Write-Host "🚀 RENDER DEPLOYMENT VERIFICATION" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""

# Test 1: Basic connectivity
Write-Host "1. Testing Basic Connectivity..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://$ApiDomain/healthz" -Method GET -UseBasicParsing -ErrorAction Stop
    Write-Host "   ✅ PASS: Health endpoint responding" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor White
    Write-Host "   Response: $($response.Content)" -ForegroundColor White
}
catch {
    Write-Host "   ❌ FAIL: Health endpoint not responding" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    return
}

Write-Host ""

# Test 2: Check for proper Flask response headers
Write-Host "2. Testing Flask App Headers..." -ForegroundColor Cyan
try {
    $headers = $response.Headers
    if ($headers.Server -match "gunicorn") {
        Write-Host "   ✅ PASS: Gunicorn server detected" -ForegroundColor Green
    }
    elseif ($headers.Server -match "Werkzeug") {
        Write-Host "   ⚠️  WARN: Development server detected (should be gunicorn)" -ForegroundColor Yellow  
    }
    else {
        Write-Host "   ⚠️  INFO: Server header: $($headers.Server)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ⚠️  WARN: Could not check server headers" -ForegroundColor Yellow
}

Write-Host ""

# Test 3: CORS headers
Write-Host "3. Testing CORS Configuration..." -ForegroundColor Cyan
try {
    $corsTest = Invoke-WebRequest -Uri "https://$ApiDomain/healthz" -Method OPTIONS -UseBasicParsing -ErrorAction SilentlyContinue
    if ($corsTest -and $corsTest.Headers.'Access-Control-Allow-Origin') {
        Write-Host "   ✅ PASS: CORS headers present" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  WARN: CORS headers not detected" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ⚠️  INFO: OPTIONS request not supported (normal)" -ForegroundColor Yellow
}

Write-Host ""

# Test 4: Auth endpoint
Write-Host "4. Testing Auth Endpoint..." -ForegroundColor Cyan
try {
    $authResponse = Invoke-WebRequest -Uri "https://$ApiDomain/auth/login" -Method POST -ContentType "application/json" -Body '{"email":"test","password":"test"}' -UseBasicParsing -ErrorAction Stop
    Write-Host "   ❌ UNEXPECTED: Auth endpoint returned success without valid credentials" -ForegroundColor Red
}
catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401 -or $_.Exception.Response.StatusCode.value__ -eq 400) {
        Write-Host "   ✅ PASS: Auth endpoint properly rejecting invalid credentials" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ FAIL: Auth endpoint error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""

# Test 5: Database connectivity (indirect test)
Write-Host "5. Testing Database Connectivity..." -ForegroundColor Cyan
try {
    # Try to access an endpoint that would require database
    $dbTest = Invoke-WebRequest -Uri "https://$ApiDomain/auth/me" -Method GET -UseBasicParsing -ErrorAction Stop
    Write-Host "   ❌ UNEXPECTED: Protected endpoint accessible without auth" -ForegroundColor Red  
}
catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401) {
        Write-Host "   ✅ PASS: Protected endpoint properly secured (DB likely connected)" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  WARN: Unexpected response from protected endpoint" -ForegroundColor Yellow
        Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
    }
}

Write-Host ""

# Test 6: Performance check
Write-Host "6. Testing Response Time..." -ForegroundColor Cyan
$startTime = Get-Date
try {
    $perfTest = Invoke-WebRequest -Uri "https://$ApiDomain/healthz" -Method GET -UseBasicParsing -ErrorAction Stop
    $endTime = Get-Date
    $responseTime = ($endTime - $startTime).TotalMilliseconds
    
    if ($responseTime -lt 1000) {
        Write-Host "   ✅ PASS: Response time: $([math]::Round($responseTime))ms" -ForegroundColor Green
    }
    elseif ($responseTime -lt 3000) {
        Write-Host "   ⚠️  WARN: Slow response time: $([math]::Round($responseTime))ms" -ForegroundColor Yellow
    }
    else {
        Write-Host "   ❌ FAIL: Very slow response time: $([math]::Round($responseTime))ms" -ForegroundColor Red
    }
}
catch {
    Write-Host "   ❌ FAIL: Could not test response time" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 DEPLOYMENT VERIFICATION COMPLETE" -ForegroundColor Yellow

# Summary
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. If all tests pass: Run full smoke tests with .\ProductionVerify.ps1" -ForegroundColor White  
Write-Host "2. If tests fail: Check Render service logs for specific errors" -ForegroundColor White
Write-Host "3. Verify all environment variables are set in Render dashboard" -ForegroundColor White
