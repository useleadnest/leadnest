@echo off
REM LeadNest Production Deployment Script for Windows

echo 🚀 Building and deploying LeadNest to production...

REM Navigate to frontend directory
cd frontend

REM Install dependencies
echo 📦 Installing dependencies...
"C:\Program Files\nodejs\npm.cmd" install

REM Build production version
echo 🔨 Building production version...
"C:\Program Files\nodejs\npm.cmd" run build

REM Deploy to Vercel
echo 🌐 Deploying to Vercel...
"C:\Program Files\nodejs\npx.cmd" vercel --prod

echo ✅ Deployment complete!
echo 🌍 Your LeadNest app should be live at: https://useleadnest.com
pause
