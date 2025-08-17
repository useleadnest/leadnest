# SERVICE STATUS CHECKER

Write-Host "Checking if leadnest-api-final service is ready..."

# Check if service exists and is responding
try {
    $response = Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/" -TimeoutSec 10
    
    if ($response.version -eq "1.0.6-PERFECT") {
        Write-Host "SUCCESS! Service is live and perfect!"
        Write-Host "Version: $($response.version)"
        Write-Host "Status: $($response.status)"
        Write-Host "Database: $($response.database_available)"
        Write-Host ""
        Write-Host "Ready to run full testing suite!"
        return $true
    } else {
        Write-Host "Service is live but may not be latest version"
        Write-Host "Current version: $($response.version)"
        return $false
    }
} catch {
    Write-Host "Service not ready yet: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Please wait for deployment to complete, then run this check again."
    return $false
}

# If service is ready, show next steps
Write-Host ""
Write-Host "NEXT STEPS:"
Write-Host "1. Run comprehensive backend tests"
Write-Host "2. Redeploy frontend with new API URL"  
Write-Host "3. Test registration flow end-to-end"
