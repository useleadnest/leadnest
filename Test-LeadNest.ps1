<#
.SYNOPSIS
    LeadNest API End-to-End Smoke Test Suite

.DESCRIPTION
    Comprehensive test suite for LeadNest Flask API backend including:
    - Health checks with automatic retry
    - JWT authentication
    - Protected endpoints
    - Idempotency testing
    - CSV bulk import (small inline, large background jobs)
    - Job polling with timeout
    - Twilio webhook simulation
    - JUnit XML reporting

.PREREQUISITES
    - PowerShell 5.1+ or PowerShell Core
    - curl.exe available in PATH
    - For large CSV tests: Redis server and RQ worker running
    - For Twilio tests: TWILIO_AUTH_TOKEN unset for local unsigned tests

.PARAMETER BaseUrl
    API base URL (default: http://localhost:5000)

.PARAMETER Email
    Login email (default: a@b.c)

.PARAMETER Password
    Login password (default: x)

.PARAMETER PollSeconds
    Job polling interval in seconds (default: 2)

.PARAMETER PollTimeoutS
    Job polling timeout in seconds (default: 120)

.PARAMETER SkipLargeCsv
    Skip large CSV/background job tests (useful for local testing without Redis)

.EXAMPLE
    .\Test-LeadNest.ps1 -BaseUrl http://localhost:5000 -Email admin@test.com -Password secret123

.EXAMPLE
    .\Test-LeadNest.ps1 -SkipLargeCsv
#>

param(
    [string]$BaseUrl = "http://localhost:5000",
    [string]$Email = "a@b.c", 
    [string]$Password = "x",
    [int]$PollSeconds = 2,
    [int]$PollTimeoutS = 120,
    [switch]$SkipLargeCsv
)

# Colors and formatting
function Write-Note($msg) { Write-Host "[*] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[✓] $msg" -ForegroundColor Green }
function Write-Err($msg) { Write-Host "[✗] $msg" -ForegroundColor Red }
function Write-Warn($msg) { Write-Host "[!] $msg" -ForegroundColor Yellow }
function Die($msg) { Write-Err $msg; exit 1 }

# JUnit XML results
$script:TestResults = @()
$script:StartTime = Get-Date

function Add-TestResult($Name, $Status, $Duration, $ErrorMessage = $null) {
    $script:TestResults += [PSCustomObject]@{
        Name = $Name
        Status = $Status
        Duration = $Duration
        Error = $ErrorMessage
        Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    }
}

function Write-JUnitXml($FilePath) {
    $totalTests = $script:TestResults.Count
    $failures = ($script:TestResults | Where-Object Status -eq "FAIL").Count
    $totalTime = (Get-Date) - $script:StartTime
    
    $xml = @"
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="LeadNest.API.SmokeTests" tests="$totalTests" failures="$failures" time="$($totalTime.TotalSeconds)">
"@
    
    foreach ($result in $script:TestResults) {
        $xml += "`n  <testcase name=`"$($result.Name)`" time=`"$($result.Duration)`">"
        if ($result.Status -eq "FAIL") {
            $escapedError = [System.Security.SecurityElement]::Escape($result.Error)
            $xml += "`n    <failure message=`"Test Failed`">$escapedError</failure>"
        }
        $xml += "`n  </testcase>"
    }
    
    $xml += "`n</testsuite>"
    $xml | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Note "JUnit XML report written to: $FilePath"
}

function Test-WithRetry($Name, $ScriptBlock, $MaxRetries = 3, $RetryDelay = 5) {
    $attempt = 1
    $testStart = Get-Date
    
    while ($attempt -le $MaxRetries) {
        try {
            $result = & $ScriptBlock
            $duration = ((Get-Date) - $testStart).TotalSeconds
            Add-TestResult -Name $Name -Status "PASS" -Duration $duration
            return $result
        }
        catch {
            if ($attempt -eq $MaxRetries) {
                $duration = ((Get-Date) - $testStart).TotalSeconds
                Add-TestResult -Name $Name -Status "FAIL" -Duration $duration -Error $_.Exception.Message
                throw
            }
            Write-Warn "$Name failed (attempt $attempt/$MaxRetries), retrying in $RetryDelay seconds..."
            Start-Sleep -Seconds $RetryDelay
            $attempt++
        }
    }
}

function Format-JsonResponse($Response) {
    try {
        $json = $Response | ConvertFrom-Json
        return ($json | ConvertTo-Json -Depth 10)
    }
    catch {
        return $Response
    }
}

Write-Host "🚀 LeadNest API Smoke Test Suite" -ForegroundColor Magenta
Write-Host "Base URL: $BaseUrl" -ForegroundColor Gray
Write-Host "Email: $Email" -ForegroundColor Gray
Write-Host "Skip Large CSV: $SkipLargeCsv" -ForegroundColor Gray
Write-Host ""

# Global variables
$TOKEN = $null
$AuthHeader = @{}

# Test 1: Health Check
Write-Note "Test 1: Health Check (/healthz)"
Test-WithRetry -Name "health_check" -ScriptBlock {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/healthz" -TimeoutSec 10
    if ($response.StatusCode -ne 200) {
        throw "/healthz returned status $($response.StatusCode)"
    }
    Write-Ok "Health check passed: $($response.Content)"
}

# Test 2: Ready Check (with retry for DB cold start)
Write-Note "Test 2: Ready Check (/readyz) - with retry for DB cold start"
Test-WithRetry -Name "ready_check" -MaxRetries 5 -RetryDelay 3 -ScriptBlock {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/readyz" -TimeoutSec 10
    if ($response.StatusCode -ne 200) {
        throw "/readyz returned status $($response.StatusCode): $(Format-JsonResponse $response.Content)"
    }
    Write-Ok "Ready check passed: $($response.Content)"
}

# Test 3: Authentication
Write-Note "Test 3: Authentication (/auth/login)"
Test-WithRetry -Name "authentication" -ScriptBlock {
    $loginBody = @{ email = $Email; password = $Password } | ConvertTo-Json
    $response = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$BaseUrl/auth/login" `
        -ContentType "application/json" -Body $loginBody -TimeoutSec 10
    
    if ($response.StatusCode -ne 200) {
        throw "Login failed with status $($response.StatusCode): $(Format-JsonResponse $response.Content)"
    }
    
    $loginJson = $response.Content | ConvertFrom-Json
    $script:TOKEN = $loginJson.token
    
    if (-not $script:TOKEN) {
        throw "No token in login response: $(Format-JsonResponse $response.Content)"
    }
    
    $script:AuthHeader = @{ "Authorization" = "Bearer $script:TOKEN" }
    Write-Ok "Authentication successful, token obtained"
}

# Test 4: Protected Endpoint
Write-Note "Test 4: Protected Endpoint (/leads)"
Test-WithRetry -Name "protected_leads" -ScriptBlock {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/leads" -Headers $script:AuthHeader -TimeoutSec 10
    if ($response.StatusCode -ne 200) {
        throw "/leads returned status $($response.StatusCode): $(Format-JsonResponse $response.Content)"
    }
    $leads = $response.Content | ConvertFrom-Json
    Write-Ok "Leads endpoint OK, returned $($leads.Count) leads"
}

# Test 5: Idempotency
Write-Note "Test 5: Idempotency Testing (/leads/bulk with Idempotency-Key)"
Test-WithRetry -Name "idempotency_test" -ScriptBlock {
    $idemKey = "ps1-test-$(Get-Date -UFormat %s)-$([guid]::NewGuid().ToString('N').Substring(0,8))"
    $jsonBody = @(
        @{ full_name = "Idem Test PowerShell"; email = "idem.ps1@example.com"; source = "ps1-test"; status = "new" }
    ) | ConvertTo-Json
    
    $headers = $script:AuthHeader + @{ 
        "Content-Type" = "application/json"
        "Idempotency-Key" = $idemKey 
    }
    
    # First request
    $response1 = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$BaseUrl/leads/bulk" `
        -Headers $headers -Body $jsonBody -TimeoutSec 10
    
    if ($response1.StatusCode -ne 200) {
        throw "First idempotency request failed: $($response1.StatusCode) $(Format-JsonResponse $response1.Content)"
    }
    
    $result1 = $response1.Content | ConvertFrom-Json
    Write-Ok "First request: created=$($result1.created) updated=$($result1.updated)"
    
    # Second request (should be idempotent)
    $response2 = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$BaseUrl/leads/bulk" `
        -Headers $headers -Body $jsonBody -TimeoutSec 10
    
    if ($response2.StatusCode -ne 200) {
        throw "Second idempotency request failed: $($response2.StatusCode) $(Format-JsonResponse $response2.Content)"
    }
    
    $result2 = $response2.Content | ConvertFrom-Json
    if (-not $result2.idempotent) {
        throw "Expected idempotent=true on second request, got: $(Format-JsonResponse $response2.Content)"
    }
    
    Write-Ok "Idempotency test passed: second request properly marked as idempotent"
}

# Test 6: Small CSV Import
Write-Note "Test 6: Small CSV Import (/leads/bulk with file)"
Test-WithRetry -Name "csv_small_import" -ScriptBlock {
    $csvPath = Join-Path $env:TEMP "leads_small_$(Get-Date -UFormat %s).csv"
    $csvContent = @'
full_name,email,phone,source,status
PS Test One,ps1-one@example.com,,csv-test,new
PS Test Two,ps1-two@example.com,+15550123456,csv-test,contacted
PS Test Three,ps1-three@example.com,+15550123457,csv-test,qualified
'@
    
    $csvContent | Out-File -FilePath $csvPath -Encoding UTF8
    
    try {
        $curlOutput = & curl.exe -s -X POST "$BaseUrl/leads/bulk" `
            -H "Authorization: Bearer $script:TOKEN" `
            -F "file=@`"$csvPath`"" 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            throw "curl failed with exit code ${LASTEXITCODE}: $curlOutput"
        }
        
        $result = $curlOutput | ConvertFrom-Json
        if (-not $result.created -and -not $result.updated) {
            throw "Unexpected CSV import result: $(Format-JsonResponse $curlOutput)"
        }
        
        Write-Ok "CSV import successful: created=$($result.created) updated=$($result.updated) errors=$($result.errors.Count)"
    }
    finally {
        if (Test-Path $csvPath) { Remove-Item $csvPath -Force }
    }
}

# Test 7: Large CSV Import (Background Job) - Optional
if (-not $SkipLargeCsv) {
    Write-Note "Test 7: Large CSV Import - Background Job (>5000 rows)"
    Test-WithRetry -Name "csv_large_background" -ScriptBlock {
        $largeCsvPath = Join-Path $env:TEMP "leads_large_$(Get-Date -UFormat %s).csv"
        
        try {
            Write-Note "Generating large CSV file with 5100 rows..."
            "full_name,email,phone,source,status" | Out-File -FilePath $largeCsvPath -Encoding UTF8
            
            for ($i = 1; $i -le 5100; $i++) {
                $phone = "+1888{0:D4}" -f $i
                "PS Large $i,ps-large-$i@bigcsv.test,$phone,bg-test,new" | Add-Content -Path $largeCsvPath -Encoding UTF8
            }
            
            Write-Note "Uploading large CSV (should enqueue background job)..."
            $curlOutput = & curl.exe -s -X POST "$BaseUrl/leads/bulk" `
                -H "Authorization: Bearer $script:TOKEN" `
                -F "file=@`"$largeCsvPath`"" 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                throw "curl failed with exit code ${LASTEXITCODE}: $curlOutput"
            }
            
            $result = $curlOutput | ConvertFrom-Json
            if ($result.status -ne "enqueued" -or -not $result.job_id) {
                throw "Expected enqueued job, got: $(Format-JsonResponse $curlOutput)"
            }
            
            Write-Ok "Job enqueued successfully: $($result.job_id)"
            
            # Test 8: Job Polling
            Write-Note "Test 8: Job Polling (/jobs/{id})"
            $jobId = $result.job_id
            $deadline = (Get-Date).AddSeconds($PollTimeoutS)
            $pollCount = 0
            
            do {
                Start-Sleep -Seconds $PollSeconds
                $pollCount++
                
                $jobResponse = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/jobs/$jobId" `
                    -Headers $script:AuthHeader -TimeoutSec 10
                
                if ($jobResponse.StatusCode -ne 200) {
                    throw "Job status check failed: $($jobResponse.StatusCode) $(Format-JsonResponse $jobResponse.Content)"
                }
                
                $jobStatus = $jobResponse.Content | ConvertFrom-Json
                Write-Note "Job $($jobStatus.id): $($jobStatus.status) (poll #$pollCount)"
                
                if ($jobStatus.status -eq "finished") {
                    Write-Ok "Job completed successfully!"
                    if ($jobStatus.result) {
                        Write-Ok "Job result: created=$($jobStatus.result.created) updated=$($jobStatus.result.updated)"
                    }
                    break
                }
                elseif ($jobStatus.status -eq "failed") {
                    throw "Job failed: $($jobStatus.error)"
                }
                
            } while ((Get-Date) -lt $deadline)
            
            if ((Get-Date) -ge $deadline) {
                throw "Job polling timed out after $PollTimeoutS seconds"
            }
        }
        finally {
            if (Test-Path $largeCsvPath) { Remove-Item $largeCsvPath -Force }
        }
    }
    
    # Add separate test result for job polling
    Add-TestResult -Name "job_polling" -Status "PASS" -Duration 0
}
else {
    Write-Warn "Skipping large CSV and job polling tests (--SkipLargeCsv specified)"
    Add-TestResult -Name "csv_large_background" -Status "SKIP" -Duration 0
    Add-TestResult -Name "job_polling" -Status "SKIP" -Duration 0
}

