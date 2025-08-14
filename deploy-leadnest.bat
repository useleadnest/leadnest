@echo off
echo.
echo ========================================
echo    LeadNest Production Deployment
echo ========================================
echo.

echo Step 1: Navigate to frontend directory
cd /d "c:\Users\mccab\contractornest\frontend"
echo Current directory: %CD%

echo.
echo Step 2: Build production version
echo Building LeadNest for production...
"C:\Program Files\nodejs\npm.cmd" run build

echo.
echo Step 3: Check build output
if exist "build" (
    echo ✅ Build successful! Build folder created.
    dir build
) else (
    echo ❌ Build failed! Build folder not found.
    pause
    exit /b 1
)

echo.
echo Step 4: Deploy to Vercel
echo Deploying to Vercel...
"C:\Program Files\nodejs\npx.cmd" vercel --prod

echo.
echo Step 5: Set custom domain
echo Setting up custom domain...
"C:\Program Files\nodejs\npx.cmd" vercel domains add useleadnest.com

echo.
echo ========================================
echo         Deployment Complete!
echo ========================================
echo.
echo Your LeadNest app should be live at:
echo 🌍 https://useleadnest.com
echo 📊 API: https://leadnest-api.onrender.com
echo.
echo Next steps:
echo 1. Test the live site
echo 2. Verify API connections
echo 3. Check all functionality
echo 4. Start marketing!
echo.
pause
