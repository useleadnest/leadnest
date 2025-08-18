# Sentry + Monitoring Integration

## Install Sentry Dependencies

### Frontend (React)
```bash
npm install --save @sentry/react @sentry/integrations @sentry/tracing
```

### Backend (Flask)
```bash
pip install sentry-sdk[flask]
```

## Frontend Sentry Setup

### 1. Environment Variables (Vercel)
```bash
VITE_SENTRY_DSN=https://YOUR_DSN@o123456.ingest.sentry.io/1234567
VITE_SENTRY_ENVIRONMENT=production
```

### 2. Sentry Init (src/main.tsx)
```typescript
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  integrations: [
    new BrowserTracing({
      routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        React.useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes
      ),
    }),
  ],
  environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || 'development',
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // Filter out expected errors
    if (event.exception) {
      const error = event.exception.values?.[0];
      if (error?.value?.includes('Network Error') || 
          error?.value?.includes('401')) {
        return null;
      }
    }
    return event;
  },
});
```

### 3. Error Boundary (src/components/ErrorBoundary.tsx)
```typescript
import * as Sentry from "@sentry/react";

const ErrorBoundary = Sentry.withErrorBoundary(
  ({ children }: { children: React.ReactNode }) => {
    return <>{children}</>;
  },
  {
    fallback: ({ error, resetError }) => (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Something went wrong
          </h1>
          <p className="text-gray-600 mb-4">
            We've been notified and are working on a fix.
          </p>
          <button 
            onClick={resetError}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Try again
          </button>
        </div>
      </div>
    ),
    beforeCapture: (scope, error) => {
      scope.setTag("errorBoundary", true);
    }
  }
);

export default ErrorBoundary;
```

## Backend Sentry Setup

### 1. Environment Variables (Render)
```bash
SENTRY_DSN=https://YOUR_DSN@o123456.ingest.sentry.io/1234567
SENTRY_ENVIRONMENT=production
```

### 2. Sentry Init (app/__init__.py)
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

# Sentry configuration
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            FlaskIntegration(transaction_style='endpoint'),
            RedisIntegration(),
            sentry_logging,
        ],
        environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),
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
            if isinstance(exc_value, (ValidationError, AuthError)):
                return None
    return event
```

### 3. Custom Error Handling
```python
@app.errorhandler(500)
def internal_error(error):
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
    sentry_sdk.capture_exception(e)
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred.'
    }), 500
```

## Monitoring Dashboard Setup

### Health Check Monitoring (UptimeRobot)
1. **API Health Check:**
   - URL: `https://api.useleadnest.com/api/health`
   - Interval: Every 5 minutes
   - Timeout: 30 seconds

2. **Frontend Health Check:**
   - URL: `https://useleadnest.com`
   - Interval: Every 5 minutes
   - Look for: Status 200 and "LeadNest" in content

### Performance Monitoring
1. **Response Time Alerts:**
   - Warn if response time > 2 seconds
   - Critical if response time > 5 seconds

2. **Error Rate Monitoring:**
   - Warn if error rate > 1%
   - Critical if error rate > 5%

### Database Monitoring (Redis)
1. **Memory Usage:**
   - Warn at 80% capacity
   - Critical at 95% capacity

2. **Connection Health:**
   - Monitor Redis connection pool
   - Alert on connection failures

## Logging Strategy

### Frontend Logging
```typescript
// Custom logger with Sentry integration
export const logger = {
  info: (message: string, extra?: any) => {
    console.info(message, extra);
    Sentry.addBreadcrumb({
      message,
      level: 'info',
      data: extra,
    });
  },
  
  warn: (message: string, extra?: any) => {
    console.warn(message, extra);
    Sentry.captureMessage(message, 'warning');
  },
  
  error: (message: string, error?: Error, extra?: any) => {
    console.error(message, error, extra);
    Sentry.captureException(error || new Error(message));
  },
};
```

### Backend Logging
```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage in routes
@app.route('/api/leads', methods=['POST'])
def create_lead():
    try:
        logger.info("Creating new lead", user_id=current_user.id)
        # ... create lead logic
        logger.info("Lead created successfully", lead_id=lead.id)
        return jsonify(lead_data)
    except Exception as e:
        logger.error("Failed to create lead", 
                    user_id=current_user.id, 
                    error=str(e))
        raise
```

## Alerts Configuration

### Critical Alerts (Immediate notification)
- API down (health check fails)
- Database connection lost
- Error rate > 5%
- Payment processing failures

### Warning Alerts (Daily digest)
- High response times
- Memory usage above 80%
- Error rate > 1%
- Failed background jobs

### Success Metrics (Weekly report)
- New user signups
- Successful payments
- Lead generation volume
- API response times
