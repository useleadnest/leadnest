# Setting Sentry DSN in Vercel Environment Variables

## Method 1: Vercel Dashboard (Recommended)

### Step-by-Step Instructions:

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Sign in to your account

2. **Navigate to Your Project**
   - Find your LeadNest frontend project
   - Click on the project name

3. **Go to Settings**
   - Click on the "Settings" tab at the top

4. **Environment Variables Section**
   - Click on "Environment Variables" in the left sidebar

5. **Add New Environment Variable**
   - Click "Add New" button
   - **Name:** `REACT_APP_SENTRY_DSN`
   - **Value:** `https://your-actual-dsn@sentry.io/project-id`
   - **Environments:** Select "Production" (and "Preview" if you want)
   - Click "Save"

6. **Trigger Redeploy**
   - Go to "Deployments" tab
   - Click "..." on the latest deployment
   - Click "Redeploy"
   - OR push a new commit to trigger automatic deployment

## Method 2: Vercel CLI

### Prerequisites:
- Install Vercel CLI: `npm i -g vercel`
- Login: `vercel login`

### Commands:
```bash
# Navigate to your frontend directory
cd frontend

# Add environment variable
vercel env add REACT_APP_SENTRY_DSN

# When prompted, enter your Sentry DSN:
# https://your-actual-dsn@sentry.io/project-id

# Select environments (Production recommended)

# Redeploy to apply changes
vercel --prod
```

## Getting Your Actual Sentry DSN

### If you don't have a Sentry project yet:

1. **Create Sentry Account**
   - Go to https://sentry.io
   - Sign up or login

2. **Create New Project**
   - Click "Create Project"
   - Select "React" as platform
   - Choose a project name (e.g., "leadnest-frontend")
   - Select your team/organization

3. **Get DSN**
   - After project creation, you'll see setup instructions
   - Copy the DSN that looks like: `https://abc123@o123456.ingest.sentry.io/123456`

4. **Configure Project**
   - Set alert rules
   - Configure error filtering
   - Set up team notifications

## Verification

### Check Environment Variables:
```bash
# Using Vercel CLI
vercel env ls

# Should show your REACT_APP_SENTRY_DSN
```

### Test in Production:
After deployment, you can test Sentry integration by:
1. Visiting your production site
2. Opening browser console
3. Manually triggering an error: `throw new Error("Test Sentry Integration")`
4. Check Sentry dashboard for the error

## Important Notes:

- ⚠️ **Replace `https://your-dsn@sentry.io/project-id` with your ACTUAL Sentry DSN**
- ✅ Use `REACT_APP_` prefix (not `VITE_`) for Create React App
- ✅ Set for "Production" environment at minimum
- ✅ Redeploy after adding environment variables
- 🔒 Sentry DSN is safe to expose (it's a public key)

## PowerShell Script Alternative

If you prefer automation, here's a PowerShell script:
