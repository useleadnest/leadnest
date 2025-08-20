#!/usr/bin/env python3
"""
Test Launch Multiplier Endpoints

Tests the onboarding and ROI endpoints locally.
"""

import requests
import json
import sys
from datetime import datetime


def test_endpoint(method, url, data=None, description=""):
    """Test an endpoint and report results."""
    print(f"\n🧪 {description}")
    print(f"   {method} {url}")
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  Connection failed - server not running at {url}")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def main():
    """Test Launch Multiplier endpoints."""
    print("🚀 Testing Launch Multiplier Endpoints")
    print("=" * 50)
    
    # Test configuration
    base_url = "http://localhost:5000/api"
    business_id = 1
    user_id = 1
    
    tests = [
        # Health check
        ("GET", f"{base_url}/launch-multiplier/health", None, "Launch Multiplier health check"),
        
        # Onboarding tests
        ("GET", f"{base_url}/launch-multiplier/onboarding/status?business_id={business_id}&user_id={user_id}", None, "Get onboarding status"),
        
        ("POST", f"{base_url}/launch-multiplier/onboarding/complete-step", {
            "user_id": user_id,
            "step": "connect_twilio",
            "data": {
                "account_sid": "AC123456789",
                "phone_number": "+1234567890"
            }
        }, "Complete Twilio onboarding step"),
        
        ("GET", f"{base_url}/launch-multiplier/onboarding/status?business_id={business_id}&user_id={user_id}", None, "Get updated onboarding status"),
        
        # ROI tests
        ("POST", f"{base_url}/launch-multiplier/roi/calculate", {
            "business_id": business_id
        }, "Calculate ROI for business"),
        
        ("GET", f"{base_url}/launch-multiplier/roi/status/{business_id}", None, "Get ROI status"),
    ]
    
    # Run tests
    passed = 0
    total = len(tests)
    
    for method, url, data, description in tests:
        if test_endpoint(method, url, data, description):
            passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Launch Multiplier endpoints are working.")
        return 0
    else:
        print("❌ Some tests failed. Check the server logs.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
