# DEPLOYMENT MONITOR - Tracks deployment progress

$serviceUrl = "https://leadnest-api-final.onrender.com/"
$maxChecks = 20
$checkInterval = 30  # seconds

Write-Host "Monitoring deployment of LeadNest API..."
Write-Host "Service URL: $serviceUrl"
Write-Host "Will check every $checkInterval seconds for up to $($maxChecks * $checkInterval / 60) minutes"
Write-Host ""

for ($i = 1; $i -le $maxChecks; $i++) {
    Write-Host "[$i/$maxChecks] Checking service status..."
    
    try {
        $response = Invoke-RestMethod -Uri $serviceUrl -TimeoutSec 10
        
        Write-Host "SERVICE IS LIVE!"
        Write-Host "Version: $($response.version)"
        Write-Host "Status: $($response.status)"
        Write-Host "Database: $($response.database_available)"
        Write-Host ""
        Write-Host "Ready to run automated tests!"
        Write-Host ""
        Write-Host "Starting comprehensive testing..."
        powershell -ExecutionPolicy Bypass .\AUTOMATED_TESTING.ps1
        break
        
    } catch {
        Write-Host "Not ready yet: $($_.Exception.Message)"
        
        if ($i -lt $maxChecks) {
            Write-Host "Waiting $checkInterval seconds before next check..."
            Start-Sleep -Seconds $checkInterval
        } else {
            Write-Host ""
            Write-Host "Max checks reached. Service may still be deploying."
            Write-Host "You can run this monitor again or check manually."
        }
    }
}

Write-Host ""
Write-Host "TIP: Once service is live, run AUTOMATED_TESTING.ps1 for full validation!"
