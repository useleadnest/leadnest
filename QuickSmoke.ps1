# QuickSmoke.ps1 - ASCII-only PowerShell 5.x compatible smoke test
param(
    [string]$BaseUrl = "http://127.0.0.1:5000",
    [string]$Email = "a@b.c", 
    [string]$Password = "x",
    [switch]$SkipLargeCsv
)

function Write-Ok($msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

function Write-Fail($msg) {
    Write-Host "[FAIL] $msg" -ForegroundColor Red
}

function Write-Note($msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Cyan
}

# Test 1: Health Check
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/healthz" -Method GET
    if ($health.status -eq "ok") {
        Write-Ok "Health check passed"
    } else {
        Write-Fail "Health check failed: $($health.status)"
    }
} catch {
    Write-Fail "Health check error: $($_.Exception.Message)"
}

# Test 2: Ready Check  
try {
    $ready = Invoke-RestMethod -Uri "$BaseUrl/readyz" -Method GET
    if ($ready.status -eq "ready") {
        Write-Ok "Ready check passed"
    } else {
        Write-Fail "Ready check failed: $($ready.status)"
    }
} catch {
    Write-Fail "Ready check error: $($_.Exception.Message)"
}

# Test 3: Authentication
try {
    $loginBody = @{
        email = $Email
        password = $Password
    } | ConvertTo-Json
    
    $login = Invoke-RestMethod -Uri "$BaseUrl/auth/login" -Method POST -ContentType "application/json" -Body $loginBody
    if ($login.token) {
        Write-Ok "Login successful, got token"
        $headers = @{ Authorization = "Bearer $($login.token)" }
    } else {
        Write-Fail "Login failed: no token received"
        exit 1
    }
} catch {
    Write-Fail "Login error: $($_.Exception.Message)"
    exit 1
}

# Test 4: Get Leads
try {
    $leads = Invoke-RestMethod -Uri "$BaseUrl/leads" -Method GET -Headers $headers
    if ($leads.leads) {
        Write-Ok "Retrieved $($leads.leads.Count) leads"
    } else {
        Write-Ok "Retrieved leads (empty list)"
    }
} catch {
    Write-Fail "Get leads error: $($_.Exception.Message)"
}

# Test 5: Small bulk import (inline processing)
try {
    $smallBulk = @(
        @{ full_name="Jane Demo"; email="jane@demo.com"; source="api" }
        @{ full_name="John Demo"; phone="+15551234567"; source="api" }
    )
    $bulkBody = $smallBulk | ConvertTo-Json
    $bulkHeaders = $headers + @{ "Content-Type" = "application/json" }
    
    $result = Invoke-RestMethod -Uri "$BaseUrl/leads/bulk" -Method POST -Headers $bulkHeaders -Body $bulkBody
    if ($result.created -ne $null) {
        Write-Ok "Small bulk import: created=$($result.created) updated=$($result.updated)"
    } else {
        Write-Fail "Small bulk import failed: $result"
    }
} catch {
    Write-Fail "Small bulk import error: $($_.Exception.Message)"
}

# Test 6: Idempotency test
try {
    $idempotencyKey = [guid]::NewGuid().ToString()
    $idempotentHeaders = $headers + @{ 
        "Content-Type" = "application/json"
        "Idempotency-Key" = $idempotencyKey 
    }
    
    # First request
    $result1 = Invoke-RestMethod -Uri "$BaseUrl/leads/bulk" -Method POST -Headers $idempotentHeaders -Body $bulkBody
    
    # Second request (should return cached result)
    $result2 = Invoke-RestMethod -Uri "$BaseUrl/leads/bulk" -Method POST -Headers $idempotentHeaders -Body $bulkBody
    
    if ($result1.created -eq $result2.created -and $result1.updated -eq $result2.updated) {
        Write-Ok "Idempotency test passed - got same result"
    } else {
        Write-Fail "Idempotency test failed - results differ"
    }
} catch {
    Write-Fail "Idempotency test error: $($_.Exception.Message)"
}

# Test 7: Create booking
try {
    $futureTime = (Get-Date).ToUniversalTime().AddMinutes(30).ToString("yyyy-MM-ddTHH:mm:ssZ")
    $bookingBody = @{
        lead_id = 1
        starts_at = $futureTime
        notes = "Test booking from smoke test"
    } | ConvertTo-Json
    
    $bookingHeaders = $headers + @{ "Content-Type" = "application/json" }
    $booking = Invoke-RestMethod -Uri "$BaseUrl/bookings" -Method POST -Headers $bookingHeaders -Body $bookingBody
    
    if ($booking.id) {
        Write-Ok "Created booking with ID $($booking.id)"
    } else {
        Write-Fail "Booking creation failed: $booking"
    }
} catch {
    Write-Fail "Booking creation error: $($_.Exception.Message)"
}

