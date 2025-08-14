@echo off
echo 🚀 Setting up LeadNest...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

echo ✅ Prerequisites found!

REM Setup backend
echo 📦 Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

REM Copy environment file
if not exist .env (
    copy .env.example .env
    echo 📝 Created .env file. Please update it with your API keys.
)

cd ..

REM Setup frontend
echo 🎨 Setting up frontend...
cd frontend
npm install
cd ..

echo.
echo 🎉 Setup complete! Next steps:
echo 1. Update backend\.env with your API keys
echo 2. Setup PostgreSQL database (see db\README.md)
echo 3. Run backend: cd backend ^&^& venv\Scripts\activate ^&^& python main.py
echo 4. Run frontend: cd frontend ^&^& npm start
echo 5. Visit http://localhost:3000
pause
