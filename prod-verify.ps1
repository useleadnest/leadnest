# LeadNest Production Verification Script
# Run this to validate all systems for launch readiness

param(
    [string]$TwilioNumber = "",
    [switch]$SkipSMS = $false
)

Write-Host "🚀 LEADNEST PRODUCTION VERIFICATION" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Test Results Storage
$results = @()

function Add-Result {
    param($Component, $Status, $Details, $Command = "")
    $results += [PSCustomObject]@{
        Component = $Component
        Status = $Status  
        Details = $Details
        Command = $Command
    }
    
    $color = if ($Status -eq "PASS") { "Green" } elseif ($Status -eq "WARN") { "Yellow" } else { "Red" }
    $symbol = if ($Status -eq "PASS") { "✅" } elseif ($Status -eq "WARN") { "⚠️" } else { "❌" }
    Write-Host "$symbol $Component - $Details" -ForegroundColor $color
}

# 1) HEALTH/READY CHECKS
Write-Host "`n📊 INFRASTRUCTURE HEALTH" -ForegroundColor Yellow

try {
    $health = Invoke-WebRequest -Uri "https://api.useleadnest.com/healthz" -UseBasicParsing
    if ($health.StatusCode -eq 200) {
        Add-Result "Health Check" "PASS" "Backend responding (200 OK)"
    } else {
        Add-Result "Health Check" "FAIL" "Unexpected status: $($health.StatusCode)"
    }
} catch {
    Add-Result "Health Check" "FAIL" "Failed to connect: $($_.Exception.Message)"
}

try {
    $ready = Invoke-WebRequest -Uri "https://api.useleadnest.com/readyz" -UseBasicParsing
    if ($ready.StatusCode -eq 200) {
        Add-Result "Ready Check" "PASS" "Application ready (200 OK)"
    } else {
        Add-Result "Ready Check" "FAIL" "Not ready: $($ready.StatusCode)"
    }
} catch {
    Add-Result "Ready Check" "FAIL" "Readiness check failed: $($_.Exception.Message)"
}

# Test root endpoint for Flask banner
try {
    $root = Invoke-WebRequest -Uri "https://api.useleadnest.com/" -UseBasicParsing
    $content = $root.Content | ConvertFrom-Json
    if ($content.service -eq "leadnest-api") {
        Add-Result "Root Endpoint" "✅" "Flask banner present"
    } else {
        Add-Result "Root Endpoint" "⚠️" "Unexpected response: $($root.Content)"
    }
} catch {
    Add-Result "Root Endpoint" "❌" "Root endpoint failed: $($_.Exception.Message)"
}

# 2) TWILIO DEBUG CHECK
Write-Host "`n📱 TWILIO CONFIGURATION" -ForegroundColor Yellow

try {
    $twilioDebug = Invoke-WebRequest -Uri "https://api.useleadnest.com/api/twilio/debug" -UseBasicParsing
    if ($twilioDebug.StatusCode -eq 200) {
        $debugData = $twilioDebug.Content | ConvertFrom-Json
        
        $twilioChecks = @{
            "Account SID" = $debugData.twilio_account_sid_set
            "Auth Token" = $debugData.twilio_auth_token_set  
            "From Number" = $debugData.twilio_from_set
            "Database URL" = $debugData.database_url_set
            "JWT Secret" = $debugData.jwt_secret_set
        }
        
        foreach ($check in $twilioChecks.GetEnumerator()) {
            $status = if ($check.Value) { "✅" } else { "❌" }
            Add-Result "Twilio $($check.Key)" $status "$(if ($check.Value) {'SET'} else {'NOT SET'})"
        }
        
        Add-Result "Public Base URL" "✅" "Set to: $($debugData.public_base_url)"
        
    } else {
        Add-Result "Twilio Debug" "❌" "Debug endpoint failed: $($twilioDebug.StatusCode)"
    }
} catch {
    Add-Result "Twilio Debug" "❌" "Debug endpoint error: $($_.Exception.Message)"
}

# 3) TWILIO INBOUND SIMULATION
Write-Host "`n📞 TWILIO WEBHOOK TEST" -ForegroundColor Yellow

try {
    $twilioTest = Invoke-WebRequest `
        -Uri "https://api.useleadnest.com/api/twilio/inbound" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body "From=+15551234567&Body=Test&MessageSid=SM123&AccountSid=AC123"
    
    # This should return 403 due to invalid signature - that's expected!
    Add-Result "Twilio Signature" "❌" "Got 403 (expected without valid signature)"
} catch {
    $response = $_.Exception.Response
    if ($response.StatusCode -eq 403) {
        Add-Result "Twilio Signature" "✅" "Returns 403 for invalid signature (correct behavior)"
    } else {
        Add-Result "Twilio Signature" "❌" "Unexpected response: $($response.StatusCode)"
    }
}

# Test the debug inbound endpoint (no signature required)
try {
    $twilioDebugInbound = Invoke-WebRequest `
        -Uri "https://api.useleadnest.com/api/twilio/inbound-debug" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body "From=+15551234567&Body=Test"
    
    if ($twilioDebugInbound.StatusCode -eq 200 -and $twilioDebugInbound.Content -match "<Response>") {
        Add-Result "Twilio TwiML" "✅" "Returns valid TwiML XML"
    } else {
        Add-Result "Twilio TwiML" "❌" "Invalid TwiML response"
    }
} catch {
    Add-Result "Twilio TwiML" "❌" "Debug inbound failed: $($_.Exception.Message)"
}

