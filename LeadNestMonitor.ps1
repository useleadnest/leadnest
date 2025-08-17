# LeadNest Status Monitor
# Runs every 60 seconds to check API health and alert if issues found

param(
    [string]$ApiUrl = "https://api.useleadnest.com",
    [string]$SlackWebhook = "",  # Optional: Add Slack webhook URL for alerts
    [string]$LogFile = "leadnest-monitor.log"
)

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Log {
    param($Message, $Level = "INFO")
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $LogFile -Value $logEntry
}

function Send-Alert {
    param($Message)
    Write-Log "ALERT: $Message" "ERROR"
    
    if ($SlackWebhook) {
        $payload = @{ 
            text = "🚨 LeadNest Alert: $Message" 
            username = "LeadNest Monitor"
            icon_emoji = ":warning:"
        } | ConvertTo-Json
        
        try {
            Invoke-RestMethod -Uri $SlackWebhook -Method POST -Body $payload -ContentType "application/json"
            Write-Log "Alert sent to Slack" "INFO"
        } catch {
            Write-Log "Failed to send Slack alert: $($_.Exception.Message)" "ERROR"
        }
    }
}

# Health Check
try {
    $response = Invoke-RestMethod -Uri "$ApiUrl/healthz" -TimeoutSec 30
    if ($response.status -eq "healthy") {
        Write-Log "Health check passed" "INFO"
    } else {
        Send-Alert "Health check returned: $($response.status)"
    }
} catch {
    Send-Alert "Health check failed: $($_.Exception.Message)"
}

# Ready Check
try {
    $response = Invoke-RestMethod -Uri "$ApiUrl/readyz" -TimeoutSec 30
    if ($response.status -eq "ready") {
        Write-Log "Ready check passed" "INFO"
    } else {
        Send-Alert "Ready check returned: $($response.status)"
    }
} catch {
    Send-Alert "Ready check failed: $($_.Exception.Message)"
}

# API Response Time Check
try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    Invoke-RestMethod -Uri "$ApiUrl/healthz" -TimeoutSec 10 | Out-Null
    $stopwatch.Stop()
    $responseTime = $stopwatch.ElapsedMilliseconds
    
    Write-Log "API response time: ${responseTime}ms" "INFO"
    
    if ($responseTime -gt 5000) {
        Send-Alert "API response time is slow: ${responseTime}ms"
    }
} catch {
    Send-Alert "API response time check failed: $($_.Exception.Message)"
}

Write-Log "Monitor check complete" "INFO"
