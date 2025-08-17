# 🚀 GitHub Repository Setup Instructions

## Backend Repository Setup

### Step 1: Create GitHub Repository
1. Go to https://github.com (make sure you're logged into `useleadnest@gmail.com`)
2. Click "New repository" 
3. Repository name: `leadnest-backend`
4. Description: `LeadNest SaaS Backend - FastAPI, PostgreSQL, Stripe Integration`
5. Set to **Public** (required for free Render deployment)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### Step 2: Push Code to GitHub
```powershell
# Navigate to backend directory
cd "c:\Users\mccab\contractornest\backend"

# Add the GitHub remote (replace with your actual repo URL)
git remote add origin https://github.com/useleadnest/leadnest-backend.git

# Push to GitHub
git push -u origin main
```

### Step 3: Deploy to Render
1. Go to https://render.com
2. Sign up/login with your `useleadnest@gmail.com` account
3. Click "New +" → "Web Service"
4. Connect your GitHub account
5. Select the `leadnest-backend` repository
6. Render will automatically detect the `render.yaml` file
7. Click "Deploy"

### Step 4: Configure Environment Variables
In Render dashboard, add these environment variables:
- `DATABASE_URL` - (Render will auto-create PostgreSQL)
- `STRIPE_PUBLISHABLE_KEY` - Your Stripe publishable key
- `STRIPE_SECRET_KEY` - Your Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Your Stripe webhook secret
- `OPENAI_API_KEY` - Your OpenAI API key

### Step 5: Test Deployment
Once deployed, test the health endpoint:
```
https://your-render-app.onrender.com/health
```

## Current Status
✅ Backend code ready and committed locally
✅ Render.yaml configuration file created
✅ Git repository initialized
⏳ Waiting for GitHub repository creation
⏳ Waiting for Render deployment

## Next Steps
1. Create GitHub repo under useleadnest@gmail.com
2. Push code to GitHub
3. Deploy to Render
4. Configure environment variables
5. Test API endpoints
6. Run E2E tests with live backend
