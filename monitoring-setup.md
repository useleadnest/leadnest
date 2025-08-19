# 📊 LEADNEST MONITORING & OBSERVABILITY SETUP

## 🎯 Quick Production Health Checks

```bash
# Health/readiness
curl -s https://api.useleadnest.com/healthz
curl -s https://api.useleadnest.com/readyz

# Auth flow (adjust email/pass/token)
curl -X POST https://api.useleadnest.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"********"}'

# Authenticated ping
curl -H "Authorization: Bearer <JWT>" https://api.useleadnest.com/api/me

# Twilio webhook (from Twilio console test)
curl -X POST https://api.useleadnest.com/api/twilio/inbound \
  -d "From=+15555555555&Body=test"

# Stripe webhook (use Stripe CLI in your terminal)
stripe listen --forward-to https://api.useleadnest.com/api/stripe/webhook
```

## 📈 Observability & Alerts Setup

### 1. Uptime Monitoring

**Recommended Services:**
- **UptimeRobot** (free tier available)
- **Pingdom** 
- **StatusCake**
- **Datadog Synthetics**

**Endpoints to Monitor:**
```
✅ https://api.useleadnest.com/healthz (every 1-2 min)
✅ https://api.useleadnest.com/readyz (every 5 min)
✅ Protected endpoint test (with canary JWT token, every 10 min)
```

**Alert Conditions:**
- Health check fails 2+ times in 5 minutes
- Response time > 2000ms for 3+ consecutive checks
- SSL certificate expires in < 30 days

### 2. Error & Tracing

**Option A: Sentry (Recommended)**
```python
# Already configured in your Flask app!
# Just set SENTRY_DSN environment variable in Render
SENTRY_DSN=https://your-dsn@sentry.io/project-id
```

**Option B: Datadog APM**
```bash
# Add to requirements.txt
ddtrace[profile]==2.8.0

# Add to Render start command:
ddtrace-run gunicorn wsgi:app --bind 0.0.0.0:$PORT
```

**Option C: New Relic**
```bash
# Add to requirements.txt  
newrelic==9.2.0

# Add to start command:
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn wsgi:app
```

### 3. Dashboards & Metrics

**API Metrics to Track:**
```yaml
Request Metrics:
  - Requests per second (by route)
  - P95/P99 response latency
  - Error rate (4xx/5xx by route)
  - Request size distribution

User Metrics:
  - Active sessions
  - Login success/failure rate
  - Registration conversion
  - JWT token renewals

Business Metrics:
  - New leads per hour
  - SMS messages sent/received  
  - Stripe webhook success rate
  - User onboarding funnel
```

**Database Metrics:**
```yaml
Performance:
  - Active connections
  - Slow queries (>1s)
  - Deadlock frequency
  - Query throughput

Resources:
  - CPU utilization
  - Memory usage
  - Disk I/O
  - Connection pool usage

Health:
  - Table bloat percentage
  - Index usage efficiency
  - Replication lag (if applicable)
```

**Queue & Webhook Metrics:**
```yaml
Webhooks:
  - Twilio webhook success/failure rate
  - Stripe webhook processing time
  - Webhook retry attempts
  - Signature verification failures

Background Jobs:
  - Queue depth
  - Job processing time
  - Failed job count
  - Worker process health
```

### 4. Alerting & Paging

**Critical Alerts (Page Immediately):**
- API is down (health check fails)
- Error rate > 5% for 5+ minutes
- P95 latency > 3000ms for 10+ minutes
- Database CPU > 90% for 5+ minutes
- Webhook failure rate > 20% for 15+ minutes

**Warning Alerts (Slack/Email):**
- P95 latency > 1000ms for 15+ minutes
- Error rate > 2% for 15+ minutes
- Database connections > 80% of limit
- Disk space > 80% used
- SSL certificate expires in 7 days

**Business Alerts:**
- No new users in 6+ hours (during business hours)
- SMS webhook failures > 10% for 1+ hour
- Stripe payment failures spike

### 5. Log Aggregation

**Option A: Render Built-in Logs**
- Already available in Render dashboard
- Good for debugging and basic monitoring
- Limited retention and search

**Option B: External Log Service**
```python
# Add structured logging to your Flask app
import structlog

# Configure in app/__init__.py
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
```

**Services:**
- **LogDNA/Mezmo** (IBM)
- **Papertrail** (SolarWinds) 
- **Loggly** (SolarWinds)
- **Datadog Logs**

### 6. Implementation Priority

**Week 1 (Critical):**
1. ✅ Set up UptimeRobot for health checks
2. ✅ Configure Sentry error tracking (set SENTRY_DSN)
3. ✅ Create basic Slack/email alerts

**Week 2 (Important):**
4. Set up performance monitoring (Datadog/New Relic)
5. Configure webhook monitoring
6. Create operational dashboard

**Week 3 (Optimization):**
7. Add business metrics tracking
8. Set up log aggregation
9. Create runbooks for common issues

### 7. Sample Alert Configuration

**UptimeRobot Setup:**
```yaml
Monitor 1:
  Name: "LeadNest API Health"
  URL: "https://api.useleadnest.com/healthz"
  Type: HTTP(s)
  Interval: 1 minute
  Timeout: 30 seconds
  
Monitor 2:
  Name: "LeadNest API Readiness" 
  URL: "https://api.useleadnest.com/readyz"
  Type: HTTP(s)
  Interval: 5 minutes
  
Monitor 3:
  Name: "LeadNest Auth Test"
  URL: "https://api.useleadnest.com/api/me"
  Type: HTTP(s) 
  Headers: "Authorization: Bearer <canary-token>"
  Interval: 10 minutes
```

**Sentry Environment Variable:**
```bash
# In Render dashboard > Environment
SENTRY_DSN=https://your-public-key@o123456.ingest.sentry.io/123456
```

### 8. Cost Estimates

**Free Tier Options:**
- UptimeRobot: 50 monitors, 5-min intervals
- Sentry: 5K errors/month
- Render logs: Built-in (limited retention)

**Paid Recommendations (Scale-dependent):**
- Sentry Pro: ~$26/month (50K errors)
- Datadog: ~$15/host/month + $0.10/1M spans
- UptimeRobot Pro: ~$7/month (50 monitors, 1-min intervals)

**Total Monthly: ~$50-100 for comprehensive monitoring**

---

## 🚀 Quick Start Commands

```powershell
# Run comprehensive API test
.\production-test-suite.ps1

# Test specific endpoints
curl https://api.useleadnest.com/healthz
curl https://api.useleadnest.com/api/deployment-info
```

Your LeadNest API is production-ready! 🎉
