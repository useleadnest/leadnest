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

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        routes = {
            "/": {"status": "healthy", "service": "leadnest-api", "version": "1.0.0"},
            "/health": {"status": "healthy"},
            "/api/auth/test": {"message": "Pure Python server is working!"}
        }
        self.wfile.write(
            json.dumps(routes.get(self.path, {"error": "Not found"})).encode()
        )
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

port = int(os.environ.get("PORT", 8000))
server = HTTPServer(("", port), Handler)
print(f"✅ Server running on port {port}")
server.serve_forever()
