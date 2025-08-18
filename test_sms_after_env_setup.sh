#!/bin/bash
# SMS Integration Test Script
# Run this after setting environment variables in Render

echo "🧪 Testing SMS Integration After Environment Variable Setup"
echo "========================================================"

echo ""
echo "1. Testing API Health..."
curl -s "https://api.useleadnest.com/healthz" | echo "Health: $(cat)"

echo ""
echo "2. Testing Debug Endpoint (should show all environment variables as 'true')..."
curl -s "https://api.useleadnest.com/api/twilio/debug" || echo "Debug endpoint not available yet"

echo ""
echo "3. Testing Webhook with Sample Data..."
curl -X POST "https://api.useleadnest.com/api/twilio/inbound" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "From=%2B18584223515&Body=Test+webhook&To=%2B18584223515" \
     -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "🎯 If environment variables are set correctly:"
echo "   - Debug endpoint should return all 'true' values"
echo "   - Webhook should return 403 (signature validation working)"
echo "   - Real SMS to +1 858 422 3515 should get auto-reply"

echo ""
echo "📱 Phone Numbers Configured:"
echo "   Primary: +1 858 422 3515 (webhook configured ✅)"
echo "   Toll-free: +1 855 914 4065 (needs webhook setup)"
