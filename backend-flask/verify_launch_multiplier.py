#!/usr/bin/env python3
"""
Launch Multiplier Onboarding and ROI Backend Verification

Verifies that all Launch Multiplier endpoints are properly registered
and the database models are working correctly.
"""

import sys
import json
from datetime import datetime, timedelta


def test_app_creation():
    """Test that Flask app can be created."""
    print("🚀 Testing Flask App Creation")
    print("-" * 40)
    
    try:
        from app import create_app
        app = create_app()
        
        # Count routes
        routes = list(app.url_map.iter_rules())
        launch_multiplier_routes = [r for r in routes if 'launch-multiplier' in r.rule]
        
        print(f"✅ Flask app created successfully!")
        print(f"   Total routes: {len(routes)}")
        print(f"   Launch Multiplier routes: {len(launch_multiplier_routes)}")
        
        # Show Launch Multiplier routes
        if launch_multiplier_routes:
            print("\n   Launch Multiplier Routes:")
            for route in launch_multiplier_routes:
                methods = ', '.join(route.methods - {'HEAD', 'OPTIONS'})
                print(f"     {methods:12} {route.rule}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create Flask app: {e}")
        return False


def test_database_models():
    """Test that database models can be imported and used."""
    print("\n🗄️  Testing Database Models")
    print("-" * 40)
    
    try:
        from app import create_app
        from app.models import db, Business, User, OnboardingProgress, ROIReport, ActivityLog
        
        app = create_app()
        
        with app.app_context():
            print("✅ All Launch Multiplier models imported successfully!")
            
            # Check if default business exists
            business = Business.query.first()
            if business:
                print(f"   Default business: {business.name} (ID: {business.id})")
            else:
                print("   No business found in database")
            
            # Test model creation (in memory only)
            print("\n   Testing model instantiation:")
            
            # OnboardingProgress
            progress = OnboardingProgress(
                user_id=1,
                step='connect_twilio',
                completed_at=datetime.utcnow(),
                data={'account_sid': 'AC123', 'phone_number': '+1234567890'}
            )
            print(f"   ✅ OnboardingProgress: {progress}")
            
            # ROIReport
            roi_report = ROIReport(
                business_id=1,
                period_start=datetime.utcnow() - timedelta(days=30),
                period_end=datetime.utcnow(),
                leads_received=45,
                deals_closed=7,
                estimated_revenue=35000.0,
                total_cost=2250.0,
                roi_percentage=1455.6
            )
            print(f"   ✅ ROIReport: {roi_report}")
            
            # ActivityLog
            activity = ActivityLog(
                business_id=1,
                action='onboarding_step_completed',
                description='Test activity',
                source='test'
            )
            print(f"   ✅ ActivityLog: {activity}")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to test database models: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_endpoint_functions():
    """Test that endpoint functions can be imported and inspected."""
    print("\n🌐 Testing Endpoint Functions")
    print("-" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        # Get Launch Multiplier endpoint functions
        launch_endpoints = []
        
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if 'launch-multiplier' in rule.rule:
                    endpoint = app.view_functions.get(rule.endpoint)
                    if endpoint:
                        launch_endpoints.append({
                            'rule': rule.rule,
                            'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                            'function': endpoint.__name__,
                            'doc': endpoint.__doc__
                        })
        
        print(f"✅ Found {len(launch_endpoints)} Launch Multiplier endpoints:")
        
        for ep in launch_endpoints:
            methods = ', '.join(ep['methods'])
            print(f"   {methods:12} {ep['rule']}")
            print(f"                Function: {ep['function']}")
            if ep['doc']:
                doc = ep['doc'].strip().split('\n')[0]  # First line only
                print(f"                Doc: {doc}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test endpoint functions: {e}")
        return False


def generate_api_documentation():
    """Generate API documentation for Launch Multiplier endpoints."""
    print("\n📚 Launch Multiplier API Documentation")
    print("=" * 50)
    
    try:
        from app import create_app
        
        app = create_app()
        
        endpoints_doc = {
            'onboarding': [],
            'roi': [],
            'health': []
        }
        
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if 'launch-multiplier' in rule.rule:
                    endpoint = app.view_functions.get(rule.endpoint)
                    if endpoint:
                        doc_entry = {
                            'method': list(rule.methods - {'HEAD', 'OPTIONS'})[0],
                            'path': rule.rule,
                            'description': endpoint.__doc__.strip() if endpoint.__doc__ else 'No description',
                            'function': endpoint.__name__
                        }
                        
                        if 'onboarding' in rule.rule:
                            endpoints_doc['onboarding'].append(doc_entry)
                        elif 'roi' in rule.rule:
                            endpoints_doc['roi'].append(doc_entry)
                        elif 'health' in rule.rule:
                            endpoints_doc['health'].append(doc_entry)
        
        # Print organized documentation
        for category, endpoints in endpoints_doc.items():
            if endpoints:
                print(f"\n## {category.title()} Endpoints")
                for ep in endpoints:
                    print(f"\n### {ep['method']} {ep['path']}")
                    print(f"**Description:** {ep['description']}")
                    print(f"**Function:** `{ep['function']}`")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate API documentation: {e}")
        return False


def main():
    """Run all Launch Multiplier backend verification tests."""
    print("🎯 Launch Multiplier Backend Verification")
    print("=" * 50)
    
    tests = [
        test_app_creation,
        test_database_models,
        test_endpoint_functions,
        generate_api_documentation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n⚠️  Test failed: {test.__name__}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All verification tests passed!")
        print("\n💡 Next Steps:")
        print("   1. Start the Flask server: flask run")
        print("   2. Test endpoints with: python test_launch_multiplier.py")
        print("   3. Build frontend components for onboarding and ROI")
        return 0
    else:
        print("❌ Some verification tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
