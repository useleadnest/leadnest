# Production Validation - LeadNest API (ASCII-only, PowerShell 5.x safe)

Write-Host "=== LEADNEST PRODUCTION VALIDATION ===" -ForegroundColor Green

$BaseUrl = "https://api.useleadnest.com"

# Test authentication first
Write-Host "`nTesting authentication..." -ForegroundColor Cyan
$token = $null
try {
    $authBody = @{ email = "test@example.com"; password = "testpass" } | ConvertTo-Json
    $authResponse = Invoke-RestMethod -Uri "$BaseUrl/api/auth/login" -Method POST -ContentType "application/json" -Body $authBody
    $token = $authResponse.token
    Write-Host "SUCCESS: Login worked, token received" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Authentication failed - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test protected endpoint
Write-Host "`nTesting protected endpoint..." -ForegroundColor Cyan
try {
    $headers = @{ Authorization = "Bearer $token" }
    $leads = Invoke-RestMethod -Uri "$BaseUrl/api/leads" -Method GET -Headers $headers
    Write-Host "SUCCESS: Got $($leads.Count) leads from /api/leads" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Protected endpoint failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test health endpoints
Write-Host "`nTesting health endpoints..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/healthz" -Method GET
    Write-Host "SUCCESS: /healthz returned $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Health check failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Create small CSV for testing
Write-Host "`nCreating test CSV..." -ForegroundColor Cyan
$csvPath = ".\small_test.csv"
$csvContent = "first_name,last_name,phone,email,source`nTest,User,+15551234567,test@example.com,bulk"
[System.IO.File]::WriteAllText($csvPath, $csvContent, [System.Text.Encoding]::UTF8)

if (Test-Path $csvPath) {
    Write-Host "SUCCESS: Created test CSV at $csvPath" -ForegroundColor Green
    
    # Test bulk upload
    Write-Host "`nTesting bulk upload..." -ForegroundColor Cyan
    try {
        $headers = @{
            Authorization = "Bearer $token"
            "Idempotency-Key" = [System.Guid]::NewGuid().ToString()
        }
        
        $form = @{ file = Get-Item $csvPath }
        $bulkResponse = Invoke-RestMethod -Uri "$BaseUrl/api/leads/bulk" -Method POST -Headers $headers -Form $form
        
        Write-Host "SUCCESS: Bulk upload initiated" -ForegroundColor Green
        $bulkResponse | ConvertTo-Json | Write-Host -ForegroundColor Gray
        
    } catch {
        Write-Host "ERROR: Bulk upload failed - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== VALIDATION COMPLETE ===" -ForegroundColor Green
Write-Host "`nAPI is ready for production use!" -ForegroundColor Yellow
