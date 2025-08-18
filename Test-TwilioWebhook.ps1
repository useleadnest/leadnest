#!/usr/bin/env pwsh
# Test-TwilioWebhook.ps1 - Test Twilio webhook signature validation
param(
    [Parameter(Mandatory=$false)]
    [string]$BaseUrl = "https://api.useleadnest.com"
)

Write-Host "🔍 Testing Twilio Webhook Endpoint" -ForegroundColor Cyan
Write-Host "URL: $BaseUrl/api/twilio/inbound" -ForegroundColor Gray
Write-Host ""

# Test 1: POST without signature (should return 403 if auth token is configured)
Write-Host "1. Testing without Twilio signature:" -ForegroundColor Yellow
try {
    $body = "From=+15551234567" + "&" + "Body=Test"
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/twilio/inbound" -Method POST -UseBasicParsing -ContentType "application/x-www-form-urlencoded" -Body $body
    Write-Host "  Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "  Response: $($response.Content)" -ForegroundColor Gray
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  Status: $statusCode" -ForegroundColor $(if ($statusCode -eq 403) {"Green"} else {"Red"})
    Write-Host "  Expected: 403 (Invalid signature)" -ForegroundColor Gray
}

Write-Host ""

# Test 2: Check if endpoint exists and responds
Write-Host "2. Testing endpoint availability:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/twilio/inbound" -Method GET -UseBasicParsing
    Write-Host "  GET Status: $($response.StatusCode)" -ForegroundColor Yellow
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  GET Status: $statusCode (Expected - webhook is POST only)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ Test complete. If auth token is configured, POST should return 403." -ForegroundColor Green
Write-Host "📝 Check Twilio Console → Monitor → Logs for actual webhook attempts." -ForegroundColor Cyan