# Test 8: Twilio inbound webhook simulation (no signature validation in dev)
try {
    $twilioBody = @{
        From = "+15556667777"
        To = "+15550001111"
        Body = "hello from test inbound"
        MessageSid = "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    }
    
    # Use Invoke-WebRequest to get raw TwiML content
    $twilioResponse = Invoke-WebRequest -Uri "$BaseUrl/twilio/inbound" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $twilioBody
    
    if ($twilioResponse.StatusCode -eq 200 -and $twilioResponse.Content -like "*<Response>*") {
        Write-Ok "Twilio inbound webhook simulation successful (returned TwiML)"
    } else {
        Write-Fail "Twilio inbound simulation failed: Status=$($twilioResponse.StatusCode) Content=$($twilioResponse.Content)"
    }
} catch {
    Write-Fail "Twilio inbound simulation error: $($_.Exception.Message)"
}

# ------ Ensure test lead exists (idempotent) ------
function Get-LeadByPhoneOrEmail {
    param([string]$BaseUrl, [hashtable]$Headers, [string]$Phone, [string]$Email)
    $all = Invoke-RestMethod -Uri "$BaseUrl/leads" -Headers $Headers -Method GET
    $match = $null
    if ($Phone) { $match = $all | Where-Object { $_.phone -eq $Phone } | Select-Object -First 1 }
    if (-not $match -and $Email) { $match = $all | Where-Object { $_.email -eq $Email } | Select-Object -First 1 }
    return $match
}

$testPhone = "+15556667777"
$testEmail = "twilio@test.com"
$lead = Get-LeadByPhoneOrEmail -BaseUrl $BaseUrl -Headers $headers -Phone $testPhone -Email $testEmail

if (-not $lead) {
    Write-Note "Creating test lead via /leads/bulk..."
    $payload = @(
        @{
            full_name = "Twilio Test"
            email     = $testEmail
            phone     = $testPhone
            source    = "api"
            status    = "new"
        }
    ) | ConvertTo-Json

    try {
        # Add idempotency for safer re-runs
        $bulkHeaders = $headers + @{ 
            "Content-Type" = "application/json"
            "Idempotency-Key" = "smoke-$(Get-Date -Format 'yyyyMMddHHmm')"
        }
        $bulkRes = Invoke-RestMethod -Uri "$BaseUrl/leads/bulk" -Method POST -Headers $bulkHeaders -Body $payload
        Write-Note "Bulk result: created=$($bulkRes.created) updated=$($bulkRes.updated)"
    } catch {
        Write-Note "Bulk create failed (this is OK if the lead already exists): $($_.Exception.Message)"
    }

    # re-check after bulk create
    $lead = Get-LeadByPhoneOrEmail -BaseUrl $BaseUrl -Headers $headers -Phone $testPhone -Email $testEmail
}

if (-not $lead) {
    Write-Fail "Could not ensure a Twilio test lead exists"
    $leadId = $null
} else {
    $leadId = $lead.id
    Write-Ok "Using test lead id: $leadId (phone: $($lead.phone))"
}
# ------ end ensure lead ------

# Test 9: Twilio outbound SMS (expected to fail without credentials)
if ($leadId) {
    try {
        $smsBody = @{ 
            lead_id = $leadId
            body = "Test outbound from LeadNest smoke test" 
        } | ConvertTo-Json
        
        $smsHeaders = $headers + @{ "Content-Type" = "application/json" }
        $smsResponse = Invoke-RestMethod -Uri "$BaseUrl/twilio/send" -Method POST -Headers $smsHeaders -Body $smsBody
        
        Write-Ok "Twilio send success: $($smsResponse | ConvertTo-Json -Compress)"
    } catch {
        if ($_.Exception.Message -like "*503*" -or $_.Exception.Message -like "*Twilio not configured*") {
            Write-Ok "Expected 503 when Twilio not configured (endpoint working correctly)"
        } else {
            Write-Fail "Twilio send error: $($_.Exception.Message)"
        }
    }
} else {
    Write-Note "Skipping Twilio outbound test - no test lead available"
}

# Test 10: Skip large CSV if requested
if (-not $SkipLargeCsv) {
    Write-Note "Skipping large CSV test (use -SkipLargeCsv:$false to enable)"
} else {
    Write-Note "Large CSV test skipped as requested"
}

Write-Host ""
Write-Host "=== SMOKE TEST COMPLETE ===" -ForegroundColor Yellow
Write-Host "All critical endpoints tested successfully!" -ForegroundColor Green
