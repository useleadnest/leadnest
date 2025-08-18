# Sentry Sourcemap Upload Script for LeadNest Frontend
# This script uploads sourcemaps to Sentry for better error stack traces

param(
    [Parameter(Mandatory=$false)]
    [string]$Environment = "production",
    
    [Parameter(Mandatory=$false)]
    [string]$Release = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Blue"

Write-Host "🚀 Sentry Sourcemap Upload Script" -ForegroundColor $Blue
Write-Host "Environment: $Environment" -ForegroundColor $Blue

# Check if build directory exists
if (-not (Test-Path "build")) {
    Write-Host "❌ Build directory not found. Please run 'npm run build' first." -ForegroundColor $Red
    exit 1
}

# Get release version
if ($Release -eq "") {
    # Try to get from Vercel git SHA
    $Release = $env:VERCEL_GIT_COMMIT_SHA
    if (-not $Release) {
        $Release = $env:REACT_APP_VERCEL_GIT_COMMIT_SHA
    }
    if (-not $Release) {
        # Fallback to timestamp
        $Release = "frontend-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Write-Host "⚠️  No git SHA found, using timestamp: $Release" -ForegroundColor $Yellow
    } else {
        Write-Host "✅ Using git SHA as release: $($Release.Substring(0, 8))" -ForegroundColor $Green
    }
}

# Check for required environment variables
$SentryAuthToken = $env:SENTRY_AUTH_TOKEN
$SentryOrg = $env:SENTRY_ORG
$SentryProject = $env:SENTRY_PROJECT

if (-not $SentryAuthToken) {
    Write-Host "❌ SENTRY_AUTH_TOKEN environment variable is required" -ForegroundColor $Red
    Write-Host "   Get your token from: https://sentry.io/settings/account/api/auth-tokens/" -ForegroundColor $Yellow
    exit 1
}

if (-not $SentryOrg) {
    $SentryOrg = "leadnest"
    Write-Host "⚠️  SENTRY_ORG not set, using default: $SentryOrg" -ForegroundColor $Yellow
}

if (-not $SentryProject) {
    $SentryProject = "leadnest-frontend"
    Write-Host "⚠️  SENTRY_PROJECT not set, using default: $SentryProject" -ForegroundColor $Yellow
}

Write-Host "📦 Release: $Release" -ForegroundColor $Blue
Write-Host "🏢 Org: $SentryOrg" -ForegroundColor $Blue  
Write-Host "📋 Project: $SentryProject" -ForegroundColor $Blue

# Check if sentry-cli is available
$SentryCli = Get-Command "sentry-cli" -ErrorAction SilentlyContinue
if (-not $SentryCli) {
    Write-Host "❌ sentry-cli not found. Installing..." -ForegroundColor $Red
    
    try {
        if ($DryRun) {
            Write-Host "[DRY RUN] Would run: npm install -g @sentry/cli" -ForegroundColor $Yellow
        } else {
            npm install -g @sentry/cli
            Write-Host "✅ Installed @sentry/cli globally" -ForegroundColor $Green
        }
    } catch {
        Write-Host "❌ Failed to install sentry-cli: $($_.Exception.Message)" -ForegroundColor $Red
        exit 1
    }
}

# Create a new release
Write-Host "📝 Creating Sentry release: $Release" -ForegroundColor $Blue
if ($DryRun) {
    Write-Host "[DRY RUN] Would run: sentry-cli releases new $Release" -ForegroundColor $Yellow
} else {
    try {
        sentry-cli releases new $Release --org $SentryOrg --project $SentryProject
        Write-Host "✅ Created release: $Release" -ForegroundColor $Green
    } catch {
        Write-Host "⚠️  Release might already exist, continuing..." -ForegroundColor $Yellow
    }
}

# Upload sourcemaps
Write-Host "📤 Uploading sourcemaps..." -ForegroundColor $Blue
$SourceMapPath = "build/static/js/"
$UrlPrefix = "~/static/js/"

if ($DryRun) {
    Write-Host "[DRY RUN] Would upload sourcemaps from: $SourceMapPath" -ForegroundColor $Yellow
    Write-Host "[DRY RUN] Would use URL prefix: $UrlPrefix" -ForegroundColor $Yellow
} else {
    try {
        sentry-cli sourcemaps upload --release=$Release --org=$SentryOrg --project=$SentryProject --url-prefix=$UrlPrefix $SourceMapPath
        Write-Host "✅ Uploaded sourcemaps successfully" -ForegroundColor $Green
    } catch {
        Write-Host "❌ Failed to upload sourcemaps: $($_.Exception.Message)" -ForegroundColor $Red
        exit 1
    }
}

# Set commits for the release (if git is available)
if (Get-Command "git" -ErrorAction SilentlyContinue) {
    Write-Host "📝 Setting commits for release..." -ForegroundColor $Blue
    if ($DryRun) {
        Write-Host "[DRY RUN] Would set commits for release" -ForegroundColor $Yellow
    } else {
        try {
            sentry-cli releases set-commits --release=$Release --org=$SentryOrg --project=$SentryProject --auto
            Write-Host "✅ Set commits for release" -ForegroundColor $Green
        } catch {
            Write-Host "⚠️  Could not set commits (this is optional)" -ForegroundColor $Yellow
        }
    }
} else {
    Write-Host "⚠️  Git not available, skipping commit association" -ForegroundColor $Yellow
}

# Finalize the release
Write-Host "🏁 Finalizing release..." -ForegroundColor $Blue
if ($DryRun) {
    Write-Host "[DRY RUN] Would finalize release: $Release" -ForegroundColor $Yellow
} else {
    try {
        sentry-cli releases finalize --release=$Release --org=$SentryOrg --project=$SentryProject
        Write-Host "✅ Finalized release: $Release" -ForegroundColor $Green
    } catch {
        Write-Host "❌ Failed to finalize release: $($_.Exception.Message)" -ForegroundColor $Red
        exit 1
    }
}

# Deploy notification
Write-Host "🚀 Sending deploy notification..." -ForegroundColor $Blue
if ($DryRun) {
    Write-Host "[DRY RUN] Would send deploy notification for environment: $Environment" -ForegroundColor $Yellow
} else {
    try {
        sentry-cli releases deploys --release=$Release --org=$SentryOrg --project=$SentryProject new --env=$Environment
        Write-Host "✅ Sent deploy notification for environment: $Environment" -ForegroundColor $Green
    } catch {
        Write-Host "❌ Failed to send deploy notification: $($_.Exception.Message)" -ForegroundColor $Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Sourcemap upload completed successfully!" -ForegroundColor $Green
Write-Host "   Release: $Release" -ForegroundColor $Blue
Write-Host "   Environment: $Environment" -ForegroundColor $Blue
Write-Host "   View in Sentry: https://sentry.io/organizations/$SentryOrg/projects/$SentryProject/releases/$Release/" -ForegroundColor $Blue
Write-Host ""
Write-Host "Next steps:" -ForegroundColor $Yellow
Write-Host "1. Visit your deployed app and trigger test errors" -ForegroundColor $Yellow  
Write-Host "2. Check Sentry dashboard for clean stack traces" -ForegroundColor $Yellow
Write-Host "3. Verify performance traces and breadcrumbs" -ForegroundColor $Yellow
