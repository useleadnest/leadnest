# Production Smoke Test Commands (PowerShell 5.x safe)
# Copy/paste these after Render deployment is live

Write-Host "== Production Smoke Test ==" -ForegroundColor Yellow

$B = "https://leadnest-api.onrender.com"

Write-Host "1. Health checks:" -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$B/healthz" -Method GET
    Write-Host "  Healthz: OK" -ForegroundColor Green
} catch {
    Write-Host "  Healthz: FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

try {
    Invoke-WebRequest -Uri "$B/readyz" -Method GET  
    Write-Host "  Readyz: OK" -ForegroundColor Green
} catch {
    Write-Host "  Readyz: FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "2. Auth & protected routes:" -ForegroundColor Cyan
try {
    $login = Invoke-RestMethod -Uri "$B/auth/login" -Method POST -ContentType "application/json" -Body (@{email="a@b.c";password="x"} | ConvertTo-Json)
    $headers = @{ Authorization = "Bearer " + $login.token }
    Write-Host "  Login: OK, token received" -ForegroundColor Green
    
    $leads = Invoke-RestMethod -Uri "$B/leads" -Headers $headers -Method GET
    Write-Host "  Leads endpoint: OK" -ForegroundColor Green
} catch {
    Write-Host "  Auth/Leads: FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "3. Twilio webhook:" -ForegroundColor Cyan
try {
    $inboundForm = @{ From="+12223334444"; To="+19998887777"; Body="Prod TEST"; MessageSid="SM987654" }
    $result = Invoke-RestMethod -Uri "$B/twilio/inbound" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $inboundForm
    Write-Host "  Twilio webhook: OK" -ForegroundColor Green
} catch {
    Write-Host "  Twilio webhook: FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "== Smoke test complete ==" -ForegroundColor Yellow
