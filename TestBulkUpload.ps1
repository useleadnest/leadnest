# Test CSV Bulk Upload - Production Ready
# This script demonstrates both CSV generation and upload using curl

Write-Host "=== CSV BULK UPLOAD TEST ===" -ForegroundColor Green

# Step 1: Generate a test CSV
Write-Host "`n1. Generating test CSV..." -ForegroundColor Cyan
$csvPath = "bulk_test.csv"
$csvContent = @"
first_name,last_name,phone,email,source
John,Doe,+15551111111,john.doe@example.com,bulk_import
Jane,Smith,+15552222222,jane.smith@example.com,bulk_import
Bob,Johnson,+15553333333,bob.johnson@example.com,bulk_import
Alice,Wilson,+15554444444,alice.wilson@example.com,bulk_import
Charlie,Brown,+15555555555,charlie.brown@example.com,bulk_import
"@

[System.IO.File]::WriteAllText($csvPath, $csvContent, [System.Text.Encoding]::UTF8)
Write-Host "Created $csvPath" -ForegroundColor Green

# Step 2: Get authentication token
Write-Host "`n2. Getting authentication token..." -ForegroundColor Cyan
try {
    $authBody = @{ email = "test@example.com"; password = "testpass" } | ConvertTo-Json
    $auth = Invoke-RestMethod -Uri "https://api.useleadnest.com/api/auth/login" -Method POST -ContentType "application/json" -Body $authBody
    $token = $auth.token
    Write-Host "Token obtained: $($token.Substring(0,20))..." -ForegroundColor Green
} catch {
    Write-Host "Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Upload using curl
Write-Host "`n3. Uploading CSV with curl..." -ForegroundColor Cyan
$idempotencyKey = [System.Guid]::NewGuid().ToString()

try {
    $curlResult = curl.exe -s -X POST "https://api.useleadnest.com/api/leads/bulk" -H "Authorization: Bearer $token" -H "Idempotency-Key: $idempotencyKey" -F "file=@$csvPath"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Upload successful!" -ForegroundColor Green
        $response = $curlResult | ConvertFrom-Json
        Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Gray
        
        # Step 4: Check job status if job_id returned
        if ($response.job_id) {
            Write-Host "`n4. Checking job status..." -ForegroundColor Cyan
            Start-Sleep -Seconds 2
            
            $jobStatus = Invoke-RestMethod -Uri "https://api.useleadnest.com/api/jobs/$($response.job_id)" -Method GET -Headers @{ Authorization = "Bearer $token" }
            Write-Host "Job status: $($jobStatus.status)" -ForegroundColor Green
            $jobStatus | ConvertTo-Json | Write-Host -ForegroundColor Gray
        }
    } else {
        Write-Host "Upload failed with curl exit code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Response: $curlResult" -ForegroundColor Red
    }
} catch {
    Write-Host "Upload error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Green

# Cleanup
if (Test-Path $csvPath) {
    Remove-Item $csvPath
    Write-Host "Cleaned up test file" -ForegroundColor Gray
}
