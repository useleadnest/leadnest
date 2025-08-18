#!/usr/bin/env python3
"""
Local Webhook Test Server
This creates a simple test server to debug webhook issues without Twilio signature validation
"""
import os
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_test_app():
    app = Flask(__name__)
    
    @app.route('/api/twilio/inbound', methods=['POST'])
    def test_webhook():
        """Test webhook without signature validation"""
        logger.info("Received webhook request")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Form data: {request.form.to_dict()}")
        
        # Extract form data
        from_number = request.form.get("From", "")
        body = request.form.get("Body", "")
        to_number = request.form.get("To", "")
        
        print(f"📱 SMS Received:")
        print(f"   From: {from_number}")
        print(f"   To: {to_number}")
        print(f"   Message: {body}")
        
        # Create TwiML response
        resp = MessagingResponse()
        resp.message(f"✅ Test webhook received your message: '{body}'")
        
        return str(resp), 200, {"Content-Type": "text/xml"}
    
    @app.route('/healthz')
    def health():
        return {"status": "healthy", "service": "sms-test-server"}
    
    return app

if __name__ == "__main__":
    print("🚀 Starting SMS Test Server")
    print("=" * 40)
    print("This server receives webhooks WITHOUT signature validation")
    print("Use for local testing only!")
    print("")
    print("To test:")
    print("1. Run this server")
    print("2. Use ngrok to expose it: ngrok http 5001") 
    print("3. Configure webhook URL in Twilio Console")
    print("4. Send SMS to your Twilio number")
    print("")
    
    app = create_test_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
