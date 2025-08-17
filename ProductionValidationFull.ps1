# Production Deployment Tests - LeadNest API
# This script validates all production endpoints and functionality

$baseUrl = "https://api.useleadnest.com"
$frontendUrl = "https://useleadnest.com"

Write-Host "`n=== PRODUCTION DEPLOYMENT VALIDATION ===" -ForegroundColor Green
Write-Host "API Base: $baseUrl" -ForegroundColor Yellow
Write-Host "Frontend: $frontendUrl" -ForegroundColor Yellow

# Test 1: Health endpoints
Write-Host "`n1. HEALTH CHECKS" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/healthz" -Method GET
    Write-Host "✓ /healthz: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ /healthz failed: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $ready = Invoke-RestMethod -Uri "$baseUrl/readyz" -Method GET
    Write-Host "✓ /readyz: $($ready.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ /readyz failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Authentication
Write-Host "`n2. AUTHENTICATION TEST" -ForegroundColor Cyan
try {
    $authBody = @{
        email = "test@example.com"
        password = "testpass"
    } | ConvertTo-Json

    $authResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method POST -ContentType "application/json" -Body $authBody
    $token = $authResponse.token
    Write-Host "✓ Login successful, token: $($token.Substring(0, 50))..." -ForegroundColor Green
    
    # Test protected endpoint
    $headers = @{ Authorization = "Bearer $token" }
    $leads = Invoke-RestMethod -Uri "$baseUrl/api/leads" -Method GET -Headers $headers
    Write-Host "✓ Protected route /api/leads: $($leads.Count) leads returned" -ForegroundColor Green
    
} catch {
    Write-Host "✗ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    $token = $null
}

# Test 3: CORS Check
Write-Host "`n3. CORS VALIDATION" -ForegroundColor Cyan
try {
    $corsResponse = Invoke-WebRequest -Uri "$baseUrl/api/auth/login" -Method OPTIONS -Headers @{
        "Origin" = $frontendUrl
        "Access-Control-Request-Method" = "POST"
        "Access-Control-Request-Headers" = "Content-Type"
    }
    $corsOrigin = $corsResponse.Headers["Access-Control-Allow-Origin"]
    Write-Host "✓ CORS enabled for origin: $corsOrigin" -ForegroundColor Green
} catch {
    Write-Host "✗ CORS test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Twilio webhook endpoint
Write-Host "`n4. TWILIO WEBHOOK TEST" -ForegroundColor Cyan
try {
    $twilioBody = @{
        From = "+15551234567"
        To = "+15559876543"
        Body = "Test inbound message"
    }
    
    $twilioResponse = Invoke-RestMethod -Uri "$baseUrl/api/twilio/inbound" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $twilioBody
    Write-Host "✓ Twilio inbound webhook: Response received" -ForegroundColor Green
} catch {
    Write-Host "✗ Twilio webhook failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Background job endpoint (if token available)
if ($token) {
    Write-Host "`n5. BACKGROUND JOB TEST" -ForegroundColor Cyan
    try {
        $headers = @{ 
            Authorization = "Bearer $token"
            "Content-Type" = "application/json"
            "Idempotency-Key" = [System.Guid]::NewGuid().ToString()
        }
        
        # Small CSV data for testing
        $csvData = @"
name,email,phone,company
John Doe,john@example.com,+1234567890,Acme Corp
Jane Smith,jane@example.com,+0987654321,Beta Inc
"@
        
        $jobBody = @{
            data = $csvData
            format = "csv"
        } | ConvertTo-Json
        
        $jobResponse = Invoke-RestMethod -Uri "$baseUrl/api/leads/bulk" -Method POST -Headers $headers -Body $jobBody
        Write-Host "✓ Bulk import job created: ID $($jobResponse.job_id)" -ForegroundColor Green
        
        # Check job status
        Start-Sleep -Seconds 2
        $jobStatus = Invoke-RestMethod -Uri "$baseUrl/api/jobs/$($jobResponse.job_id)" -Method GET -Headers @{ Authorization = "Bearer $token" }
        Write-Host "✓ Job status: $($jobStatus.status)" -ForegroundColor Green
        
    } catch {
        Write-Host "✗ Background job test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== VALIDATION COMPLETE ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Update Vercel frontend env vars: VITE_API_BASE_URL=$baseUrl/api"
Write-Host "2. Configure Twilio webhook: $baseUrl/api/twilio/inbound"
Write-Host "3. Enable Render autoscaling and daily backups"
Write-Host "4. Test frontend login flow manually"
