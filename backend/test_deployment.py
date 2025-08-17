# 🚀 DEPLOYMENT VERIFICATION SCRIPT

import requests
import json
from datetime import datetime

def test_endpoints():
    base_url = "https://leadnest-backend-2.onrender.com"
    
    endpoints = [
        "/",
        "/health", 
        "/debug-info",
        "/test-deploy",
        "/status"
    ]
    
    print(f"🧪 Testing LeadNest Backend - {datetime.now().isoformat()}")
    print("=" * 60)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint} - {data.get('version', 'No version')}")
                if endpoint == "/":
                    print(f"   Database: {data.get('database_available', 'Unknown')}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"🔥 {endpoint} - Error: {str(e)[:50]}")
    
    # Test auth endpoints
    print("\n🔐 Testing Auth Endpoints:")
    auth_test_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        # Test registration
        response = requests.post(f"{base_url}/auth/register", 
                               json=auth_test_data, timeout=10)
        if response.status_code in [200, 400]:  # 400 is OK for "already exists"
            print("✅ /auth/register - Available")
        else:
            print(f"❌ /auth/register - Status: {response.status_code}")
            
        # Test login  
        response = requests.post(f"{base_url}/auth/login",
                               json=auth_test_data, timeout=10)
        if response.status_code in [200, 401]:  # Both are OK responses
            print("✅ /auth/login - Available")
        else:
            print(f"❌ /auth/login - Status: {response.status_code}")
            
    except Exception as e:
        print(f"🔥 Auth endpoints - Error: {str(e)[:50]}")
    
    # Test OpenAPI
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            openapi_data = response.json()
            endpoint_count = len(openapi_data.get("paths", {}))
            print(f"\n📋 OpenAPI: {endpoint_count} endpoints documented")
            if endpoint_count >= 7:
                print("✅ All endpoints loaded successfully!")
            else:
                print("⚠️  Some endpoints may be missing")
        else:
            print(f"❌ OpenAPI - Status: {response.status_code}")
    except Exception as e:
        print(f"🔥 OpenAPI - Error: {str(e)[:50]}")

if __name__ == "__main__":
    test_endpoints()
