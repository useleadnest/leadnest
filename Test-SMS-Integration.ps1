# SMS Integration Test Script for PowerShell
# Run this after setting environment variables in Render

Write-Host "🧪 Testing SMS Integration After Environment Variable Setup" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green

Write-Host ""
Write-Host "1. Testing API Health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "https://api.useleadnest.com/healthz" -Method GET -UseBasicParsing
    Write-Host "Health Status: $($healthResponse.StatusCode) - $($healthResponse.Content)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "2. Testing Debug Endpoint (should show all environment variables as 'true')..." -ForegroundColor Yellow
try {
    $debugResponse = Invoke-WebRequest -Uri "https://api.useleadnest.com/api/twilio/debug" -Method GET -UseBasicParsing
    Write-Host "Debug Response: $($debugResponse.Content)" -ForegroundColor Green
} catch {
    Write-Host "Debug endpoint not available yet or failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Testing Webhook with Sample Data..." -ForegroundColor Yellow
try {
    $webhookResponse = Invoke-WebRequest -Uri "https://api.useleadnest.com/api/twilio/inbound" -Method POST -Body "From=%2B18584223515&Body=Test+webhook&To=%2B18584223515" -ContentType "application/x-www-form-urlencoded" -UseBasicParsing
    Write-Host "Webhook Status: $($webhookResponse.StatusCode)" -ForegroundColor Green
    if ($webhookResponse.StatusCode -eq 403) {
        Write-Host "✅ Signature validation working correctly (403 expected without valid signature)" -ForegroundColor Green
    } elseif ($webhookResponse.StatusCode -eq 200) {
        Write-Host "✅ Webhook responding (200 OK)" -ForegroundColor Green
    }
} catch {
    Write-Host "Webhook test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Expected Results After Environment Variables Are Set:" -ForegroundColor Cyan
Write-Host "   - Debug endpoint should return all 'true' values" -ForegroundColor White
Write-Host "   - Webhook should return 403 (signature validation working) or 200" -ForegroundColor White
Write-Host "   - Real SMS to +1 858 422 3515 should get auto-reply" -ForegroundColor White

Write-Host ""
Write-Host "📱 Phone Numbers Configured:" -ForegroundColor Cyan
Write-Host "   Primary: +1 858 422 3515 (webhook configured ✅)" -ForegroundColor White
Write-Host "   Toll-free: +1 855 914 4065 (needs webhook setup)" -ForegroundColor White

Write-Host ""
Write-Host "🔧 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM to Render" -ForegroundColor White
Write-Host "   2. Wait 2-3 minutes for Render to redeploy" -ForegroundColor White
Write-Host "   3. Run this script again to verify" -ForegroundColor White
Write-Host "   4. Send real SMS to test end-to-end" -ForegroundColor White
