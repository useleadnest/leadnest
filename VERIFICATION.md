# LeadNest Production Key Verification Guide

This guide shows you how to verify that all your production API keys and configuration are working properly.

## Quick Terminal Commands

### 1. Full Automated Verification
```powershell
cd backend
python verify_keys.py
```
This runs a comprehensive test of all services and saves results to `verification_results.json`.

### 2. Manual Individual Tests

#### Database Connection Test
```powershell
cd backend
python -c "from config import config; from database import engine; from sqlalchemy import text; print('Testing DB...'); conn = engine.connect(); result = conn.execute(text('SELECT version();')); print(f'✅ Connected: {result.fetchone()[0][:50]}'); conn.close()"
```

#### OpenAI API Test
```powershell
cd backend
python -c "from config import config; import openai; openai.api_key = config.openai_api_key; response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': 'Say API test'}], max_tokens=5); print(f'✅ OpenAI: {response.choices[0].message.content}')"
```

#### Stripe API Test
```powershell
cd backend
python -c "from config import config; import stripe; stripe.api_key = config.stripe_secret_key; account = stripe.Account.retrieve(); print(f'✅ Stripe Account: {account.id}')"
```

#### Yelp API Test
```powershell
cd backend
python -c "from config import config; import requests; headers = {'Authorization': f'Bearer {config.yelp_api_key}'}; r = requests.get('https://api.yelp.com/v3/businesses/search', headers=headers, params={'term': 'construction', 'location': 'San Francisco', 'limit': 1}); r.raise_for_status(); print(f'✅ Yelp: Found {len(r.json()[\"businesses\"])} businesses')"
```

#### Environment Variables Check
```powershell
cd backend
python -c "from config import config; print(f'Database: {config.database_url[:30]}...'); print(f'OpenAI: {config.openai_api_key[:20]}...'); print(f'Stripe Secret: {config.stripe_secret_key[:20]}...'); print(f'Stripe Publishable: {config.stripe_publishable_key[:20]}...'); print(f'Yelp: {config.yelp_api_key[:20]}...'); print(f'Frontend: {config.frontend_url}'); print('✅ All env vars loaded')"
```

## What Each Test Verifies

### Database Test ✅
- Verifies PostgreSQL connection using production DATABASE_URL
- Shows PostgreSQL version info
- Confirms database is accessible and responsive

### OpenAI API Test ✅
- Verifies OPENAI_API_KEY is valid and functional
- Makes a real API call to gpt-3.5-turbo
- Confirms you have API credits and the key works

### Stripe API Test ✅
- Verifies STRIPE_SECRET_KEY is valid
- Retrieves your Stripe account information
- Confirms webhook secret is configured
- Tests both secret and publishable keys

### Yelp API Test ✅
- Verifies YELP_API_KEY is functional
- Makes a real search API call
- Confirms lead scraping will work

### Frontend URL Test ✅
- Verifies FRONTEND_URL is configured
- Optionally checks if frontend is accessible
- Ensures CORS will work correctly

### Auth Configuration Test ✅
- Verifies JWT secret key length and format
- Confirms algorithm and token expiration settings
- Ensures secure authentication configuration

## Expected Output

When all keys are working, you should see:
```
🔍 LeadNest Production Key Verification
==================================================

📊 Testing Database Connection...
   ✅ Database connected successfully
   📋 PostgreSQL Version: PostgreSQL 14.9...

🤖 Testing OpenAI API...
   ✅ OpenAI API working correctly
   🤖 Test Response: API test successful

💳 Testing Stripe API...
   ✅ Stripe API working correctly
   🏢 Account ID: acct_...
   📧 Business Name: LeadNest

🏪 Testing Yelp API...
   ✅ Yelp API working correctly
   🏢 Test Search Results: 1 businesses found

🌐 Testing Frontend URL...
   📋 Frontend URL: https://LeadNest.vercel.app
   ⚠️  Frontend is configured but not currently accessible

🔐 Testing Auth Configuration...
   ✅ Auth configuration looks good

==================================================
📊 VERIFICATION SUMMARY
==================================================
Total Tests: 6
Successful: 5
Warnings: 1
Failed: 0

🎉 All tests passed! Your LeadNest backend is ready for production.
```

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL format: `REDACTED_DATABASE_URL
- Check firewall settings for external database access
- Confirm database server is running and accessible

### API Key Issues
- Double-check keys aren't truncated when copying
- Verify keys are active in respective service dashboards
- Check for any spending limits or quotas reached

### Import Errors
- Run: `pip install -r requirements.txt`
- Ensure you're in the backend directory
- Check Python environment is activated

### Configuration Errors
- Verify .env file exists and is readable
- Check all required environment variables are set
- Look for typos in variable names

## Next Steps

After verification passes:
1. Deploy backend to Render using provided `render.yaml`
2. Deploy frontend to Vercel
3. Test the full application flow
4. Set up monitoring and logging
5. Configure database backups

The verification results are saved to `verification_results.json` for your records.
