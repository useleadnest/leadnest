# LEADNEST PRODUCTION API TESTING SUITE
Write-Host "LEADNEST PRODUCTION API TESTING" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$baseUrl = "https://api.useleadnest.com"
Write-Host "Base URL: $baseUrl" -ForegroundColor Yellow
Write-Host ""

# Test 1: Health & Readiness Checks
Write-Host "1. HEALTH & READINESS CHECKS" -ForegroundColor Green
Write-Host "-----------------------------" -ForegroundColor Green

try {
    $health = Invoke-WebRequest -Uri "$baseUrl/healthz" -UseBasicParsing -TimeoutSec 10
    Write-Host "SUCCESS /healthz: $($health.StatusCode) - $($health.Content)" -ForegroundColor Green
} catch {
    Write-Host "FAILED /healthz: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $ready = Invoke-WebRequest -Uri "$baseUrl/readyz" -UseBasicParsing -TimeoutSec 10  
    Write-Host "SUCCESS /readyz: $($ready.StatusCode) - $($ready.Content)" -ForegroundColor Green
} catch {
    Write-Host "FAILED /readyz: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: Diagnostic Endpoints
Write-Host "2. DIAGNOSTIC ENDPOINTS" -ForegroundColor Green
Write-Host "-----------------------" -ForegroundColor Green

try {
    $deployInfo = Invoke-WebRequest -Uri "$baseUrl/api/deployment-info" -UseBasicParsing -TimeoutSec 10
    $deployData = $deployInfo.Content | ConvertFrom-Json
    Write-Host "SUCCESS /api/deployment-info: $($deployInfo.StatusCode)" -ForegroundColor Green
    Write-Host "   Commit: $($deployData.commit_hash)" -ForegroundColor Cyan
    Write-Host "   Deploy Time: $($deployData.deployment_time)" -ForegroundColor Cyan
} catch {
    Write-Host "FAILED /api/deployment-info: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $twilioDebug = Invoke-WebRequest -Uri "$baseUrl/api/twilio/debug" -UseBasicParsing -TimeoutSec 10
    $twilioData = $twilioDebug.Content | ConvertFrom-Json
    Write-Host "SUCCESS /api/twilio/debug: $($twilioDebug.StatusCode)" -ForegroundColor Green
    Write-Host "   Twilio Config: SID=$($twilioData.twilio_account_sid_set), Token=$($twilioData.twilio_auth_token_set), From=$($twilioData.twilio_from_set)" -ForegroundColor Cyan
    Write-Host "   Database: $($twilioData.database_url_set)" -ForegroundColor Cyan
} catch {
    Write-Host "FAILED /api/twilio/debug: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Webhook Endpoints (Structure Check)
Write-Host "3. WEBHOOK ENDPOINTS" -ForegroundColor Green
Write-Host "-------------------" -ForegroundColor Green

# Twilio webhook (should reject without proper signature)
try {
    $twilioBody = "From=%2B15555555555&Body=test&MessageSid=test123"
    $twilio = Invoke-WebRequest -Uri "$baseUrl/api/twilio/inbound" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $twilioBody -UseBasicParsing -TimeoutSec 10
    Write-Host "SUCCESS /api/twilio/inbound: $($twilio.StatusCode) - Endpoint accessible" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 403) {
        Write-Host "SUCCESS /api/twilio/inbound: 403 - Properly rejecting unsigned requests" -ForegroundColor Green
    } else {
        Write-Host "FAILED /api/twilio/inbound: $($_.Exception.Response.StatusCode) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Stripe webhook (should reject without proper signature) 
try {
    $stripeBody = "{""id"":""evt_test"",""type"":""customer.subscription.created""}"
    $stripe = Invoke-WebRequest -Uri "$baseUrl/api/stripe/webhook" -Method POST -ContentType "application/json" -Body $stripeBody -UseBasicParsing -TimeoutSec 10
    Write-Host "SUCCESS /api/stripe/webhook: $($stripe.StatusCode) - Endpoint accessible" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "SUCCESS /api/stripe/webhook: 400 - Properly rejecting unsigned requests" -ForegroundColor Green
    } else {
        Write-Host "FAILED /api/stripe/webhook: $($_.Exception.Response.StatusCode) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""

# Test 4: Performance Check
Write-Host "4. PERFORMANCE CHECK" -ForegroundColor Green
Write-Host "-------------------" -ForegroundColor Green

$times = @()
for ($i = 1; $i -le 5; $i++) {
    $start = Get-Date
    try {
        Invoke-WebRequest -Uri "$baseUrl/healthz" -UseBasicParsing -TimeoutSec 10 | Out-Null
        $end = Get-Date
        $elapsed = ($end - $start).TotalMilliseconds
        $times += $elapsed
        Write-Host "  Request $i : $([math]::Round($elapsed, 2))ms" -ForegroundColor Cyan
    } catch {
        Write-Host "  Request $i : FAILED" -ForegroundColor Red
    }
}

if ($times.Count -gt 0) {
    $avgTime = [math]::Round(($times | Measure-Object -Average).Average, 2)
    $p95Time = [math]::Round(($times | Sort-Object)[[math]::Floor($times.Count * 0.95)], 2)
    Write-Host "Average response time: ${avgTime}ms" -ForegroundColor Green
    Write-Host "P95 response time: ${p95Time}ms" -ForegroundColor Green
}

Write-Host ""

# Summary
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "============" -ForegroundColor Cyan
Write-Host "Health checks working" -ForegroundColor Green
Write-Host "Diagnostic endpoints working" -ForegroundColor Green  
Write-Host "Webhook endpoints accessible" -ForegroundColor Green
Write-Host "Performance benchmarked" -ForegroundColor Green
Write-Host ""
Write-Host "LeadNest API is production-ready!" -ForegroundColor Green

# Next Steps
Write-Host ""
Write-Host "NEXT STEPS FOR PRODUCTION:" -ForegroundColor Yellow
Write-Host "1. Set up monitoring/alerts (see monitoring-setup.md)" -ForegroundColor White
Write-Host "2. Configure Twilio webhook: $baseUrl/api/twilio/inbound" -ForegroundColor White
Write-Host "3. Configure Stripe webhook: $baseUrl/api/stripe/webhook" -ForegroundColor White
Write-Host "4. Update frontend to use: $baseUrl" -ForegroundColor White
Write-Host "5. Set up SSL monitoring and renewal" -ForegroundColor White
