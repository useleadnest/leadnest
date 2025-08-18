#!/usr/bin/env pwsh
# quick-health-check.ps1 - Quick health verification for LeadNest production

$baseUrl = "https://api.useleadnest.com"

Write-Host "🩺 Quick Health Check - LeadNest Production" -ForegroundColor Cyan
Write-Host "URL: $baseUrl" -ForegroundColor Green

$endpoints = @(
    @{ Name = "Root"; Path = "/" },
    @{ Name = "Health"; Path = "/healthz" },
    @{ Name = "Ready"; Path = "/readyz" },
    @{ Name = "Deployment Info"; Path = "/api/deployment-info" },
    @{ Name = "Twilio Debug"; Path = "/api/twilio/debug" }
)

$passed = 0
$total = $endpoints.Count

foreach ($endpoint in $endpoints) {
    $url = "$baseUrl$($endpoint.Path)"
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $($endpoint.Name)" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "❌ $($endpoint.Name) - Status: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ $($endpoint.Name) - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nResult: $passed/$total endpoints healthy" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })

if ($passed -eq $total) {
    Write-Host "🎉 All systems GO! Ready for launch." -ForegroundColor Green
} else {
    Write-Host "⚠️  Issues detected. Check Render deployment." -ForegroundColor Yellow
}
