# LeadNest Documentation Package Creation Script
# Creates professional distribution packages for Developer, Client, and Investor materials

Write-Host "Creating LeadNest Distribution Packages..." -ForegroundColor Green

$rootPath = "C:\Users\mccab\contractornest"
$docsPath = "$rootPath\docs"
$distPath = "$rootPath\distribution"

# Create distribution directory
if (Test-Path $distPath) {
    Remove-Item $distPath -Recurse -Force
}
New-Item -ItemType Directory -Path $distPath | Out-Null

Write-Host "Creating Developer Package..." -ForegroundColor Yellow

# Create Developer Package
$devPackage = "$distPath\LeadNest-Developer-Package"
New-Item -ItemType Directory -Path $devPackage | Out-Null

# Copy developer files
Copy-Item "$docsPath\developer\*" $devPackage -Recurse

# Create ZIP
$devZip = "$distPath\LeadNest-Developer-Package.zip"
Compress-Archive -Path "$devPackage\*" -DestinationPath $devZip -Force

Write-Host "Developer Package created: LeadNest-Developer-Package.zip" -ForegroundColor Green

Write-Host "Creating Client Package..." -ForegroundColor Yellow

# Create Client Package  
$clientPackage = "$distPath\LeadNest-Client-Package"
New-Item -ItemType Directory -Path $clientPackage | Out-Null

# Copy client files
Copy-Item "$docsPath\client\*" $clientPackage -Recurse

# Create ZIP
$clientZip = "$distPath\LeadNest-Client-Package.zip"
Compress-Archive -Path "$clientPackage\*" -DestinationPath $clientZip -Force

Write-Host "Client Package created: LeadNest-Client-Package.zip" -ForegroundColor Green

Write-Host "Creating Investor Package..." -ForegroundColor Yellow

# Create Investor Package
$investorPackage = "$distPath\LeadNest-Investor-Package"
New-Item -ItemType Directory -Path $investorPackage | Out-Null

# Copy investor files
Copy-Item "$docsPath\investor\*" $investorPackage -Recurse

# Create ZIP
$investorZip = "$distPath\LeadNest-Investor-Package.zip"
Compress-Archive -Path "$investorPackage\*" -DestinationPath $investorZip -Force

Write-Host "Investor Package created: LeadNest-Investor-Package.zip" -ForegroundColor Green

Write-Host ""
Write-Host "All distribution packages created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Package Locations:" -ForegroundColor Cyan
Write-Host "   Developer Package: $devZip" -ForegroundColor White
Write-Host "   Client Package: $clientZip" -ForegroundColor White  
Write-Host "   Investor Package: $investorZip" -ForegroundColor White
Write-Host ""
Write-Host "Package Contents Summary:" -ForegroundColor Cyan
Write-Host ""
Write-Host "DEVELOPER PACKAGE:" -ForegroundColor Yellow
Write-Host "   Complete API Documentation with REST endpoints and authentication"
Write-Host "   HTTP Request Collection for immediate testing"
Write-Host "   Environment Configuration Template"
Write-Host "   React/TypeScript and Python Flask Integration Examples"
Write-Host "   Production Deployment Guide"
Write-Host ""
Write-Host "CLIENT PACKAGE:" -ForegroundColor Yellow  
Write-Host "   Complete User Guide with 15-minute setup to advanced features"
Write-Host "   30-Day Success Roadmap with week-by-week checklist"
Write-Host "   Success Metrics Template for tracking ROI"
Write-Host "   Industry-Specific Best Practices"
Write-Host "   Troubleshooting and Support Resources"
Write-Host ""
Write-Host "INVESTOR PACKAGE:" -ForegroundColor Yellow
Write-Host "   Executive Summary with complete business overview"
Write-Host "   One-Page Pitch Deck with concise investment opportunity"
Write-Host "   Financial Model Snapshot with unit economics and projections"
Write-Host "   Market Analysis with TAM/SAM breakdown"
Write-Host "   Team and Traction Details"
Write-Host ""
Write-Host "Ready for Distribution!" -ForegroundColor Green
Write-Host "These packages are now ready to email, print, or upload to investors, clients, and developers."
Write-Host ""

# Display file sizes
$devSize = [math]::Round((Get-Item $devZip).Length / 1MB, 2)
$clientSize = [math]::Round((Get-Item $clientZip).Length / 1MB, 2)  
$investorSize = [math]::Round((Get-Item $investorZip).Length / 1MB, 2)

Write-Host "Package Sizes:" -ForegroundColor Cyan
Write-Host "   Developer Package: $devSize MB"
Write-Host "   Client Package: $clientSize MB"
Write-Host "   Investor Package: $investorSize MB"
Write-Host ""
Write-Host "LeadNest is now launch-ready with professional documentation!" -ForegroundColor Green
