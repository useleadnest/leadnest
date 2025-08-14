#!/bin/bash
# LeadNest Production Deployment Script

echo "🚀 Building and deploying LeadNest to production..."

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build production version
echo "🔨 Building production version..."
npm run build

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
npx vercel --prod

echo "✅ Deployment complete!"
echo "🌍 Your LeadNest app should be live at: https://useleadnest.com"
