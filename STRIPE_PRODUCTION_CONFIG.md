# 🔴 STRIPE PRODUCTION CONFIGURATION

## LIVE MODE KEYS CONFIRMED

### Frontend Environment Variables (Vercel)
```bash
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_[SET_IN_VERCEL_DASHBOARD_ONLY]
```

### Backend Environment Variables (Render)
```bash
STRIPE_SECRET_KEY=sk_live_[SET_IN_RENDER_DASHBOARD_ONLY]
STRIPE_WEBHOOK_SECRET=whsec_[SET_IN_RENDER_DASHBOARD_ONLY]
```

## PRODUCTS & PRICES CONFIGURED

### Stripe Dashboard Setup Required:
1. **Products in Live Mode:**
   - Starter Plan: $299/month (recurring)
   - Pro Plan: $699/month (recurring) 
   - Enterprise Plan: $1,299/month (recurring)

2. **Price IDs for Backend:**
   ```python
   STRIPE_PRICE_IDS = {
       'starter': 'price_LIVE_STARTER_ID',
       'pro': 'price_LIVE_PRO_ID', 
       'enterprise': 'price_LIVE_ENTERPRISE_ID'
   }
   ```

3. **Customer Portal Features:**
   - Update payment method
   - View billing history
   - Cancel subscription
   - Update billing address

4. **Webhook Endpoint:**
   - URL: `https://api.useleadnest.com/api/stripe/webhook`
   - Events to listen for:
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`

## DEPLOYMENT CHECKLIST
- [ ] Update Vercel env vars with live publishable key
- [ ] Update Render env vars with live secret key and webhook secret
- [ ] Test checkout flow in live mode
- [ ] Verify webhook receives events from live transactions
