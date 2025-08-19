# Test Environment Variables in Production
Write-Host "TESTING PRODUCTION ENVIRONMENT VARIABLES" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Test the live site
Write-Host "1. Testing environment variable access..." -ForegroundColor Yellow
$testScript = @"
// Check if REACT_APP environment variables are available
console.log('=== ENVIRONMENT VARIABLES TEST ===');
console.log('API_BASE_URL:', typeof process !== 'undefined' && process.env ? process.env.REACT_APP_API_BASE_URL : 'Not available');
console.log('PUBLIC_APP_NAME:', typeof process !== 'undefined' && process.env ? process.env.REACT_APP_PUBLIC_APP_NAME : 'Not available');
console.log('CALENDLY_URL:', typeof process !== 'undefined' && process.env ? process.env.REACT_APP_CALENDLY_URL : 'Not available');
console.log('ENV_NAME:', typeof process !== 'undefined' && process.env ? process.env.REACT_APP_ENV_NAME : 'Not available');
console.log('ENABLE_ANALYTICS:', typeof process !== 'undefined' && process.env ? process.env.REACT_APP_ENABLE_ANALYTICS : 'Not available');
console.log('ENABLE_CHAT_SUPPORT:', typeof process !== 'undefined' && process.env ? process.env.REACT_APP_ENABLE_CHAT_SUPPORT : 'Not available');
console.log('=== END TEST ===');
"@

Write-Host "2. MANUAL VERIFICATION STEPS:" -ForegroundColor Yellow
Write-Host "   1. Open: https://useleadnest.com" -ForegroundColor Cyan
Write-Host "   2. Hard refresh: Ctrl+F5" -ForegroundColor Cyan
Write-Host "   3. Open DevTools Console (F12)" -ForegroundColor Cyan
Write-Host "   4. Paste this script:" -ForegroundColor Cyan
Write-Host ""
Write-Host $testScript -ForegroundColor White
Write-Host ""
Write-Host "   5. Press Enter to run" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. EXPECTED RESULTS:" -ForegroundColor Yellow
Write-Host "   API_BASE_URL: https://api.useleadnest.com/api" -ForegroundColor Green
Write-Host "   PUBLIC_APP_NAME: LeadNest" -ForegroundColor Green
Write-Host "   CALENDLY_URL: https://calendly.com/leadnest-demo" -ForegroundColor Green
Write-Host "   ENV_NAME: production" -ForegroundColor Green
Write-Host "   ENABLE_ANALYTICS: true" -ForegroundColor Green
Write-Host "   ENABLE_CHAT_SUPPORT: false" -ForegroundColor Green
Write-Host ""

Write-Host "4. TROUBLESHOOTING:" -ForegroundColor Yellow
Write-Host "   If any show 'Not available':" -ForegroundColor Red
Write-Host "   - Check Vercel env vars are in Production scope" -ForegroundColor White
Write-Host "   - Redeploy with clean build cache" -ForegroundColor White
Write-Host "   - Hard refresh browser" -ForegroundColor White
Write-Host ""

Write-Host "5. FINAL CHECKS:" -ForegroundColor Yellow
Write-Host "   [ ] No VITE or import.meta errors in console" -ForegroundColor White
Write-Host "   [ ] Network tab shows API calls to api.useleadnest.com" -ForegroundColor White
Write-Host "   [ ] Deep link test: https://useleadnest.com/dashboard" -ForegroundColor White
Write-Host "   [ ] All environment variables display correctly" -ForegroundColor White
Write-Host ""
Write-Host "Complete!" -ForegroundColor Green
