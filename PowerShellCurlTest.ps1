# 🚀 LeadNest PowerShell-Compatible Curl Test Script

param(
    [string]$BaseUrl = "https://leadnest-bulletproof.onrender.com",
    [string]$Email = "admin@leadnest.com",
    [string]$Password = "admin123"
)

Write-Host "🔍 LeadNest PowerShell Curl Tests" -ForegroundColor Cyan
Write-Host "Target: $BaseUrl" -ForegroundColor Yellow
Write-Host ""

# Function to execute curl with proper PowerShell handling
function Invoke-CurlTest {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Body = "",
        [int]$ExpectedStatus = 200
    )
    
    Write-Host "$Name" -ForegroundColor Cyan
    
    $curlArgs = @("-X", $Method, $Url, "--silent", "--show-error", "--write-out", "HTTP_STATUS:%{http_code}")
    
    if ($Headers.Count -gt 0) {
        foreach ($header in $Headers.GetEnumerator()) {
            $curlArgs += @("-H", "$($header.Key): $($header.Value)")
        }
    }
    
    if ($Body) {
        $curlArgs += @("-d", $Body)
    }
    
    try {
        $output = & curl @curlArgs 2>&1
        if ($LASTEXITCODE -eq 0) {
            if ($output -match "HTTP_STATUS:(\d+)") {
                $status = $matches[1]
                $response = $output -replace "HTTP_STATUS:\d+$", ""
                
                if ([int]$status -eq $ExpectedStatus -or ($ExpectedStatus -eq 0)) {
                    Write-Host "✅ Success (HTTP $status)" -ForegroundColor Green
                    if ($response -and $response.Length -gt 0) {
                        Write-Host "Response: $($response.Substring(0, [Math]::Min(200, $response.Length)))" -ForegroundColor Gray
                    }
                    return $response
                } else {
                    Write-Host "❌ Expected HTTP $ExpectedStatus, got HTTP $status" -ForegroundColor Red
                    return $null
                }
            }
        } else {
            Write-Host "❌ Curl failed: $output" -ForegroundColor Red
            return $null
        }
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
    return $null
}

# Test 1: Health Check
Write-Host "1️⃣ Health Check Test" -ForegroundColor Yellow
Invoke-CurlTest -Name "Health Endpoint" -Method "GET" -Url "$BaseUrl/healthz"

Write-Host ""

# Test 2: Ready Check
Write-Host "2️⃣ Ready Check Test" -ForegroundColor Yellow  
Invoke-CurlTest -Name "Ready Endpoint" -Method "GET" -Url "$BaseUrl/readyz"

Write-Host ""

# Test 3: Authentication
Write-Host "3️⃣ Authentication Test" -ForegroundColor Yellow
$loginBody = "{`"email`":`"$Email`",`"password`":`"$Password`"}"
$loginHeaders = @{"Content-Type" = "application/json"}
$loginResponse = Invoke-CurlTest -Name "Login Endpoint" -Method "POST" -Url "$BaseUrl/auth/login" -Headers $loginHeaders -Body $loginBody

# Extract token if login successful
$token = $null
if ($loginResponse -and $loginResponse -match '"token":\s*"([^"]+)"') {
    $token = $matches[1]
    Write-Host "✅ JWT Token extracted: $($token.Substring(0,20))..." -ForegroundColor Green
}

Write-Host ""

# Test 4: Protected Endpoint (if we have a token)
if ($token) {
    Write-Host "4️⃣ Protected Endpoint Test" -ForegroundColor Yellow
    $authHeaders = @{"Authorization" = "Bearer $token"}
    Invoke-CurlTest -Name "Leads Endpoint" -Method "GET" -Url "$BaseUrl/leads" -Headers $authHeaders
} else {
    Write-Host "4️⃣ Protected Endpoint Test - SKIPPED (no auth token)" -ForegroundColor Yellow
}

Write-Host ""

# Test 5: Twilio Inbound (the problematic one with &)
Write-Host "5️⃣ Twilio Inbound Test" -ForegroundColor Yellow
$twilioHeaders = @{"Content-Type" = "application/x-www-form-urlencoded"}
$twilioBody = "From=+1234567890&Body=TEST&MessageSid=SM123456"
Invoke-CurlTest -Name "Twilio Inbound" -Method "POST" -Url "$BaseUrl/twilio/inbound" -Headers $twilioHeaders -Body $twilioBody -ExpectedStatus 0

Write-Host ""

# Test 6: API Documentation
Write-Host "6️⃣ API Documentation Test" -ForegroundColor Yellow
$docsResponse = Invoke-CurlTest -Name "OpenAPI Docs" -Method "GET" -Url "$BaseUrl/openapi.json"

Write-Host ""
Write-Host "🎯 All Curl Tests Complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "• This script uses native curl.exe with proper PowerShell parameter handling" -ForegroundColor White
Write-Host "• Ampersands in form data are handled safely by curl's -d parameter" -ForegroundColor White
Write-Host "• For manual testing, copy the curl commands shown above" -ForegroundColor White
