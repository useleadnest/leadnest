#!/usr/bin/env pwsh
# Production-Verification.ps1 - Complete system verification
param(
    [string]$BackendUrl = "https://api.useleadnest.com",
    [string]$FrontendUrl = "https://useleadnest.com"
)

$results = @()

function Test-Endpoint {
    param($Name, $Url, $Method="GET", $Body=$null, $ExpectedStatus=200)
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
            TimeoutSec = 10
        }
        if ($Body) { $params.Body = $Body; $params.ContentType = "application/json" }
        
        $response = Invoke-WebRequest @params
        $status = "PASS"
        $detail = $response.StatusCode
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq $ExpectedStatus) {
            $status = "PASS"
            $detail = "$statusCode (expected)"
        } else {
            $status = "FAIL"
            $detail = "$statusCode (expected $ExpectedStatus)"
        }
    }
    
    $script:results += [PSCustomObject]@{ Check=$Name; Status=$status; Detail=$detail }
    return $status -eq "PASS"
}

Write-Host "🔍 LeadNest Production Verification" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Core Health Checks
Test-Endpoint "Backend Health" "$BackendUrl/healthz"
Test-Endpoint "Backend Ready" "$BackendUrl/readyz"  
Test-Endpoint "Frontend Load" $FrontendUrl

# API Structure Tests
Test-Endpoint "Stripe Webhook Structure" "$BackendUrl/api/stripe/webhook" "POST" '{}' 400
Test-Endpoint "Twilio Webhook Structure" "$BackendUrl/api/twilio/inbound" "POST" 403

# Frontend API Integration
Test-Endpoint "CORS Preflight" "$BackendUrl/api/leads" "OPTIONS"

# Results Table
Write-Host "`n📊 Verification Results:" -ForegroundColor Cyan
$results | Format-Table -AutoSize

$passCount = ($results | Where-Object Status -eq "PASS").Count
$totalCount = $results.Count

if ($passCount -eq $totalCount) {
    Write-Host "✅ All checks passed! System ready for production." -ForegroundColor Green
} else {
    Write-Host "⚠️ $($totalCount - $passCount) checks failed. Review required." -ForegroundColor Yellow
}

return $passCount -eq $totalCount
