# Database Setup for LeadNest

## PostgreSQL Setup

### 1. Install PostgreSQL
Download and install PostgreSQL from https://www.postgresql.org/download/

### 2. Create Database
```sql
CREATE DATABASE LeadNest;
CREATE USER LeadNest_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE LeadNest TO LeadNest_user;
```

### 3. Environment Setup
Copy `.env.example` to `.env` and update with your database credentials:
```
DATABASE_URL=REDACTED_DATABASE_URL
```

## Tables
The following tables will be created automatically when you run the FastAPI application:

- **users**: User accounts, trials, subscriptions
- **searches**: Search history with location/trade
- **leads**: Business leads with contact info and AI messages
- **exports**: Export history for analytics

## Sample Data
The application includes mock data generation when external APIs are not available.

## API Keys Required
- OpenAI API key for message generation
- Yelp API key for business scraping (optional, falls back to mock data)
- Stripe keys for subscription management (for production)
