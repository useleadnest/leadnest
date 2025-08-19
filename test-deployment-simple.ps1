# DEPLOYMENT STATUS MONITOR

Write-Host "Checking LeadNest deployment status..." -ForegroundColor Cyan
Write-Host ""

# Test the health endpoint
$healthUrl = "https://api.useleadnest.com/healthz"
Write-Host "Testing: $healthUrl" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 10
    
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS! LeadNest is LIVE!" -ForegroundColor Green
        Write-Host "Response: $($response.Content)" -ForegroundColor Green
        Write-Host ""
        Write-Host "DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "Your API is now available at: https://api.useleadnest.com" -ForegroundColor Green
        
        # Test readiness endpoint too
        try {
            $readyResponse = Invoke-WebRequest -Uri "https://api.useleadnest.com/readyz" -UseBasicParsing -TimeoutSec 5
            Write-Host "Readiness check: $($readyResponse.Content)" -ForegroundColor Green
        } catch {
            Write-Host "Readiness check failed, but main health is OK" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Unexpected status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "Connection failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "This could mean:" -ForegroundColor Yellow
    Write-Host "  - Deployment is still in progress" -ForegroundColor Yellow
    Write-Host "  - Build failed (check Render dashboard)" -ForegroundColor Yellow
    Write-Host "  - DNS not yet propagated" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Check your Render dashboard for build logs" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Dashboard: https://dashboard.render.com" -ForegroundColor Cyan
