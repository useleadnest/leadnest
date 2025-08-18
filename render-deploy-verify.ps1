#!/usr/bin/env pwsh
# render-deploy-verify.ps1 - Comprehensive LeadNest Render deployment verification
# 
# This script verifies all critical endpoints and configurations after Render deployment
#
# Usage: .\render-deploy-verify.ps1

param(
    [string]$BaseUrl = "https://api.useleadnest.com"
)

Write-Host "🚀 LeadNest Render Deployment Verification" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Green
Write-Host "=" * 60

$results = @{}
$allPassed = $true

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [string]$ExpectedContent = $null,
        [int]$ExpectedStatusCode = 200
    )
    
    Write-Host "Testing $Name..." -ForegroundColor Yellow
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
            Headers = $Headers
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = $Body
            if (-not $Headers.ContainsKey("Content-Type")) {
                $params.Headers["Content-Type"] = "application/json"
            }
        }
        
        $response = Invoke-WebRequest @params
        
        $statusMatch = $response.StatusCode -eq $ExpectedStatusCode
        $contentMatch = $true
        
        if ($ExpectedContent) {
            $contentMatch = $response.Content -like "*$ExpectedContent*"
        }
        
        if ($statusMatch -and $contentMatch) {
            Write-Host "✅ PASS - $Name" -ForegroundColor Green
            $results[$Name] = "PASS"
            return $true
        } else {
            Write-Host "❌ FAIL - $Name (Status: $($response.StatusCode), Content mismatch: $(-not $contentMatch))" -ForegroundColor Red
            if (-not $contentMatch) {
                Write-Host "   Expected: $ExpectedContent" -ForegroundColor DarkRed
                Write-Host "   Got: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))" -ForegroundColor DarkRed
            }
            $results[$Name] = "FAIL"
            return $false
        }
    } catch {
        Write-Host "❌ FAIL - $Name (Exception: $($_.Exception.Message))" -ForegroundColor Red
        $results[$Name] = "FAIL - $($_.Exception.Message)"
        return $false
    }
}

# Core health endpoints
Write-Host "`n🔍 Core Health Checks" -ForegroundColor Magenta
Test-Endpoint "Root Endpoint" "$BaseUrl/" -ExpectedContent "healthy"
Test-Endpoint "Health Check" "$BaseUrl/healthz" -ExpectedContent "healthy" 
Test-Endpoint "Readiness Check" "$BaseUrl/readyz" -ExpectedContent "ready"

# API endpoints 
Write-Host "`n🔍 API Endpoint Checks" -ForegroundColor Magenta
Test-Endpoint "Deployment Info" "$BaseUrl/api/deployment-info"
Test-Endpoint "Twilio Debug" "$BaseUrl/api/twilio/debug" 

# Twilio webhook (should return 403 without signature)
Write-Host "`n🔍 Twilio Integration Checks" -ForegroundColor Magenta
Test-Endpoint "Twilio Inbound (No Signature)" "$BaseUrl/api/twilio/inbound" -Method "POST" -ExpectedStatusCode 403

# Stripe endpoints (should be accessible but may return errors without proper auth/data)
Write-Host "`n🔍 Stripe Integration Checks" -ForegroundColor Magenta
Test-Endpoint "Stripe Webhook" "$BaseUrl/api/stripe/webhook" -Method "POST" -ExpectedStatusCode 400
Test-Endpoint "Billing Checkout" "$BaseUrl/api/billing/checkout" -Method "POST" -ExpectedStatusCode 401

Write-Host "`n📊 Summary" -ForegroundColor Cyan
Write-Host "=" * 60

$passCount = ($results.Values | Where-Object { $_ -eq "PASS" }).Count
$totalCount = $results.Count

foreach ($result in $results.GetEnumerator()) {
    $status = if ($result.Value -eq "PASS") { "✅" } else { "❌" }
    Write-Host "$status $($result.Key): $($result.Value)"
}

Write-Host "`nResults: $passCount/$totalCount passed" -ForegroundColor $(if ($passCount -eq $totalCount) { "Green" } else { "Yellow" })

if ($passCount -eq $totalCount) {
    Write-Host "🎉 All checks passed! LeadNest is ready for production." -ForegroundColor Green
} else {
    Write-Host "⚠️  Some checks failed. Review the Render logs and configuration." -ForegroundColor Yellow
}

Write-Host "`n🔧 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Check Render Dashboard → leadnest-backend → Environment for missing vars"
Write-Host "2. Verify Build Command: pip install -r requirements.txt"
Write-Host "3. Verify Start Command: gunicorn app.api:app --bind 0.0.0.0:`$PORT --workers 2 --threads 4 --timeout 120"
Write-Host "4. Root Directory should be: backend-flask"
Write-Host "5. If database errors, run: flask db upgrade from Render Shell"

return $passCount -eq $totalCount
