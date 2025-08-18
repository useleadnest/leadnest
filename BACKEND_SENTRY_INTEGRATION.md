# Backend Sentry Integration

## Install Sentry SDK
```bash
pip install sentry-sdk[flask]
```

## Environment Variables (Render)
```bash
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

## app/__init__.py Integration
```python
import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Sentry configuration
if os.getenv('SENTRY_DSN'):
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            FlaskIntegration(transaction_style='endpoint'),
            sentry_logging,
        ],
        environment=os.getenv('SENTRY_ENVIRONMENT', 'production'),
        traces_sample_rate=0.1,
        before_send=filter_sentry_events,
    )

def filter_sentry_events(event, hint):
    """Filter out noisy events"""
    if 'exception' in event:
        exc_info = hint.get('exc_info')
        if exc_info:
            exc_value = exc_info[1]
            # Filter out expected errors
            if 'ValidationError' in str(type(exc_value)) or '401' in str(exc_value):
                return None
    return event

# Add to your Flask app creation
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

def create_app():
    app = Flask(__name__)
    
    @app.errorhandler(500)
    def internal_error(error):
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(error)
        return jsonify({
            'error': 'Internal server error',
            'message': 'We\'ve been notified and are working on a fix.'
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return e
        
        # Log the error
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.capture_exception(e)
        
        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred.'
        }), 500
    
    return app
```

## Custom Error Logging in Routes
```python
import sentry_sdk

@app.route('/api/leads', methods=['POST'])
@jwt_required()
def create_lead():
    try:
        # Add context to Sentry
        sentry_sdk.set_context("user", {
            "id": current_user.id,
            "email": current_user.email
        })
        sentry_sdk.set_tag("endpoint", "create_lead")
        
        app.logger.info(f"Creating lead for user {current_user.id}")
        
        # Your lead creation logic here
        # ...
        
        app.logger.info(f"Lead created successfully: {lead.id}")
        return jsonify({'success': True, 'lead': lead_data})
        
    except ValidationError as e:
        app.logger.warning(f"Validation error creating lead: {str(e)}")
        return jsonify({'error': 'Invalid lead data', 'details': str(e)}), 400
        
    except Exception as e:
        app.logger.error(f"Error creating lead: {str(e)}", exc_info=True)
        sentry_sdk.capture_exception(e)
        return jsonify({'error': 'Failed to create lead'}), 500
```

## Performance Monitoring
```python
from sentry_sdk import start_transaction

@app.route('/api/leads/bulk-import', methods=['POST'])
@jwt_required()
def bulk_import():
    with start_transaction(op="bulk_import", name="process_csv") as transaction:
        try:
            transaction.set_tag("user_id", current_user.id)
            
            # Process CSV
            with transaction.start_child(op="parse", description="Parse CSV"):
                leads_data = parse_csv(file)
            
            # Validate and save
            with transaction.start_child(op="validate", description="Validate leads"):
                validated_leads = validate_leads(leads_data)
            
            with transaction.start_child(op="save", description="Save to database"):
                saved_leads = save_leads(validated_leads)
            
            transaction.set_data("leads_processed", len(saved_leads))
            return jsonify({'success': True, 'count': len(saved_leads)})
            
        except Exception as e:
            transaction.set_status("internal_error")
            raise
```

## Health Check Integration
```python
@app.route('/api/health')
def health_check():
    try:
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': os.getenv('APP_VERSION', '1.0.0'),
            'environment': os.getenv('SENTRY_ENVIRONMENT', 'production')
        }
        
        # Check database
        try:
            # Simple database query
            user_count = User.query.count()
            health_status['database'] = 'connected'
            health_status['user_count'] = user_count
        except Exception as e:
            health_status['database'] = 'error'
            health_status['database_error'] = str(e)
            sentry_sdk.capture_exception(e)
        
        # Check Redis
        try:
            from app.extensions import redis_client
            redis_client.ping()
            health_status['redis'] = 'connected'
        except Exception as e:
            health_status['redis'] = 'error'
            health_status['redis_error'] = str(e)
            sentry_sdk.capture_exception(e)
        
        return jsonify(health_status)
        
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

## Deployment Update Script
```python
# update_backend_sentry.py
import os
import subprocess

def update_requirements():
    """Add sentry-sdk to requirements.txt"""
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    
    if 'sentry-sdk' not in requirements:
        with open('requirements.txt', 'a') as f:
            f.write('\nsentry-sdk[flask]==1.39.1\n')
        print("Added sentry-sdk to requirements.txt")

def update_app_init():
    """Update app/__init__.py with Sentry integration"""
    init_file = 'app/__init__.py'
    
    # Read current content
    with open(init_file, 'r') as f:
        content = f.read()
    
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
    if 'sentry_sdk' not in content:
        updated_content = sentry_imports + content
        with open(init_file, 'w') as f:
            f.write(updated_content)
        print("Updated app/__init__.py with Sentry integration")

if __name__ == '__main__':
    update_requirements()
    update_app_init()
    print("Backend Sentry integration complete!")
    print("Don't forget to set SENTRY_DSN in your Render environment variables.")
```
