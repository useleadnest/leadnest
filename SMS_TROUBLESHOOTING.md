# SMS Integration Troubleshooting Guide

## 🚨 Current Issue: 500 Internal Server Error

Your webhook URL `https://api.useleadnest.com/api/twilio/inbound` is returning a 500 error, which means there's a server-side problem.

## 🔍 Step 1: Check Environment Variables in Render

**REQUIRED**: Go to your Render dashboard and verify these environment variables are set:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM=+1234567890
DATABASE_URL=postgresql://...
JWT_SECRET=your_jwt_secret
```

**To check in Render:**
1. Go to https://dashboard.render.com
2. Click your backend service
3. Go to "Environment" tab
4. Verify all variables are set with correct values

## 🔧 Step 2: Test the Debug Endpoint

I've added a debug endpoint to help diagnose the issue:

```bash
curl https://api.useleadnest.com/api/twilio/debug
```

This will tell you which environment variables are missing.

## 📱 Step 3: Configure Twilio Console

**IMPORTANT**: You need to configure the webhook URL in Twilio Console:

1. Go to https://console.twilio.com
2. Navigate to "Phone Numbers" → "Manage" → "Active numbers"
3. Click on your Twilio phone number
4. In the "Messaging" section, set:
   - **Webhook URL**: `https://api.useleadnest.com/api/twilio/inbound`
   - **HTTP Method**: `POST`
5. Click "Save Configuration"

## 🚀 Step 4: Deploy the Fixes

I've updated your code to:
- Add better error handling (prevents 500 errors)
- Add a debug endpoint to check configuration
- Improve logging for troubleshooting

To deploy:
```bash
git add .
git commit -m "Fix Twilio webhook error handling and add debug endpoint"
git push origin main
```

Render will automatically redeploy your app.

## 🧪 Step 5: Test the Integration

After deployment and configuration:

1. **Check debug endpoint:**
   ```bash
   curl https://api.useleadnest.com/api/twilio/debug
   ```
   Should return: `{"twilio_auth_token_set": true, ...}`

2. **Send test SMS:**
   - Send an SMS to your Twilio phone number
   - Should receive an auto-reply
   - Check Render logs for webhook activity

3. **Check Render logs:**
   - Go to Render dashboard → Your service → Logs
   - Look for webhook requests and any error messages

## 🔍 Common Issues & Solutions

### Issue: 403 Forbidden
- **Cause**: Invalid Twilio signature
- **Solution**: Verify `TWILIO_AUTH_TOKEN` matches your Twilio Console

### Issue: 500 Internal Server Error
- **Cause**: Missing environment variables or database issues
- **Solution**: Check all env vars are set, verify database connectivity

### Issue: No response to SMS
- **Cause**: Webhook not configured in Twilio Console
- **Solution**: Set webhook URL in Twilio phone number settings

### Issue: Webhook gets called but no data saved
- **Cause**: Database connectivity issues
- **Solution**: Check `DATABASE_URL` and database permissions

## 📋 Quick Checklist

- [ ] All environment variables set in Render
- [ ] Webhook URL configured in Twilio Console
- [ ] Code deployed to Render
- [ ] Debug endpoint returns all `true` values
- [ ] Test SMS sent to Twilio number
- [ ] Auto-reply received
- [ ] Data appears in database

## 🆘 If Still Not Working

1. **Check Render logs** for detailed error messages
2. **Test debug endpoint** to verify environment variables
3. **Verify Twilio Console configuration**
4. **Send me the output** of the debug endpoint
5. **Check Render service status** - ensure it's running

The most common issue is missing `TWILIO_AUTH_TOKEN` in the Render environment variables.
