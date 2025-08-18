# LeadNest Production Deployment Script
# Execute this step-by-step to deploy LeadNest to production

Write-Host "🚀 LeadNest Production Deployment Starting..." -ForegroundColor Green

# Step 1: Prepare for deployment
Write-Host "📋 Step 1: Pre-deployment checklist" -ForegroundColor Yellow

$env:DEPLOYMENT_DATE = Get-Date -Format "yyyy-MM-dd-HH-mm"
$env:COMMIT_HASH = git rev-parse --short HEAD

Write-Host "Deployment Date: $env:DEPLOYMENT_DATE"
Write-Host "Commit Hash: $env:COMMIT_HASH"
Write-Host "Current Branch: $(git branch --show-current)"

# Verify all critical files exist
$criticalFiles = @(
    "backend-flask/requirements.txt",
    "backend-flask/wsgi.py", 
    "backend-flask/Procfile",
    "frontend/package.json",
    "frontend/vercel.json",
    "frontend/.env.production"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🔧 Step 2: Backend Deployment Preparation" -ForegroundColor Yellow

# Test backend locally first
Write-Host "Testing backend locally..."
cd backend-flask

# Set test environment
$env:DATABASE_URL = "sqlite:///test.db"
$env:JWT_SECRET = "test-secret"
$env:PUBLIC_BASE_URL = "http://localhost:5000"

# Install requirements
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations
Write-Host "Running database migrations..."
flask db upgrade

# Test that app can start
Write-Host "Testing app startup..."
python -c "from app import create_app; app = create_app(); print('✅ Backend app starts successfully')"

cd ..

Write-Host ""
Write-Host "🌐 Step 3: Frontend Deployment Preparation" -ForegroundColor Yellow

cd frontend

# Install frontend dependencies
Write-Host "Installing Node.js dependencies..."
npm ci

# Test build process
Write-Host "Testing production build..."
npm run build

Write-Host "✅ Frontend builds successfully" -ForegroundColor Green

cd ..

Write-Host ""
Write-Host "📚 Step 4: Documentation Site Setup" -ForegroundColor Yellow

# Check if docs site exists
if (-not (Test-Path "docs-site")) {
    Write-Host "Creating Docusaurus documentation site..."
    npx create-docusaurus@latest docs-site classic --typescript
    
    # Configure docs site
    $docusaurusConfig = @"
module.exports = {
  title: 'LeadNest Documentation',
  tagline: 'AI-Powered Lead Management Platform',
  url: 'https://docs.useleadnest.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'useleadnest',
  projectName: 'leadnest-docs',
  
  themeConfig: {
    navbar: {
      title: 'LeadNest Docs',
      logo: {
        alt: 'LeadNest Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'getting-started',
          position: 'left',
          label: 'Getting Started',
        },
        {
          type: 'doc',
          docId: 'api/overview',
          position: 'left',
          label: 'API',
        },
        {
          href: 'https://github.com/useleadnest/leadnest',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/getting-started',
            },
            {
              label: 'API Reference',
              to: '/docs/api/overview',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/useleadnest/leadnest',
            },
            {
              label: 'Support',
              href: 'mailto:support@useleadnest.com',
            },
          ],
        },
      ],
      copyright: `Copyright © `${new Date().getFullYear()}` LeadNest. Built with Docusaurus.`,
    },
  },
  
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/useleadnest/leadnest/edit/main/docs-site/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
"@
    
    $docusaurusConfig | Out-File -FilePath "docs-site/docusaurus.config.js" -Encoding UTF8
    
    # Copy documentation files
    Copy-Item "docs/*" "docs-site/docs/" -Recurse -Force
    Copy-Item "LEADNEST_DEVELOPER_DOCUMENTATION.md" "docs-site/docs/developer-guide.md"
    Copy-Item "LEADNEST_CLIENT_QUICK_START.md" "docs-site/docs/client-guide.md"
    Copy-Item "LEADNEST_EXECUTIVE_SUMMARY.md" "docs-site/docs/executive-summary.md"
}

Write-Host ""
Write-Host "🎯 Step 5: Deployment Instructions" -ForegroundColor Yellow

Write-Host "MANUAL DEPLOYMENT STEPS (Execute in order):" -ForegroundColor Cyan
Write-Host ""

Write-Host "A. BACKEND DEPLOYMENT (Render.com):" -ForegroundColor White
Write-Host "1. Go to https://render.com/dashboard"
Write-Host "2. Click 'New +' → 'Web Service'"
Write-Host "3. Connect GitHub repo: useleadnest/leadnest"
Write-Host "4. Settings:"
Write-Host "   - Name: leadnest-api"
Write-Host "   - Environment: Python 3"
Write-Host "   - Root Directory: backend-flask"
Write-Host "   - Build Command: pip install -r requirements.txt"
Write-Host "   - Start Command: gunicorn wsgi:app --bind 0.0.0.0:`$PORT --workers 2 --threads 4 --timeout 120"
Write-Host "5. Add PostgreSQL database (New + → PostgreSQL)"
Write-Host "6. Add Redis instance (New + → Redis)"
Write-Host "7. Set environment variables (see backend-flask/.env.production)"
Write-Host "8. Add custom domain: api.useleadnest.com"
Write-Host ""

Write-Host "B. FRONTEND DEPLOYMENT (Vercel):" -ForegroundColor White
Write-Host "1. cd frontend"
Write-Host "2. vercel --prod"
Write-Host "3. Set environment variables in Vercel dashboard"
Write-Host "4. Add custom domain: useleadnest.com"
Write-Host ""

Write-Host "C. DOCUMENTATION DEPLOYMENT:" -ForegroundColor White  
Write-Host "1. cd docs-site"
Write-Host "2. npm run build"
Write-Host "3. Deploy to Vercel or Netlify"
Write-Host "4. Add custom domain: docs.useleadnest.com"
Write-Host ""

Write-Host "D. POST-DEPLOYMENT VERIFICATION:" -ForegroundColor White
Write-Host "1. Test health endpoints:"
Write-Host "   curl https://api.useleadnest.com/healthz"
Write-Host "   curl https://api.useleadnest.com/readyz"
Write-Host "2. Test authentication:"
Write-Host "   curl https://api.useleadnest.com/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"password\":\"password\"}'"
Write-Host "3. Test frontend: https://useleadnest.com"
Write-Host "4. Test documentation: https://docs.useleadnest.com"
Write-Host "5. Configure Stripe webhooks: https://api.useleadnest.com/api/stripe/webhook"
Write-Host "6. Configure Twilio webhooks: https://api.useleadnest.com/api/twilio/inbound"
Write-Host ""

Write-Host "🔗 Quick Deployment Links:" -ForegroundColor Cyan
Write-Host "Render Dashboard: https://render.com/dashboard"
Write-Host "Vercel Dashboard: https://vercel.com/dashboard" 
Write-Host "Stripe Dashboard: https://dashboard.stripe.com"
Write-Host "Twilio Console: https://console.twilio.com"
Write-Host ""

Write-Host "✅ Pre-deployment preparation complete!" -ForegroundColor Green
Write-Host "Execute the manual deployment steps above to go live." -ForegroundColor Yellow

Write-Host ""
Write-Host "🎉 After deployment, LeadNest will be live at:" -ForegroundColor Green
Write-Host "🌐 Main App: https://useleadnest.com"
Write-Host "⚡ API: https://api.useleadnest.com"
Write-Host "📚 Docs: https://docs.useleadnest.com"
