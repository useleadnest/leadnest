#!/usr/bin/env python3
"""
Update backend with Sentry integration
"""
import os

def update_requirements():
    """Add sentry-sdk to requirements.txt"""
    req_file = 'backend/requirements.txt'
    
    # Check if backend directory exists
    if not os.path.exists('backend'):
        req_file = 'requirements.txt'
    
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            requirements = f.read()
        
        if 'sentry-sdk' not in requirements:
            with open(req_file, 'a') as f:
                f.write('\nsentry-sdk[flask]==1.39.1\n')
            print(f"✅ Added sentry-sdk to {req_file}")
        else:
            print(f"✅ sentry-sdk already in {req_file}")
    else:
        print(f"❌ Requirements file not found: {req_file}")

def update_app_init():
    """Update app/__init__.py with Sentry integration"""
    init_files = [
        'backend/app/__init__.py',
        'app/__init__.py',
        'src/app.py',
        'main.py'
    ]
    
    init_file = None
    for f in init_files:
        if os.path.exists(f):
            init_file = f
            break
    
    if not init_file:
        print("❌ Could not find main Flask app file")
        return
    
    # Read current content
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Check if Sentry is already integrated
    if 'sentry_sdk' in content:
        print(f"✅ Sentry already integrated in {init_file}")
        return
    
    # Add Sentry imports at the top
    sentry_imports = '''import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Sentry configuration
if os.getenv('SENTRY_DSN'):
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR
    )
    
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            FlaskIntegration(transaction_style='endpoint'),
            sentry_logging,
        ],
        environment=os.getenv('SENTRY_ENVIRONMENT', 'production'),
        traces_sample_rate=0.1,
    )

'''
    
    # Update file
    updated_content = sentry_imports + content
    with open(init_file, 'w') as f:
        f.write(updated_content)
    print(f"✅ Updated {init_file} with Sentry integration")

def create_env_template():
    """Create environment variable template"""
    template = '''# Sentry Configuration
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production

# Add these to your Render environment variables:
# 1. Go to your Render service dashboard
# 2. Go to Environment tab
# 3. Add the above variables with your actual Sentry DSN
'''
    
    with open('SENTRY_ENV_TEMPLATE.txt', 'w') as f:
        f.write(template)
    print("✅ Created SENTRY_ENV_TEMPLATE.txt")

if __name__ == '__main__':
    print("🔧 Updating backend with Sentry integration...")
    update_requirements()
    update_app_init()
    create_env_template()
    print("\n🚀 Backend Sentry integration complete!")
    print("\n📝 Next steps:")
    print("1. Set SENTRY_DSN in your Render environment variables")
    print("2. Redeploy your backend service")
    print("3. Test error reporting")