# Test 9: Twilio Webhook Simulation
Write-Note "Test 9: Twilio Webhook Simulation (/twilio/inbound)"
if (-not $env:TWILIO_AUTH_TOKEN) {
    Test-WithRetry -Name "twilio_inbound_unsigned" -ScriptBlock {
        $twilioBody = "From=%2B15555550123&To=%2B15550000000&Body=Test+message+from+PowerShell"
        $response = Invoke-WebRequest -UseBasicParsing -Method POST -Uri "$BaseUrl/twilio/inbound" `
            -ContentType "application/x-www-form-urlencoded" -Body $twilioBody -TimeoutSec 10
        
        if ($response.StatusCode -eq 200) {
            Write-Ok "Twilio inbound webhook accepted (unsigned local test)"
        }
        elseif ($response.StatusCode -eq 403) {
            Write-Warn "Twilio webhook returned 403 (signature validation enabled)"
        }
        else {
            throw "Unexpected Twilio webhook response: $($response.StatusCode) $(Format-JsonResponse $response.Content)"
        }
    }
}
else {
    Write-Warn "TWILIO_AUTH_TOKEN is set; skipping unsigned webhook test (signature validation enforced)"
    Add-TestResult -Name "twilio_inbound_unsigned" -Status "SKIP" -Duration 0
}

# Summary
Write-Host ""
Write-Host "📊 Test Summary" -ForegroundColor Magenta
Write-Host "===============" -ForegroundColor Magenta

$passCount = ($script:TestResults | Where-Object Status -eq "PASS").Count
$failCount = ($script:TestResults | Where-Object Status -eq "FAIL").Count
$skipCount = ($script:TestResults | Where-Object Status -eq "SKIP").Count
$totalCount = $script:TestResults.Count

Write-Host "Total Tests: $totalCount" -ForegroundColor Gray
Write-Host "Passed: $passCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host "Skipped: $skipCount" -ForegroundColor Yellow

if ($failCount -gt 0) {
    Write-Host ""
    Write-Host "❌ FAILED TESTS:" -ForegroundColor Red
    $script:TestResults | Where-Object Status -eq "FAIL" | ForEach-Object {
        Write-Host "  • $($_.Name): $($_.Error)" -ForegroundColor Red
    }
}

# Write JUnit XML report
$reportPath = Join-Path (Get-Location) "Test-LeadNest.xml"
Write-JUnitXml -FilePath $reportPath

Write-Host ""
if ($failCount -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "💥 $failCount TEST(S) FAILED!" -ForegroundColor Red
    exit 1
}
