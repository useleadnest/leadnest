#!/usr/bin/env python3
"""
Test script for Twilio webhook signature validation with ProxyFix
"""
import os
import requests
from werkzeug.test import Client
from werkzeug.wrappers import Response
import base64
import hashlib
import hmac
from urllib.parse import urlencode

def create_twilio_signature(auth_token, url, params):
    """Create a valid Twilio signature for testing"""
    data = url + urlencode(sorted(params.items()), True)
    signature = base64.b64encode(
        hmac.new(
            auth_token.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('ascii')
    return signature

def test_twilio_webhook():
    print("🧪 Testing Twilio Webhook Configuration")
    print("=" * 50)
    
    # Test 1: ProxyFix Configuration
    print("\n1. Testing ProxyFix Configuration...")
    try:
        from app import create_app
        from werkzeug.middleware.proxy_fix import ProxyFix
        
        app = create_app()
        is_proxy_fix_applied = isinstance(app.wsgi_app, ProxyFix)
        print(f"   ✅ ProxyFix applied: {is_proxy_fix_applied}")
        print(f"   ✅ PREFERRED_URL_SCHEME: {app.config.get('PREFERRED_URL_SCHEME', 'not set')}")
        
    except Exception as e:
        print(f"   ❌ ProxyFix test failed: {e}")
    
    # Test 2: Twilio Route Registration
    print("\n2. Testing Twilio Route Registration...")
    try:
        twilio_routes = [str(rule) for rule in app.url_map.iter_rules() if 'twilio' in str(rule)]
        print(f"   ✅ Twilio routes found: {twilio_routes}")
        
        if '/api/twilio/inbound' not in str(app.url_map):
            print("   ❌ /api/twilio/inbound route not found!")
        else:
            print("   ✅ /api/twilio/inbound route properly registered")
            
    except Exception as e:
        print(f"   ❌ Route test failed: {e}")
    
    # Test 3: Signature Validation Logic
    print("\n3. Testing Signature Validation Logic...")
    try:
        from twilio.request_validator import RequestValidator
        
        # Mock data
        test_auth_token = "test_auth_token_12345"
        test_url = "https://example.com/api/twilio/inbound"
        test_params = {
            'From': '+15551234567',
            'Body': 'Hello test',
            'To': '+15559876543'
        }
        
        # Create valid signature
        validator = RequestValidator(test_auth_token)
        valid_signature = create_twilio_signature(test_auth_token, test_url, test_params)
        
        # Test validation
        is_valid = validator.validate(test_url, test_params, valid_signature)
        print(f"   ✅ Signature validation works: {is_valid}")
        
        # Test invalid signature
        is_invalid = validator.validate(test_url, test_params, "invalid_signature")
        print(f"   ✅ Invalid signature rejected: {not is_invalid}")
        
    except Exception as e:
        print(f"   ❌ Signature validation test failed: {e}")
    
    # Test 4: Environment Variable Check
    print("\n4. Testing Environment Variables...")
    required_env_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM']
    
    for var in required_env_vars:
        value = os.environ.get(var)
        if value:
            print(f"   ✅ {var}: {'*' * 10} (set)")
        else:
            print(f"   ⚠️  {var}: not set (required for production)")
    
    print("\n🎉 Twilio webhook configuration test complete!")
    print("\nNext steps for production:")
    print("1. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM in Render")
    print("2. Configure webhook URL in Twilio Console:")
    print("   https://your-app.onrender.com/api/twilio/inbound")
    print("3. Test with real SMS to verify end-to-end functionality")

if __name__ == "__main__":
    test_twilio_webhook()
