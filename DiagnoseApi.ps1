# LeadNest API Diagnosis Script
param(
    [string]$ApiDomain = "leadnest-api.onrender.com"
)

Write-Host "=== LeadNest API Diagnosis ===" -ForegroundColor Yellow
Write-Host "Testing API at: https://$ApiDomain" -ForegroundColor Green
Write-Host ""

# Test endpoints to try
$endpoints = @(
    "/",
    "/healthz", 
    "/health",
    "/api/healthz",
    "/api/health"
)

foreach ($endpoint in $endpoints) {
    $url = "https://$ApiDomain$endpoint"
    Write-Host "Testing: $url" -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -ErrorAction Stop
        Write-Host "  SUCCESS: Status $($response.StatusCode)" -ForegroundColor Green
        Write-Host "  Response: $($response.Content)" -ForegroundColor White
    }
    catch {
        $errorDetails = $_.Exception.Message
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode.value__
            Write-Host "  ERROR: Status $statusCode - $errorDetails" -ForegroundColor Red
        }
        else {
            Write-Host "  ERROR: $errorDetails" -ForegroundColor Red
        }
    }
    Write-Host ""
}

Write-Host "=== DNS/Connection Test ===" -ForegroundColor Yellow
try {
    $dnsResult = Resolve-DnsName -Name $ApiDomain -ErrorAction Stop
    Write-Host "DNS Resolution: SUCCESS" -ForegroundColor Green
    Write-Host "IP Address: $($dnsResult[0].IPAddress)" -ForegroundColor White
}
catch {
    Write-Host "DNS Resolution: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Port 443 Test ===" -ForegroundColor Yellow
try {
    $connection = Test-NetConnection -ComputerName $ApiDomain -Port 443 -ErrorAction Stop
    if ($connection.TcpTestSucceeded) {
        Write-Host "Port 443: OPEN" -ForegroundColor Green
    }
    else {
        Write-Host "Port 443: CLOSED" -ForegroundColor Red
    }
}
catch {
    Write-Host "Port Test: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}
