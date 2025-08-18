# LeadNest Production Verification Script
param(
    [string]$TwilioNumber = "",
    [switch]$SkipSMS = $false
)

Write-Host "LEADNEST PRODUCTION VERIFICATION" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Test Results
$results = @()

function Test-Component {
    param($Name, $TestBlock)
    try {
        $result = & $TestBlock
        Write-Host "PASS - $Name" -ForegroundColor Green
        return "PASS"
    } catch {
        Write-Host "FAIL - $Name : $($_.Exception.Message)" -ForegroundColor Red
        return "FAIL"
    }
}

# 1) Health Check
Write-Host "`nTesting Health Check..." -ForegroundColor Yellow
$healthResult = Test-Component "Health Check" {
    $response = Invoke-WebRequest -Uri "https://api.useleadnest.com/healthz" -UseBasicParsing
    if ($response.StatusCode -ne 200) { throw "Status: $($response.StatusCode)" }
}

# 2) Ready Check  
Write-Host "Testing Ready Check..." -ForegroundColor Yellow
$readyResult = Test-Component "Ready Check" {
    $response = Invoke-WebRequest -Uri "https://api.useleadnest.com/readyz" -UseBasicParsing
    if ($response.StatusCode -ne 200) { throw "Status: $($response.StatusCode)" }
}

# 3) Root Endpoint
Write-Host "Testing Root Endpoint..." -ForegroundColor Yellow
$rootResult = Test-Component "Root Endpoint" {
    $response = Invoke-WebRequest -Uri "https://api.useleadnest.com/" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    if ($data.service -ne "leadnest-api") { throw "Invalid service response" }
}

# 4) Twilio Debug
Write-Host "Testing Twilio Debug..." -ForegroundColor Yellow
$twilioResult = Test-Component "Twilio Debug" {
    $response = Invoke-WebRequest -Uri "https://api.useleadnest.com/api/twilio/debug" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  Twilio Account SID: $(if($data.twilio_account_sid_set){'SET'}else{'NOT SET'})" -ForegroundColor $(if($data.twilio_account_sid_set){'Green'}else{'Red'})
    Write-Host "  Twilio Auth Token: $(if($data.twilio_auth_token_set){'SET'}else{'NOT SET'})" -ForegroundColor $(if($data.twilio_auth_token_set){'Green'}else{'Red'})
    Write-Host "  Twilio From: $(if($data.twilio_from_set){'SET'}else{'NOT SET'})" -ForegroundColor $(if($data.twilio_from_set){'Green'}else{'Red'})
    Write-Host "  Database URL: $(if($data.database_url_set){'SET'}else{'NOT SET'})" -ForegroundColor $(if($data.database_url_set){'Green'}else{'Red'})
    if ($response.StatusCode -ne 200) { throw "Debug endpoint failed" }
}

# 5) Twilio Inbound (expect 403)
Write-Host "Testing Twilio Inbound Signature..." -ForegroundColor Yellow
try {
    $body = "From=+15551234567" + [char]38 + "Body=Test" + [char]38 + "MessageSid=SM123"
    Invoke-WebRequest -Uri "https://api.useleadnest.com/api/twilio/inbound" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $body -UseBasicParsing
    Write-Host "UNEXPECTED - Twilio Inbound: Should return 403 for invalid signature" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 403) {
        Write-Host "PASS - Twilio Inbound: Returns 403 for invalid signature (correct)" -ForegroundColor Green
    } else {
        Write-Host "FAIL - Twilio Inbound: Unexpected status $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# 6) Stripe Webhook (expect 400)
Write-Host "Testing Stripe Webhook..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "https://api.useleadnest.com/api/stripe/webhook" -Method POST -ContentType "application/json" -Body '{"test":true}' -UseBasicParsing
    Write-Host "UNEXPECTED - Stripe Webhook: Should return 400 for invalid signature" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "PASS - Stripe Webhook: Returns 400 for invalid signature (correct)" -ForegroundColor Green
    } elseif ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "FAIL - Stripe Webhook: Endpoint not found (deployment issue)" -ForegroundColor Red
    } else {
        Write-Host "WARN - Stripe Webhook: Unexpected status $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

# 7) Manual SMS Test Instructions
if (-not $SkipSMS -and $TwilioNumber) {
    Write-Host "`nMANUAL SMS TEST REQUIRED:" -ForegroundColor Cyan
    Write-Host "1. Send SMS to: $TwilioNumber" -ForegroundColor White
    Write-Host "2. Message: 'Test production webhook'" -ForegroundColor White
    Write-Host "3. Expect auto-reply within 10 seconds" -ForegroundColor White
    Write-Host "Press Enter when test is complete..." -ForegroundColor White
    Read-Host
    Write-Host "MANUAL - SMS Test: User validation required" -ForegroundColor Yellow
}

# Summary
Write-Host "`nVERIFICATION COMPLETE" -ForegroundColor Cyan
Write-Host "Review results above for launch decision." -ForegroundColor White

# Command Reference
Write-Host "`nUSEFUL COMMANDS:" -ForegroundColor Cyan
Write-Host "Health: Invoke-WebRequest -Uri 'https://api.useleadnest.com/healthz' -UseBasicParsing" -ForegroundColor Gray
Write-Host "Ready:  Invoke-WebRequest -Uri 'https://api.useleadnest.com/readyz' -UseBasicParsing" -ForegroundColor Gray
Write-Host "Debug:  Invoke-WebRequest -Uri 'https://api.useleadnest.com/api/twilio/debug' -UseBasicParsing" -ForegroundColor Gray
