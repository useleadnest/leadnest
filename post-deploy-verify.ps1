# PowerShell encoding fix
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

param(
    [string]$Domain = "https://useleadnest.com"
)

Write-Host "POST-DEPLOYMENT VERIFICATION" -ForegroundColor Cyan
Write-Host "Testing: $Domain" -ForegroundColor Yellow
Write-Host ""

# Test 1: Basic site availability
Write-Host "1. BASIC AVAILABILITY" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $Domain -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: Site loads ($($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Site returned $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Site not accessible - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Static assets
Write-Host "`n2. STATIC ASSETS" -ForegroundColor Yellow
try {
    $html = Invoke-WebRequest -Uri $Domain -UseBasicParsing
    $jsFiles = [regex]::Matches($html.Content, '/static/js/[^"]+\.js')
    $cssFiles = [regex]::Matches($html.Content, '/static/css/[^"]+\.css')
    
    Write-Host "Found $($jsFiles.Count) JS files, $($cssFiles.Count) CSS files" -ForegroundColor Green
    
    # Test first JS file
    if ($jsFiles.Count -gt 0) {
        $jsUrl = $Domain + $jsFiles[0].Value
        $jsResponse = Invoke-WebRequest -Uri $jsUrl -UseBasicParsing -TimeoutSec 10
        if ($jsResponse.StatusCode -eq 200) {
            Write-Host "SUCCESS: JS assets loading" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "WARNING: Could not verify static assets" -ForegroundColor Yellow
}

# Test 3: SPA routing (deep links)
Write-Host "`n3. SPA ROUTING" -ForegroundColor Yellow
$testRoutes = @("/dashboard", "/billing", "/settings")
foreach ($route in $testRoutes) {
    try {
        $response = Invoke-WebRequest -Uri "$Domain$route" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "SUCCESS: $route returns 200" -ForegroundColor Green
        } else {
            Write-Host "WARNING: $route returned $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "ERROR: $route failed - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 4: API connectivity
Write-Host "`n4. API CONNECTIVITY" -ForegroundColor Yellow
$apiBase = "https://api.useleadnest.com"
try {
    $healthResponse = Invoke-WebRequest -Uri "$apiBase/healthz" -UseBasicParsing -TimeoutSec 10
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "SUCCESS: Backend API healthy" -ForegroundColor Green
        $healthData = $healthResponse.Content | ConvertFrom-Json
        Write-Host "Status: $($healthData.status)" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Backend API not responding" -ForegroundColor Red
}

# Test 5: Environment variable check
Write-Host "`n5. ENVIRONMENT VARIABLES" -ForegroundColor Yellow
Write-Host "Manual check required:" -ForegroundColor Yellow
Write-Host "1. Open $Domain in browser" -ForegroundColor White
Write-Host "2. Open DevTools -> Console" -ForegroundColor White
Write-Host "3. Run: console.log('API:', process.env.REACT_APP_API_BASE_URL)" -ForegroundColor White
Write-Host "4. Should show: 'https://api.useleadnest.com/api'" -ForegroundColor White

Write-Host "`n6. FINAL FUNCTIONAL TESTS" -ForegroundColor Yellow
Write-Host "Manual tests required:" -ForegroundColor Yellow
Write-Host "- Register new account" -ForegroundColor White
Write-Host "- Login with credentials" -ForegroundColor White  
Write-Host "- Dashboard loads with data" -ForegroundColor White
Write-Host "- Billing page opens Stripe" -ForegroundColor White
Write-Host "- All navigation works" -ForegroundColor White

Write-Host "`nVERIFICATION COMPLETE!" -ForegroundColor Green
Write-Host "If all tests pass, the deployment is successful!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test user registration/login flow"
Write-Host "2. Verify Stripe checkout integration"
Write-Host "3. Test Twilio SMS functionality"  
Write-Host "4. Monitor for any console errors"
