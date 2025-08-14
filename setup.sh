#!/bin/bash

# LeadNest Setup Script
echo "🚀 Setting up LeadNest..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if Node.js is installed  
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL 12+ first."
    exit 1
fi

echo "✅ All prerequisites found!"

# Setup backend
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file. Please update it with your API keys."
fi

cd ..

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend
npm install
cd ..

# Setup database
echo "🗄️ Setting up database..."
echo "Please run the following commands in your PostgreSQL shell:"
echo "CREATE DATABASE LeadNest;"
echo "CREATE USER LeadNest_user WITH PASSWORD 'LeadNest_password';"
echo "GRANT ALL PRIVILEGES ON DATABASE LeadNest TO LeadNest_user;"

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Update backend/.env with your API keys"
echo "2. Run 'cd backend && source venv/bin/activate && python main.py'"
echo "3. In another terminal: 'cd frontend && npm start'"
echo "4. Visit http://localhost:3000"
