# 📋 LEADNEST QUICK SETUP CARD

## 🚨 **3 CRITICAL STEPS TO GO LIVE** (Total: ~15 minutes)

### 1. **TWILIO WEBHOOK** (5 min)
```
🌐 Go to: console.twilio.com → Phone Numbers → Your Number
📝 Set Webhook: https://api.useleadnest.com/api/twilio/inbound  
📋 Method: POST
💾 Save
```

### 2. **STRIPE WEBHOOK** (5 min)  
```
🌐 Go to: dashboard.stripe.com → Developers → Webhooks
📝 Add Endpoint: https://api.useleadnest.com/api/stripe/webhook
📋 Events: customer.subscription.created, invoice.payment_succeeded
💾 Add Endpoint
```

### 3. **FRONTEND UPDATE** (5 min)
```javascript
// Update your .env or config:
API_BASE_URL = 'https://api.useleadnest.com'
// Redeploy frontend
```

---

## ✅ **VERIFICATION** (2 min)
```powershell
# Run this in terminal:
.\production-test-simple.ps1
# Should show all green ✅ results
```

---

## 🎉 **THEN YOU'RE LIVE!**

**API**: https://api.useleadnest.com ✅  
**Status**: Production Ready ✅  
**Database**: Connected ✅  
**Security**: Active ✅  

**Ready to onboard customers! 🚀**

---

*For detailed setup: See FINAL-SETUP-CHECKLIST.md*  
*For monitoring: See monitoring-setup.md*
