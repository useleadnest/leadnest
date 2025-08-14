#!/usr/bin/env python3
"""
LeadNest Production Key Verification Script

This script verifies that all production environment variables and API keys
are properly configured and functional.

Usage:
    python verify_keys.py

Prerequisites:
    - All environment variables must be set in .env file
    - Database must be accessible
    - Network connectivity for API tests
"""

import sys
import os
import logging
from typing import Dict, Any
import json
import traceback

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import config
    from database import engine, get_db
    from sqlalchemy import text
    import openai
    import stripe
    import requests
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class KeyVerifier:
    """Verify all production keys and services"""
    
    def __init__(self):
        self.results = {}
        print("🔍 LeadNest Production Key Verification")
        print("=" * 50)
    
    def verify_database_connection(self) -> bool:
        """Verify PostgreSQL database connection"""
        print("\n📊 Testing Database Connection...")
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"   ✅ Database connected successfully")
                print(f"   📋 PostgreSQL Version: {version[:50]}...")
                print(f"   🔗 Database URL: {config.database_url[:30]}...")
                self.results['database'] = {'status': 'success', 'version': version}
                return True
        except Exception as e:
            print(f"   ❌ Database connection failed: {str(e)}")
            self.results['database'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def verify_openai_api(self) -> bool:
        """Verify OpenAI API key"""
        print("\n🤖 Testing OpenAI API...")
        try:
            openai.api_key = config.openai_api_key
            
            # Test with a simple completion
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'API test successful'"}],
                max_tokens=10
            )
            
            message = response.choices[0].message.content.strip()
            print(f"   ✅ OpenAI API working correctly")
            print(f"   🤖 Test Response: {message}")
            print(f"   🔑 API Key: {config.openai_api_key[:20]}...")
            self.results['openai'] = {'status': 'success', 'response': message}
            return True
        except Exception as e:
            print(f"   ❌ OpenAI API test failed: {str(e)}")
            self.results['openai'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def verify_stripe_api(self) -> bool:
        """Verify Stripe API keys"""
        print("\n💳 Testing Stripe API...")
        try:
            stripe.api_key = config.stripe_secret_key
            
            # Test retrieving account info
            account = stripe.Account.retrieve()
            
            print(f"   ✅ Stripe API working correctly")
            print(f"   🏢 Account ID: {account.id}")
            print(f"   📧 Business Name: {account.business_profile.get('name', 'Not set')}")
            print(f"   🔑 Secret Key: {config.stripe_secret_key[:20]}...")
            print(f"   🔑 Publishable Key: {config.stripe_publishable_key[:20]}...")
            
            # Test webhook endpoint secret
            webhook_secret_status = "✅ Set" if config.stripe_webhook_secret else "❌ Missing"
            print(f"   🪝 Webhook Secret: {webhook_secret_status}")
            
            self.results['stripe'] = {
                'status': 'success', 
                'account_id': account.id,
                'business_name': account.business_profile.get('name', 'Not set')
            }
            return True
        except Exception as e:
            print(f"   ❌ Stripe API test failed: {str(e)}")
            self.results['stripe'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def verify_yelp_api(self) -> bool:
        """Verify Yelp API key"""
        print("\n🏪 Testing Yelp API...")
        try:
            headers = {'Authorization': f'Bearer {config.yelp_api_key}'}
            
            # Test with a simple business search
            url = "https://api.yelp.com/v3/businesses/search"
            params = {
                'term': 'construction',
                'location': 'San Francisco, CA',
                'limit': 1
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            business_count = len(data.get('businesses', []))
            
            print(f"   ✅ Yelp API working correctly")
            print(f"   🏢 Test Search Results: {business_count} businesses found")
            print(f"   🔑 API Key: {config.yelp_api_key[:20]}...")
            
            self.results['yelp'] = {'status': 'success', 'business_count': business_count}
            return True
        except Exception as e:
            print(f"   ❌ Yelp API test failed: {str(e)}")
            self.results['yelp'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def verify_frontend_url(self) -> bool:
        """Verify frontend URL configuration"""
        print("\n🌐 Testing Frontend URL...")
        try:
            frontend_url = config.frontend_url
            print(f"   📋 Frontend URL: {frontend_url}")
            
            # Try to ping the frontend (optional, might not be running)
            try:
                response = requests.get(frontend_url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Frontend is accessible")
                    status = 'accessible'
                else:
                    print(f"   ⚠️  Frontend returned status {response.status_code}")
                    status = 'configured_not_accessible'
            except requests.exceptions.RequestException:
                print(f"   ⚠️  Frontend is configured but not currently accessible")
                status = 'configured_not_accessible'
            
            self.results['frontend'] = {'status': status, 'url': frontend_url}
            return True
        except Exception as e:
            print(f"   ❌ Frontend URL test failed: {str(e)}")
            self.results['frontend'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def verify_auth_config(self) -> bool:
        """Verify authentication configuration"""
        print("\n🔐 Testing Auth Configuration...")
        try:
            print(f"   📋 Secret Key: {config.secret_key[:20]}...")
            print(f"   📋 Algorithm: {config.algorithm}")
            print(f"   📋 Token Expire Minutes: {config.access_token_expire_minutes}")
            
            # Test that secret key is sufficiently long
            if len(config.secret_key) < 32:
                print(f"   ⚠️  Warning: Secret key should be at least 32 characters")
                status = 'warning'
            else:
                print(f"   ✅ Auth configuration looks good")
                status = 'success'
            
            self.results['auth'] = {
                'status': status,
                'algorithm': config.algorithm,
                'expire_minutes': config.access_token_expire_minutes
            }
            return True
        except Exception as e:
            print(f"   ❌ Auth configuration test failed: {str(e)}")
            self.results['auth'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results.values() if r['status'] == 'success')
        warning_tests = sum(1 for r in self.results.values() if r['status'] == 'warning')
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Warnings: {warning_tests}")
        print(f"Failed: {total_tests - successful_tests - warning_tests}")
        
        print("\nDetailed Results:")
        for service, result in self.results.items():
            status_icon = {
                'success': '✅',
                'warning': '⚠️',
                'failed': '❌',
                'configured_not_accessible': '⚠️'
            }.get(result['status'], '❓')
            
            print(f"  {status_icon} {service.title()}: {result['status']}")
            if 'error' in result:
                print(f"    Error: {result['error']}")
        
        # Save results to file
        with open('verification_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n📝 Detailed results saved to verification_results.json")
        
        if successful_tests == total_tests:
            print("\n🎉 All tests passed! Your LeadNest backend is ready for production.")
            return True
        else:
            print(f"\n⚠️  {total_tests - successful_tests} tests failed. Please fix the issues above.")
            return False

def main():
    """Main verification function"""
    verifier = KeyVerifier()
    
    try:
        # Run all verification tests
        verifier.verify_database_connection()
        verifier.verify_openai_api()
        verifier.verify_stripe_api()
        verifier.verify_yelp_api()
        verifier.verify_frontend_url()
        verifier.verify_auth_config()
        
        # Print summary
        success = verifier.print_summary()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during verification: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
