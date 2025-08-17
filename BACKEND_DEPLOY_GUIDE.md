# 🔥 Backend Deployment Verification Script

## Quick Health Check Commands

### Test API Endpoints (Run after deployment):
```bash
# Test health endpoint
curl https://leadnest-api.onrender.com/health

# Test API root
curl https://leadnest-api.onrender.com/

# Test API documentation
curl https://leadnest-api.onrender.com/docs

# Test authentication endpoint
curl -X POST https://leadnest-api.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### Expected Responses:
- **Health**: `{"status": "healthy", "service": "leadnest-api", "version": "1.0.0"}`
- **Root**: `{"message": "LeadNest API is running!"}`
- **Docs**: HTML page with API documentation

---

## 🧪 E2E Testing Script (Run after backend is live)

### Frontend to Backend Integration Test:
1. **Open**: https://leadnest-frontend-9ur0366lo-christians-projects-d64cce8f.vercel.app
2. **Sign Up**: Create account with test@leadnest.com
3. **Login**: Verify authentication works
4. **Dashboard**: Check if API calls succeed
5. **Lead Generation**: Test search functionality
6. **Export**: Download CSV file
7. **Stripe**: Test payment flow

### Success Criteria:
- ✅ No CORS errors in browser console
- ✅ API calls return data (not 404/500 errors)
- ✅ User can complete full journey
- ✅ Stripe webhooks receive events

---

## 🎯 Post-Deployment Checklist

### Once Backend is Live:
- [ ] API health check passes
- [ ] Frontend can connect to backend
- [ ] Database connections working
- [ ] Authentication flow functional
- [ ] Stripe webhooks responding
- [ ] Admin panel accessible

### Then Update Domain:
- [ ] Update DNS to point useleadnest.com to Vercel
- [ ] Verify HTTPS works on custom domain
- [ ] Test complete flow on production domain

---

## 🚀 Final GitHub Push

### After Everything is Working:
```bash
cd c:\Users\mccab\contractornest

# Create GitHub repository first, then:
git remote add origin https://github.com/YOUR_USERNAME/leadnest.git
git push -u origin main
git push origin v1.0.0
```

---

## 🎉 LAUNCH CONFIRMATION

### When All Systems Green:
✅ Frontend: https://useleadnest.com (live)
✅ Backend: https://leadnest-api.onrender.com (live)
✅ Database: PostgreSQL (connected)
✅ Payments: Stripe (processing)
✅ Domain: Custom domain (active)
✅ Version: GitHub tagged (v1.0.0)

**🚀 LEADNEST IS 100% LIVE AND REVENUE-READY! 🎯💰**
