#!/usr/bin/env python3
"""
SMS Integration Test & Debug Tool
This script helps diagnose SMS integration issues step by step
"""
import os
import requests
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 STEP 1: Environment Variable Check")
    print("=" * 50)
    
    required_vars = {
        'TWILIO_ACCOUNT_SID': 'Account SID from Twilio Console',
        'TWILIO_AUTH_TOKEN': 'Auth Token from Twilio Console', 
        'TWILIO_FROM': 'Your Twilio phone number (+1234567890)',
        'DATABASE_URL': 'Database connection string',
        'JWT_SECRET': 'JWT secret key'
    }
    
    missing_vars = []
    for var, desc in required_vars.items():
        value = os.environ.get(var)
        if value:
            if 'TOKEN' in var or 'SECRET' in var:
                print(f"   ✅ {var}: {'*' * 10} (set)")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: NOT SET - {desc}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All environment variables are set!")
        return True

def test_twilio_api():
    """Test Twilio API connection"""
    print("\n🔍 STEP 2: Twilio API Connection Test")
    print("=" * 50)
    
    try:
        from twilio.rest import Client
        
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            print("   ❌ Twilio credentials not set")
            return False
            
        client = Client(account_sid, auth_token)
        
        # Test API connection by fetching account info
        account = client.api.accounts(account_sid).fetch()
        print(f"   ✅ Connected to Twilio account: {account.friendly_name}")
        print(f"   ✅ Account status: {account.status}")
        
        # Check phone numbers
        phone_numbers = client.incoming_phone_numbers.list()
        if phone_numbers:
            print(f"   ✅ Available phone numbers: {len(phone_numbers)}")
            for number in phone_numbers[:3]:  # Show first 3
                print(f"      📱 {number.phone_number}")
        else:
            print("   ⚠️  No phone numbers found")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Twilio API connection failed: {e}")
        return False

