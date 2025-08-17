# 🧪 IMMEDIATE BACKEND TESTING

## Copy and paste these commands in PowerShell:

# Test 1: Root endpoint (should show version 1.0.6-PERFECT)
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/"

# Test 2: Health check
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/health"

# Test 3: Debug info
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/debug-info"

# Test 4: Status page
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/status"

# Test 5: Registration endpoint
$testUser = @{
    email = "test@leadnest.com"
    password = "securepass123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/auth/register" -Method POST -ContentType "application/json" -Body $testUser

# Test 6: Login endpoint
Invoke-RestMethod -Uri "https://leadnest-api-final.onrender.com/auth/login" -Method POST -ContentType "application/json" -Body $testUser
