#!/bin/bash

# LeadNest Test Runner
# Runs all tests with coverage reporting

echo "🧪 Running LeadNest Test Suite..."

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Please run this script from the LeadNest root directory"
    exit 1
fi

# Set up test environment
export ENVIRONMENT=test
export DATABASE_URL=sqlite:///./test.db

# Navigate to backend
cd backend

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements.txt
pip install -r test-requirements.txt

# Run tests with coverage
echo "🏃 Running tests with coverage..."
python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

# Generate coverage badge
echo "📊 Generating coverage report..."
coverage-badge -o coverage.svg

# Run security checks
echo "🔒 Running security checks..."
pip install bandit safety
bandit -r . -f json -o security-report.json || true
safety check --json --output safety-report.json || true

# Run linting
echo "🔍 Running code quality checks..."
pip install flake8 black isort
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
black --check . || echo "⚠️  Code formatting issues found. Run 'black .' to fix."
isort --check-only . || echo "⚠️  Import sorting issues found. Run 'isort .' to fix."

echo ""
echo "✅ Test suite completed!"
echo "📊 Coverage report: backend/htmlcov/index.html"
echo "🔒 Security report: backend/security-report.json"
echo ""

# Return to root directory
cd ..
