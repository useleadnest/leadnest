#!/usr/bin/env pwsh
# Test-Stripe-Integration.ps1 - Stripe webhook testing
param(
    [string]$WebhookUrl = "https://api.useleadnest.com/api/stripe/webhook"
)

Write-Host "🧪 Testing Stripe Integration" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

Write-Host "1. Test webhook endpoint structure:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $WebhookUrl -Method POST -Body '{}' -ContentType "application/json" -UseBasicParsing
    Write-Host "   ✅ Webhook accepts POST requests" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 400 -or $statusCode -eq 401) {
        Write-Host "   ✅ Webhook returns $statusCode (expected for missing signature)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Unexpected status: $statusCode" -ForegroundColor Red
    }
}

Write-Host "`n2. CLI test commands (run these with Stripe CLI):" -ForegroundColor Yellow
Write-Host "   stripe listen --forward-to $WebhookUrl" -ForegroundColor Gray
Write-Host "   stripe trigger customer.subscription.created" -ForegroundColor Gray

Write-Host "`n3. Frontend checkout test:" -ForegroundColor Yellow
Write-Host "   • Visit https://useleadnest.com" -ForegroundColor Gray  
Write-Host "   • Click 'Upgrade Plan' or pricing button" -ForegroundColor Gray
Write-Host "   • Should open Stripe Checkout (test mode)" -ForegroundColor Gray
