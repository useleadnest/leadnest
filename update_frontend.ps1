# 🔄 FRONTEND UPDATE FOR NEW BACKEND

## After Backend Success, Run This:

### Update API URL
$newApiUrl = "https://leadnest-api-final.onrender.com"

# Update .env.production
$envPath = "c:\Users\mccab\contractornest\frontend\.env.production"
$envContent = @"
VITE_API_URL=$newApiUrl
"@

Set-Content -Path $envPath -Value $envContent
Write-Host "✅ Updated frontend API URL to: $newApiUrl"

# Rebuild frontend
Set-Location "c:\Users\mccab\contractornest\frontend"
& "C:\Program Files\nodejs\npm.cmd" run build

# Redeploy to Vercel
& "C:\Program Files\nodejs\npx.cmd" vercel --prod

Write-Host "🚀 Frontend updated and redeployed!"
