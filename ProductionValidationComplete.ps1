# Production Deployment Validation - LeadNest API
# PowerShell 5.x compatible version

Write-Host "=== LEADNEST PRODUCTION DEPLOYMENT VALIDATION ===" -ForegroundColor Green
Write-Host "Date: $(Get-Date)" -ForegroundColor Yellow

$BaseUrl = "https://api.useleadnest.com"
$FrontendUrl = "https://useleadnest.com"

# Test 1: Generate CSV file first
Write-Host "`n1. GENERATING TEST CSV" -ForegroundColor Cyan
try {
    $csvPath = ".\test_leads_small.csv"
    $csvContent = "first_name,last_name,phone,email,source`n"
    $csvContent += "John,Doe,+15551234567,john.doe@example.com,bulk`n"
    $csvContent += "Jane,Smith,+15559876543,jane.smith@example.com,bulk`n"
    $csvContent += "Bob,Johnson,+15556547890,bob.johnson@example.com,bulk"
    
    [System.IO.File]::WriteAllText($csvPath, $csvContent, [System.Text.Encoding]::UTF8)
    
    if (Test-Path $csvPath) {
        $fileSize = (Get-Item $csvPath).Length
        Write-Host "✓ CSV generated: $csvPath ($fileSize bytes)" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ CSV generation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Health endpoints
Write-Host "`n2. HEALTH CHECKS" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/healthz" -Method GET
    Write-Host "✓ /healthz: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ /healthz failed: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $ready = Invoke-RestMethod -Uri "$BaseUrl/readyz" -Method GET
    Write-Host "✓ /readyz: $($ready.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ /readyz failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Authentication
Write-Host "`n3. AUTHENTICATION" -ForegroundColor Cyan
$token = $null
try {
    $authBody = @{
        email = "test@example.com"
        password = "testpass"
    } | ConvertTo-Json
    
    $authResponse = Invoke-RestMethod -Uri "$BaseUrl/api/auth/login" -Method POST -ContentType "application/json" -Body $authBody
    $token = $authResponse.token
    Write-Host "✓ Login successful, token length: $($token.Length)" -ForegroundColor Green
} catch {
    Write-Host "✗ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Protected endpoints
if ($token) {
    Write-Host "`n4. PROTECTED ENDPOINTS" -ForegroundColor Cyan
    $headers = @{ Authorization = "Bearer $token" }
    
    try {
        $leads = Invoke-RestMethod -Uri "$BaseUrl/api/leads" -Method GET -Headers $headers
        Write-Host "✓ /api/leads: $($leads.Count) leads returned" -ForegroundColor Green
    } catch {
        Write-Host "✗ /api/leads failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 5: Bulk upload test (if token and CSV available)
if ($token -and (Test-Path $csvPath)) {
    Write-Host "`n5. BULK UPLOAD TEST" -ForegroundColor Cyan
    try {
        $headers = @{
            Authorization = "Bearer $token"
            "Idempotency-Key" = [System.Guid]::NewGuid().ToString()
        }
        
        $form = @{ file = Get-Item $csvPath }
        $bulkResponse = Invoke-RestMethod -Uri "$BaseUrl/api/leads/bulk" -Method POST -Headers $headers -Form $form
        
        Write-Host "✓ Bulk upload response:" -ForegroundColor Green
        $bulkResponse | Format-List
        
        if ($bulkResponse.job_id) {
            Write-Host "Checking job status..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
            
            $jobStatus = Invoke-RestMethod -Uri "$BaseUrl/api/jobs/$($bulkResponse.job_id)" -Method GET -Headers @{ Authorization = "Bearer $token" }
            Write-Host "✓ Job status: $($jobStatus.status)" -ForegroundColor Green
            $jobStatus | Format-List
        }
        
    } catch {
        Write-Host "✗ Bulk upload failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 6: Twilio webhook simulation
Write-Host "`n6. TWILIO WEBHOOK TEST" -ForegroundColor Cyan
try {
    $twilioForm = @{
        From = "+15551234567"
        To = "+15559876543"
        Body = "Test inbound SMS from production validation"
    }
    
    $twilioResponse = Invoke-RestMethod -Uri "$BaseUrl/api/twilio/inbound" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $twilioForm
    Write-Host "✓ Twilio webhook responded successfully" -ForegroundColor Green
    Write-Host "Response: $($twilioResponse -replace "`n", " ")" -ForegroundColor Gray
} catch {
    Write-Host "✗ Twilio webhook failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: CORS check
Write-Host "`n7. CORS VALIDATION" -ForegroundColor Cyan
try {
    $corsRequest = @{
        Uri = "$BaseUrl/api/auth/login"
        Method = "OPTIONS"
        Headers = @{
            "Origin" = $FrontendUrl
            "Access-Control-Request-Method" = "POST"
            "Access-Control-Request-Headers" = "Content-Type"
        }
    }
    
    $corsResponse = Invoke-WebRequest @corsRequest
    $allowOrigin = $corsResponse.Headers["Access-Control-Allow-Origin"]
    if ($allowOrigin) {
        Write-Host "✓ CORS configured for origin: $allowOrigin" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ CORS validation failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== VALIDATION COMPLETE ===" -ForegroundColor Green

# Final instructions
Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. In Vercel dashboard, set environment variables:"
Write-Host "   VITE_API_BASE_URL = $BaseUrl/api"
Write-Host "   VITE_ENV_NAME = PROD"
Write-Host "2. Redeploy Vercel frontend"
Write-Host "3. In Twilio Console → Messaging → Webhooks:"
Write-Host "   URL: $BaseUrl/api/twilio/inbound"
Write-Host "   Method: POST"
Write-Host "4. In Render dashboard:"
Write-Host "   - Enable daily PostgreSQL snapshots"
Write-Host "   - Set autoscaling: CPU > 70%, min 1 instance"
Write-Host "   - Verify both web and worker services are running"
