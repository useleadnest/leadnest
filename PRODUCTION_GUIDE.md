# Production Configuration Guide for LeadNest

## Required GitHub Secrets

### Backend CI/CD (Choose ONE deployment method)

#### Option A: Deploy Hook (Recommended - Simplest)
```bash
RENDER_DEPLOY_HOOK_BACKEND=https://api.render.com/deploy/srv-YOUR_SERVICE_ID_HERE?key=YOUR_DEPLOY_KEY
RENDER_BACKEND_BASE_URL=https://your-api.onrender.com
SMOKE_EMAIL=admin@yourdomain.com
SMOKE_PASSWORD=your-test-password
```

#### Option B: Render API (More Control)
```bash
RENDER_API_KEY=rnd_YOUR_API_KEY_HERE
RENDER_SERVICE_ID=srv-YOUR_SERVICE_ID_HERE
RENDER_BACKEND_BASE_URL=https://your-api.onrender.com
SMOKE_EMAIL=admin@yourdomain.com
SMOKE_PASSWORD=your-test-password
```

### Frontend CI/CD
```bash
VERCEL_TOKEN=your_vercel_token_here
VERCEL_ORG_ID=team_YOUR_ORG_ID or prj_YOUR_PERSONAL_ID
VERCEL_PROJECT_ID=prj_YOUR_PROJECT_ID_HERE
VITE_API_BASE_URL=https://your-api.onrender.com
VITE_ENV_NAME=production
FRONTEND_PUBLIC_URL=https://your-app.vercel.app
```

## Render Service Configuration

### Web Service (Backend)
```yaml
name: leadnest-backend
runtime: python3
buildCommand: pip install -r requirements.txt
startCommand: gunicorn wsgi:app
plan: starter # or pro for production
region: oregon # choose closest to your users
healthCheckPath: /readyz
autoDeploy: true

# Auto-scaling (Pro plan)
scaling:
  minInstances: 1
  maxInstances: 3
  targetCPUPercentage: 70
```

### Environment Variables (Render)
```bash
# Required
DATABASE_URL=REDACTED_DATABASE_URL
JWT_SECRET=super-secure-production-secret-min-32-chars
PUBLIC_BASE_URL=https://your-api.onrender.com

# Optional but recommended
REDIS_URL=redis://red-xxx:6379/0
TWILIO_AUTH_TOKEN=REDACTED
IDEMPOTENCY_TTL_HOURS=24
FLASK_ENV=production
LOG_LEVEL=INFO

# Optional: Error tracking
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Worker Service (Background Jobs)
```yaml
name: leadnest-worker
runtime: python3
buildCommand: pip install -r requirements.txt
startCommand: python worker.py
plan: starter
region: oregon # same as web service
# Same environment variables as web service
```

### Database Service
```yaml
name: leadnest-db
plan: starter # or pro for production
region: oregon
version: 15 # PostgreSQL version
# Enable daily backups in production
```

### Redis Service
```yaml
name: leadnest-redis
plan: starter
region: oregon
# For background job queue
```

## Vercel Configuration

### Environment Variables (Vercel Dashboard)
```bash
VITE_API_BASE_URL=https://your-api.onrender.com
VITE_ENV_NAME=production
```

### Build Settings
```yaml
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm ci
Root Directory: frontend
Node.js Version: 18.x
```

## Post-Deployment Checklist

### 1. Initial Setup
- [ ] Run database migrations: Check Render deploy logs for `flask db upgrade`
- [ ] Create admin user via Render shell or API
- [ ] Test health endpoints: `/healthz` and `/readyz`
- [ ] Verify environment variables are set correctly

### 2. Smoke Testing
```bash
# Run comprehensive smoke tests
./test-leadnest.sh https://your-api.onrender.com admin@test.com your-password

# Or PowerShell on Windows
.\Test-LeadNest.ps1 -BaseUrl "https://your-api.onrender.com" -Email "admin@test.com" -Password "your-password"
```

### 3. Monitoring Setup
- [ ] Set up Render alerts for service health
- [ ] Configure log retention and monitoring
- [ ] Set up Sentry for error tracking (optional)
- [ ] Monitor performance and scaling metrics

### 4. Security Verification
- [ ] Verify HTTPS is enforced
- [ ] Check CORS settings are restrictive
- [ ] Confirm rate limiting is active
- [ ] Test JWT token expiration
- [ ] Verify environment isolation

### 5. Feature Testing
- [ ] User registration and login
- [ ] Lead CRUD operations
- [ ] CSV bulk import (small and large)
- [ ] Background job processing
- [ ] Twilio webhook (if configured)
- [ ] Idempotency behavior

## Monitoring & Alerts

### Health Check Endpoints
```bash
# Liveness probe (always returns 200 if app is running)
GET https://your-api.onrender.com/healthz

# Readiness probe (returns 200 only if DB is accessible)
GET https://your-api.onrender.com/readyz
```

### Key Metrics to Monitor
- Response times (95th percentile < 500ms)
- Error rates (< 1% for 5xx errors)
- Database connection pool usage
- Background job queue length
- Memory and CPU usage

### Recommended Alerts
- Service down for > 2 minutes
- Error rate > 5% for 5 minutes
- Response time > 2 seconds for 5 minutes
- Failed deploys
- Database connection failures

## Scaling Considerations

### When to Scale Up
- CPU usage consistently > 70%
- Response times > 1 second
- Queue backlog > 100 jobs
- Memory usage > 80%

### Horizontal Scaling
- Enable auto-scaling on Render Pro
- Use Redis for session storage if multiple instances
- Ensure database can handle connection pool growth
- Monitor and tune database queries

### Optimization Tips
- Add database indexes for frequently queried fields
- Implement caching for expensive operations
- Use background jobs for heavy processing
- Optimize frontend bundle size
- Enable CDN for static assets

## Backup & Recovery

### Database Backups
- Enable daily automated backups on Render
- Test restore procedures monthly
- Consider cross-region backup replication

### Application State
- Background jobs are stateless and can be retried
- User sessions stored in JWT tokens (stateless)
- File uploads stored in database or external storage

### Disaster Recovery
- Document recovery procedures
- Test failover scenarios
- Have monitoring during recovery
- Communicate status to users

## Cost Optimization

### Development
- Use Render free tier for staging environments
- Share staging database across environments
- Use local development for feature work

### Production
- Monitor usage patterns for right-sizing
- Use spot instances where applicable
- Implement graceful degradation for high load
- Regular cost reviews and optimization

## Common Issues & Solutions

### Deployment Issues
- **Build failures**: Check Python version and dependencies
- **Database migrations**: Ensure migrations run before app start
- **Environment variables**: Verify all required vars are set

### Runtime Issues
- **Slow responses**: Check database query performance
- **Memory leaks**: Monitor memory usage trends
- **Background job failures**: Check Redis connectivity

### Frontend Issues
- **API errors**: Verify CORS settings and API URL
- **Build failures**: Check Node.js version and dependencies
- **Environment variables**: Ensure Vite vars are set correctly

## Support & Maintenance

### Regular Tasks
- Review error logs weekly
- Update dependencies monthly
- Performance reviews quarterly
- Security audits semi-annually

### Emergency Procedures
- Have rollback plan ready
- Monitor during deployments
- Keep emergency contacts updated
- Document incident response

---

**🚀 You're now ready for production! Remember to run the smoke tests after any deployment.**
