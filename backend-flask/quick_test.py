#!/usr/bin/env python3
"""
Quick SMS Integration Test for Production
"""
import requests
import json

def test_webhook():
    print("🧪 Testing Production Webhook")
    print("=" * 40)
    
    webhook_url = "https://api.useleadnest.com/api/twilio/inbound"
    
    # Test 1: Health check
    try:
        health_response = requests.get("https://api.useleadnest.com/healthz")
        print(f"✅ Health check: {health_response.status_code} - {health_response.text}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Test webhook without signature (should get 403 or similar)
    test_data = {
        'From': '+15551234567',
        'To': '+15559876543',
        'Body': 'Test webhook',
        'MessageSid': 'SM1234567890abcdef',
        'AccountSid': 'AC1234567890abcdef'
    }
    
    try:
        response = requests.post(
            webhook_url,
            data=test_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        print(f"📊 Webhook test: {response.status_code}")
        print(f"📊 Response: {response.text[:200]}")
        
        if response.status_code == 403:
            print("✅ Webhook correctly rejecting unsigned requests")
        elif response.status_code == 500:
            print("❌ Internal Server Error - Check environment variables")
        elif response.status_code == 200:
            print("⚠️  Webhook accepting unsigned requests (security concern)")
        
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
    
    # Test 3: Check if environment variables are likely missing
    print("\n🔍 Common Issues:")
    print("1. TWILIO_AUTH_TOKEN not set in Render environment")
    print("2. Database connection issues")
    print("3. Missing other required environment variables")
    print("4. App not properly handling form data")
    
    print("\n🔧 Next Steps:")
    print("1. Check Render logs for detailed error messages")
    print("2. Verify TWILIO_AUTH_TOKEN is set in Render dashboard")
    print("3. Test with actual Twilio signature")

if __name__ == "__main__":
    test_webhook()
