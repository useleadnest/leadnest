#!/bin/bash
# scan-secrets.sh - Secret scanning for CI/CD pipelines
# Exits 1 if any secrets found, 0 if clean

set -e

secret_patterns=(
    'sk_live_[a-zA-Z0-9]{99}'        # Stripe live secret keys
    'rk_live_[a-zA-Z0-9]{48}'        # Stripe restricted keys  
    'pk_live_[a-zA-Z0-9]{107}'       # Stripe live publishable keys
    'whsec_[a-zA-Z0-9+/=]{32,}'      # Stripe webhook secrets
    'AKIA[0-9A-Z]{16}'               # AWS Access Key ID
    'ghp_[a-zA-Z0-9]{36}'            # GitHub Personal Access Token
    'gho_[a-zA-Z0-9]{36}'            # GitHub OAuth Token
    'github_pat_[a-zA-Z0-9_]{82}'    # GitHub Fine-grained PAT
    'glpat-[a-zA-Z0-9\-_]{20}'       # GitLab Personal Access Token
    'xoxb-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}' # Slack Bot Token
    '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*[pP]ass.*[:=]\s*[^\s]+' # Email + password
    'password\s*[:=]\s*[^\s\[\]]{8,}' # Password assignments
    '[sS]ecret.*[:=]\s*[a-zA-Z0-9+/=]{16,}' # Generic secrets
)

found_secrets=false
exclude_patterns="node_modules/|\.git/|__pycache__/|\.venv/|dist/|build/"

echo "🔍 Scanning for secrets..."
echo "Patterns: ${#secret_patterns[@]}"
echo "Exclude: $exclude_patterns"

for pattern in "${secret_patterns[@]}"; do
    echo "Checking pattern: $pattern"
    
    if find . -type f -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./__pycache__/*" -not -path "./.venv/*" -not -path "./dist/*" -not -path "./build/*" -exec grep -l -E "$pattern" {} \; 2>/dev/null | head -1 | grep -q .; then
        echo "❌ FOUND SECRET matching pattern: $pattern"
        found_secrets=true
        find . -type f -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./__pycache__/*" -not -path "./.venv/*" -not -path "./dist/*" -not -path "./build/*" -exec grep -l -E "$pattern" {} \; 2>/dev/null || true
    fi
done

if [ "$found_secrets" = true ]; then
    echo ""
    echo "❌ SECRET SCAN FAILED - Secrets detected in repository"
    echo "🚨 DO NOT COMMIT - Fix all secrets before proceeding"
    exit 1
else
    echo ""
    echo "✅ SECRET SCAN PASSED - No secrets detected"
    echo "🛡️  Repository is clean for deployment"
    exit 0
fi