def test_local_webhook():
    """Test the webhook endpoint locally"""
    print("\n🔍 STEP 3: Local Webhook Test")
    print("=" * 50)
    
    try:
        # Start Flask app in test mode
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Simulate a Twilio webhook request
            test_data = {
                'From': '+15551234567',
                'To': '+15559876543', 
                'Body': 'Test message from debug script',
                'MessageSid': 'SM1234567890abcdef',
                'AccountSid': 'AC1234567890abcdef'
            }
            
            print("   📡 Sending test webhook request...")
            response = client.post('/api/twilio/inbound', 
                                 data=test_data,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
            
            print(f"   📊 Response status: {response.status_code}")
            print(f"   📊 Response data: {response.get_data(as_text=True)[:200]}")
            
            if response.status_code == 403:
                print("   ⚠️  403 Forbidden - This is expected without valid Twilio signature")
                print("   ⚠️  In production, Twilio will provide valid signatures")
                return True
            elif response.status_code == 200:
                print("   ✅ Webhook endpoint responding correctly")
                return True
            else:
                print(f"   ❌ Unexpected response: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Local webhook test failed: {e}")
        return False

def test_production_webhook(webhook_url):
    """Test the production webhook endpoint"""
    print(f"\n🔍 STEP 4: Production Webhook Test")
    print("=" * 50)
    
    if not webhook_url:
        print("   ⚠️  No webhook URL provided, skipping production test")
        return True
        
    try:
        print(f"   📡 Testing webhook URL: {webhook_url}")
        
        # Test basic connectivity
        health_url = webhook_url.replace('/api/twilio/inbound', '/healthz')
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ App is running: {health_url}")
        else:
            print(f"   ⚠️  Health check failed: {response.status_code}")
            
        # Test webhook endpoint (will return 403 without signature, which is expected)
        test_data = {
            'From': '+15551234567',
            'Body': 'Production test'
        }
        
        response = requests.post(webhook_url, data=test_data, timeout=10)
        print(f"   📊 Webhook response: {response.status_code}")
        
        if response.status_code == 403:
            print("   ✅ Webhook rejecting unsigned requests (correct behavior)")
            return True
        elif response.status_code == 200:
            print("   ⚠️  Webhook accepting unsigned requests (security issue)")
            return False
        else:
            print(f"   ❌ Unexpected webhook response: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Production webhook test failed: {e}")
        return False

def check_twilio_console_config():
    """Guide user through Twilio Console configuration"""
    print(f"\n🔍 STEP 5: Twilio Console Configuration Check")
    print("=" * 50)
    
    webhook_url = os.environ.get('WEBHOOK_URL', 'https://your-app.onrender.com/api/twilio/inbound')
    
    print("   📋 Twilio Console Configuration Checklist:")
    print("   " + "=" * 40)
    print("   1. Go to: https://console.twilio.com/")
    print("   2. Navigate to: Phone Numbers → Manage → Active numbers")
    print("   3. Click your phone number")
    print("   4. In 'Messaging' section:")
    print(f"      📱 Webhook URL: {webhook_url}")
    print("      📱 HTTP Method: POST")
    print("      📱 Save configuration")
    print("")
    print("   ⚠️  IMPORTANT: The webhook URL must be publicly accessible")
    print("   ⚠️  For local testing, use ngrok or similar tunneling tool")
    
    return True

def send_test_sms():
    """Send a test SMS if possible"""
    print(f"\n🔍 STEP 6: Send Test SMS")
    print("=" * 50)
    
    try:
        from twilio.rest import Client
        
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        twilio_from = os.environ.get('TWILIO_FROM')
        
        if not all([account_sid, auth_token, twilio_from]):
            print("   ⚠️  Missing Twilio credentials, cannot send test SMS")
            return True
            
        test_to = input("   📱 Enter your phone number to receive test SMS (+1234567890): ").strip()
        if not test_to:
            print("   ⚠️  No phone number provided, skipping SMS test")
            return True
            
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body="Test SMS from LeadNest! Reply to test webhook.",
            from_=twilio_from,
            to=test_to
        )
        
        print(f"   ✅ Test SMS sent successfully!")
        print(f"   📱 Message SID: {message.sid}")
        print(f"   📱 Status: {message.status}")
        print("")
        print("   📋 Next steps:")
        print("   1. Check your phone for the test message")
        print("   2. Reply to that message")
        print("   3. Check your app logs for webhook activity")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to send test SMS: {e}")
        return False

def main():
    """Run all SMS integration tests"""
    print("🚀 SMS Integration Diagnostic Tool")
    print("=" * 50)
    print("This tool will help diagnose SMS integration issues step by step.\n")
    
    # Get webhook URL from user
    webhook_url = input("Enter your production webhook URL (or press Enter to skip): ").strip()
    if webhook_url:
        os.environ['WEBHOOK_URL'] = webhook_url
    
    # Run all tests
    tests = [
        ("Environment Check", check_environment),
        ("Twilio API Test", test_twilio_api), 
        ("Local Webhook Test", test_local_webhook),
        ("Production Webhook Test", lambda: test_production_webhook(webhook_url)),
        ("Console Configuration Guide", check_twilio_console_config),
        ("Send Test SMS", send_test_sms)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL" 
        print(f"   {status} {test_name}")
    
    # Recommendations
    print("\n🔧 TROUBLESHOOTING RECOMMENDATIONS:")
    print("=" * 40)
    
    if not results.get("Environment Check", False):
        print("   1. ❗ Set all required environment variables")
        
    if not results.get("Twilio API Test", False):
        print("   2. ❗ Check Twilio credentials and account status")
        
    if not results.get("Production Webhook Test", True):
        print("   3. ❗ Verify webhook URL is publicly accessible")
        
    print("\n   4. 📱 Common issues:")
    print("      • Webhook URL not configured in Twilio Console")
    print("      • Environment variables not set in production")
    print("      • App not deployed or not responding")
    print("      • Signature validation failing (check auth token)")
    
    print("\n   5. 🔍 Debug logs:")
    print("      • Check Render/Heroku logs for webhook requests")
    print("      • Look for 403 errors (signature validation)")
    print("      • Look for 500 errors (application errors)")
    
    print(f"\n✅ Diagnostic complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
