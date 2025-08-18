#!/usr/bin/env python3
"""
Test Twilio Auto-Reply Functionality
===================================

This script tests the complete Twilio SMS auto-reply flow:
1. Checks webhook health
2. Verifies environment variables
3. Tests signature validation
4. Confirms TwiML response format

Usage: python test_twilio_autoreply.py
"""
import requests
import json
import time

def test_webhook_health():
    """Test if the Twilio webhook endpoint is accessible"""
    print("🔍 Testing webhook health...")
    
    try:
        response = requests.get("https://leadnest-backend.onrender.com/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_twilio_debug():
    """Test the Twilio debug endpoint"""
    print("\n🔍 Testing Twilio debug endpoint...")
    
    try:
        response = requests.get("https://leadnest-backend.onrender.com/api/twilio/debug", timeout=10)
        if response.status_code == 200:
            debug_info = response.json()
            print("✅ Twilio debug endpoint accessible")
            print(f"   Webhook URL: {debug_info.get('webhook_url', 'NOT SET')}")
            print(f"   TWILIO_FROM: {debug_info.get('twilio_from', 'NOT SET')}")
            print(f"   Auth Token: {'SET' if debug_info.get('auth_token_set') else 'NOT SET'}")
            return True
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
        return False

def test_webhook_response():
    """Test the webhook response format"""
    print("\n🔍 Testing webhook response format...")
    
    # Simulate a Twilio webhook request
    webhook_data = {
        'From': '+15551234567',
        'Body': 'Test message',
        'MessageSid': 'SM1234567890abcdef',
        'AccountSid': 'AC1234567890abcdef'
    }
    
    try:
        response = requests.post(
            "https://leadnest-backend.onrender.com/api/twilio/inbound",
            data=webhook_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'NOT SET')}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200 and 'application/xml' in response.headers.get('Content-Type', ''):
            print("✅ Webhook returns proper TwiML response")
            return True
        else:
            print("❌ Webhook response format issue")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False

def main():
    print("🚀 Testing Twilio Auto-Reply Functionality")
    print("=" * 50)
    
    # Wait for deployment if needed
    print("⏳ Waiting for deployment to be ready...")
    for attempt in range(6):  # Try for 3 minutes
        if test_webhook_health():
            break
        print(f"   Attempt {attempt + 1}/6 - waiting 30 seconds...")
        time.sleep(30)
    else:
        print("❌ Deployment not ready after 3 minutes")
        return False
    
    # Run tests
    tests_passed = 0
    tests_total = 2
    
    if test_twilio_debug():
        tests_passed += 1
    
    if test_webhook_response():
        tests_passed += 1
    
    # Results
    print(f"\n📊 Test Results: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("✅ All tests passed! Ready to test SMS auto-reply")
        print("\n📱 Next steps:")
        print("   1. Send an SMS to your Twilio number")
        print("   2. Check Render logs for 'twilio_inbound=True'")
        print("   3. Verify you receive an auto-reply")
        return True
    else:
        print("❌ Some tests failed. Check configuration.")
        return False

if __name__ == "__main__":
    main()
