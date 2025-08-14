@echo off
REM LeadNest Test Runner for Windows
REM Runs all tests with coverage reporting

echo 🧪 Running LeadNest Test Suite...

REM Check if we're in the right directory
if not exist "backend\main.py" (
    echo ❌ Please run this script from the LeadNest root directory
    pause
    exit /b 1
)

REM Set up test environment
set ENVIRONMENT=test
set DATABASE_URL=sqlite:///./test.db

REM Navigate to backend
cd backend

REM Install test dependencies
echo 📦 Installing test dependencies...
pip install -r requirements.txt
pip install -r test-requirements.txt

REM Run tests with coverage
echo 🏃 Running tests with coverage...
python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

REM Run security checks
echo 🔒 Running security checks...
pip install bandit safety
bandit -r . -f json -o security-report.json
safety check --json --output safety-report.json

REM Run linting
echo 🔍 Running code quality checks...
pip install flake8 black isort
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
black --check .
isort --check-only .

echo.
echo ✅ Test suite completed!
echo 📊 Coverage report: backend\htmlcov\index.html
echo 🔒 Security report: backend\security-report.json
echo.

REM Return to root directory
cd ..
pause