# 4) STRIPE ENDPOINTS TEST
Write-Host "`n💳 STRIPE INTEGRATION" -ForegroundColor Yellow

# Test webhook endpoint (should return 400 for unsigned)
try {
    $stripeWebhook = Invoke-WebRequest `
        -Uri "https://api.useleadnest.com/api/stripe/webhook" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"test": true}'
    
    Add-Result "Stripe Webhook" "❌" "Unexpected success - should return 400"
} catch {
    $response = $_.Exception.Response
    if ($response.StatusCode -eq 400) {
        Add-Result "Stripe Webhook" "✅" "Returns 400 for unsigned webhook (correct)"
    } elseif ($response.StatusCode -eq 404) {
        Add-Result "Stripe Webhook" "❌" "Endpoint not found - deployment issue"
    } else {
        Add-Result "Stripe Webhook" "⚠️" "Unexpected status: $($response.StatusCode)"
    }
}

# Test create checkout endpoint (should require auth)
try {
    $stripeCheckout = Invoke-WebRequest `
        -Uri "https://api.useleadnest.com/api/stripe/create-checkout" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"test": true}'
    
    Add-Result "Stripe Checkout" "❌" "Unexpected success - should require auth"
} catch {
    $response = $_.Exception.Response
    if ($response.StatusCode -eq 401 -or $response.StatusCode -eq 403) {
        Add-Result "Stripe Checkout" "✅" "Requires authentication (correct)"
    } elseif ($response.StatusCode -eq 404) {
        Add-Result "Stripe Checkout" "❌" "Endpoint not found - deployment issue"
    } else {
        Add-Result "Stripe Checkout" "⚠️" "Unexpected status: $($response.StatusCode)"
    }
}

# 5) REAL SMS TEST INSTRUCTIONS
if (-not $SkipSMS -and $TwilioNumber) {
    Write-Host "`n📲 REAL SMS TEST" -ForegroundColor Yellow
    Write-Host "Manual Action Required:" -ForegroundColor Cyan
    Write-Host "1. Send SMS to: $TwilioNumber" -ForegroundColor White
    Write-Host "2. Message: 'Test from verification script'" -ForegroundColor White
    Write-Host "3. Wait 10 seconds for auto-reply" -ForegroundColor White
    Write-Host "4. Press any key when done..." -ForegroundColor White
    
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    # Check if we can validate the SMS in logs (this would need Render API access)
    Add-Result "Real SMS Test" "⚠️" "Manual validation required - check for auto-reply"
} else {
    Add-Result "Real SMS Test" "⚠️" "Skipped - no Twilio number provided"
}

# 6) GENERATE SUMMARY REPORT
Write-Host "`n📋 LAUNCH READINESS SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$passed = ($results | Where-Object { $_.Status -eq "✅" }).Count
$warnings = ($results | Where-Object { $_.Status -eq "⚠️" }).Count  
$failed = ($results | Where-Object { $_.Status -eq "❌" }).Count
$total = $results.Count

Write-Host "`nResults: $passed✅ $warnings⚠️ $failed❌ (Total: $total)" -ForegroundColor White

# Display detailed results
$results | Format-Table -Property Component, Status, Details -AutoSize

# Overall recommendation
if ($failed -eq 0) {
    Write-Host "`n🎉 RECOMMENDATION: GO FOR LAUNCH! 🚀" -ForegroundColor Green -BackgroundColor Black
    Write-Host "All critical systems operational." -ForegroundColor Green
} elseif ($failed -le 2 -and $warnings -gt 0) {
    Write-Host "`n⚠️ RECOMMENDATION: CONDITIONAL GO" -ForegroundColor Yellow -BackgroundColor Black
    Write-Host "Minor issues present - address before marketing push." -ForegroundColor Yellow
} else {
    Write-Host "`n❌ RECOMMENDATION: NO-GO" -ForegroundColor Red -BackgroundColor Black
    Write-Host "Critical issues must be resolved before launch." -ForegroundColor Red
}

# TROUBLESHOOTING GUIDE
Write-Host "`n🔧 TROUBLESHOOTING QUICK FIXES" -ForegroundColor Cyan

$troubleshooting = @{
    "Health Check Failed" = "Check Render service status, verify domain routing"
    "Database URL Not Set" = "Set DATABASE_URL in Render environment variables"
    "Twilio Env Missing" = "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM in Render"
    "Stripe Endpoints 404" = "Deployment not taking effect - check Render build logs, clear cache"
    "TwiML Invalid" = "Check Twilio webhook URL points to https://api.useleadnest.com/api/twilio/inbound"
}

foreach ($item in $troubleshooting.GetEnumerator()) {
    Write-Host "$($item.Key): " -ForegroundColor Yellow -NoNewline
    Write-Host "$($item.Value)" -ForegroundColor White
}

Write-Host "`n✅ VERIFICATION COMPLETE" -ForegroundColor Green
Write-Host "Save this output for launch decision!" -ForegroundColor Cyan
