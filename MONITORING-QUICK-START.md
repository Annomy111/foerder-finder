# EduFunds Monitoring - Quick Start Guide

**Time to implement**: 2-4 hours
**Cost**: $0 (100% free tier)
**Difficulty**: Beginner

---

## Phase 1: Structured Logging (30 minutes)

### Step 1: Install Dependencies

```bash
cd /Users/winzendwyers/Papa\ Projekt/backend
pip install structlog prometheus-client prometheus-fastapi-instrumentator
```

### Step 2: Update `main.py`

Add at the top:

```python
from utils.logging_config import configure_logging
from prometheus_fastapi_instrumentator import Instrumentator

# Configure logging on startup
configure_logging(env=os.getenv('ENV', 'development'))
```

Add after `app = FastAPI(...)`:

```python
# Add Prometheus metrics endpoint
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### Step 3: Test Locally

```bash
# Start API
uvicorn api.main:app --reload --port 8009

# Check metrics endpoint
curl http://localhost:8009/metrics

# Expected output:
# http_requests_total{method="GET",path="/metrics"} 1.0
# http_request_duration_seconds_bucket{...} 0.002
```

### Step 4: Replace `print()` with Structured Logging

**Before**:
```python
print(f'[INFO] User {user_id} generated draft')
```

**After**:
```python
from utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info(
    'draft_generated',
    user_id=user_id,
    school_id=school_id,
    funding_id=funding_id,
)
```

**Benefits**:
- ✅ Structured JSON output in production
- ✅ Automatic PII redaction
- ✅ Queryable in Loki/Grafana
- ✅ Timestamped with log level

---

## Phase 2: Prometheus + Grafana (90 minutes)

### Step 1: Run Monitoring Setup Script on OCI VM

```bash
# SSH to OCI VM
ssh -i ~/.ssh/be-api-direct opc@130.61.76.199

# Download and run setup script
curl -o monitoring_setup.sh https://raw.githubusercontent.com/.../monitoring_setup.sh
chmod +x monitoring_setup.sh
sudo bash monitoring_setup.sh
```

**What it installs**:
- Prometheus (metrics storage)
- Node Exporter (system metrics)
- Grafana (dashboards)
- Loki (log aggregation)
- Promtail (log shipper)

**Duration**: ~15 minutes

### Step 2: Configure FastAPI Log Output

Update systemd service to output JSON logs:

```bash
sudo nano /etc/systemd/system/foerder-api.service
```

Add environment variable:

```ini
[Service]
Environment="ENV=production"
Environment="LOG_LEVEL=INFO"
StandardOutput=append:/var/log/foerder-api.log
StandardError=append:/var/log/foerder-api.log
```

Restart service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart foerder-api
```

### Step 3: Access Grafana via SSH Tunnel

**Local machine**:
```bash
ssh -L 3000:localhost:3000 -L 9090:localhost:9090 -i ~/.ssh/be-api-direct opc@130.61.76.199
```

Open browser:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

**Grafana First Login**:
- Username: `admin`
- Password: `admin`
- Change password when prompted

### Step 4: Add Data Sources in Grafana

**Add Prometheus**:
1. Settings (gear icon) → Data Sources → Add data source
2. Select "Prometheus"
3. URL: `http://localhost:9090`
4. Click "Save & Test"

**Add Loki**:
1. Settings → Data Sources → Add data source
2. Select "Loki"
3. URL: `http://localhost:3100`
4. Click "Save & Test"

### Step 5: Import Pre-Built Dashboard

1. Dashboards (four squares icon) → Import
2. Upload JSON or paste Dashboard ID:
   - **FastAPI Dashboard**: 14282
   - **Node Exporter Full**: 1860
3. Select Prometheus data source
4. Click "Import"

**You now have real-time monitoring!**

---

## Phase 3: Uptime Monitoring (15 minutes)

### Step 1: Create UptimeRobot Account

Go to https://uptimerobot.com/signUp

### Step 2: Add Monitors

**Monitor 1: Frontend Health**
- Monitor Type: HTTP(s)
- URL: `https://app.foerder-finder.de/`
- Monitoring Interval: 5 minutes
- Alert Contacts: Your email

**Monitor 2: Backend API Health**
- Monitor Type: HTTP(s)
- URL: `https://api.foerder-finder.de/api/v1/health`
- Monitoring Interval: 5 minutes
- Keyword Alert: `"status": "healthy"`
- Alert Contacts: Your email

**Monitor 3: SSL Certificate**
- Monitor Type: Keyword
- URL: `https://app.foerder-finder.de`
- Alert when SSL expires in 30 days

**Monitor 4: DNS Resolution**
- Monitor Type: Port
- Domain: `foerder-finder.de`
- Port: 443
- Monitoring Interval: 30 minutes

### Step 3: Configure Alert Channels

**Slack Integration** (optional):
1. UptimeRobot → Integrations → Slack
2. Connect Slack workspace
3. Select channel: `#edufunds-alerts`

**Email Alerts** (included):
- Already configured with your account email

---

## Phase 4: Error Tracking with Sentry (30 minutes)

### Step 1: Create Sentry Account

Go to https://sentry.io/signup/

**Free Tier**: 5,000 errors/month

### Step 2: Create Project

1. Create Organization: "EduFunds"
2. Create Project: "edufunds-frontend"
3. Platform: React
4. Copy DSN: `https://xxx@xxx.ingest.sentry.io/xxx`

### Step 3: Install Sentry in Frontend

```bash
cd /Users/winzendwyers/Papa\ Projekt/frontend
npm install @sentry/react
```

### Step 4: Configure Sentry (`src/main.jsx`)

Add at the top:

```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  integrations: [
    new Sentry.BrowserTracing({
      routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        React.useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes
      ),
    }),
    new Sentry.Replay({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],

  // Performance monitoring
  tracesSampleRate: 0.1, // 10% of transactions

  // Session replay
  replaysSessionSampleRate: 0.1, // 10% of sessions
  replaysOnErrorSampleRate: 1.0, // 100% of errors

  environment: import.meta.env.MODE,
});
```

### Step 5: Add Environment Variable

Create `frontend/.env.local`:

```bash
VITE_SENTRY_DSN=https://YOUR_SENTRY_DSN
```

### Step 6: Test Error Tracking

Add test button in your app:

```javascript
<button onClick={() => {
  throw new Error("Test Sentry error!");
}}>
  Trigger Error
</button>
```

Click button → Check Sentry dashboard → Error should appear!

---

## Phase 5: Business Metrics Dashboard (60 minutes)

### Step 1: Install Metabase (Self-Hosted)

**On OCI VM**:

```bash
docker run -d -p 3001:3000 \
  -e "MB_DB_TYPE=postgres" \
  -e "MB_DB_DBNAME=metabase" \
  -e "MB_DB_PORT=5432" \
  -e "MB_DB_USER=metabase" \
  -e "MB_DB_PASS=secure_password_here" \
  -e "MB_DB_HOST=localhost" \
  -v metabase-data:/metabase-data \
  --name metabase metabase/metabase
```

**Or use Plausible Analytics** (Privacy-first):

```bash
git clone https://github.com/plausible/hosting
cd hosting
./start.sh
```

### Step 2: Create Business Metrics Dashboard

**Queries to add**:

1. **Daily Active Schools**
```sql
SELECT DATE(created_at) as date, COUNT(DISTINCT school_id) as schools
FROM applications
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;
```

2. **Draft Generation Success Rate**
```sql
SELECT
  COUNT(*) FILTER (WHERE status = 'success') as successful,
  COUNT(*) FILTER (WHERE status = 'error') as failed,
  ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'success') / COUNT(*), 2) as success_rate
FROM drafts
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';
```

3. **Top Funding Programs**
```sql
SELECT f.title, COUNT(a.id) as applications
FROM funding_opportunities f
JOIN applications a ON a.funding_id = f.id
WHERE a.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY f.id, f.title
ORDER BY applications DESC
LIMIT 10;
```

---

## Verification Checklist

After implementation, verify everything works:

### ✅ Structured Logging
- [ ] API logs are in JSON format
- [ ] PII is redacted (check for emails in logs)
- [ ] Log level is INFO in production
- [ ] Logs include `user_id`, `school_id`, timestamps

### ✅ Prometheus Metrics
- [ ] `/metrics` endpoint returns data
- [ ] `http_requests_total` counter incrementing
- [ ] `http_request_duration_seconds` histogram populating
- [ ] Custom metrics (e.g., `draft_generation_total`) working

### ✅ Grafana Dashboards
- [ ] Prometheus data source connected
- [ ] Loki data source connected
- [ ] At least 1 dashboard showing live data
- [ ] Can query logs via Loki

### ✅ Uptime Monitoring
- [ ] All 4 monitors are green
- [ ] Email alerts configured
- [ ] SSL certificate monitor active
- [ ] Test alert triggers correctly

### ✅ Sentry Error Tracking
- [ ] Frontend errors appear in Sentry
- [ ] Source maps uploaded (production builds)
- [ ] Session replays working
- [ ] User context attached to errors

### ✅ Business Metrics
- [ ] Metabase/Plausible accessible
- [ ] Connected to production database
- [ ] At least 3 queries returning data
- [ ] Dashboard auto-refreshes

---

## Common Issues & Fixes

### Issue: `/metrics` endpoint returns 404

**Fix**: Ensure Prometheus instrumentator is added in `main.py`:

```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### Issue: Logs not appearing in Loki

**Fix**: Check Promtail is reading correct log file:

```bash
sudo journalctl -u promtail -f
# Should show: "Reading file: /var/log/foerder-api.log"
```

Verify log file exists and has content:

```bash
ls -lh /var/log/foerder-api.log
tail -f /var/log/foerder-api.log
```

### Issue: Grafana shows "No data"

**Fix**: Check Prometheus is scraping FastAPI:

1. Open http://localhost:9090
2. Status → Targets
3. Verify `fastapi` target is "UP"

If DOWN, check firewall or FastAPI is running on port 8009.

### Issue: UptimeRobot shows "Down"

**Fix**: Ensure backend is accessible from public internet:

```bash
# Test from local machine
curl https://api.foerder-finder.de/api/v1/health

# Should return: {"status": "healthy"}
```

Check Cloudflare DNS settings and OCI security lists.

### Issue: Sentry not capturing errors

**Fix**: Verify DSN is correct in `.env`:

```bash
# Frontend
cat .env.local | grep SENTRY_DSN

# Test manually
Sentry.captureException(new Error("Test error"));
```

---

## Next Steps

After basic monitoring is running:

### Week 2: Alerting

1. Configure Grafana alerts for:
   - Error rate > 5%
   - Response time p95 > 2s
   - Disk usage > 80%

2. Set up Slack/Telegram notifications

3. Create on-call rotation (if team exists)

### Week 3: Advanced Metrics

1. Add custom business metrics:
   - User conversion funnel
   - Draft generation quality scores
   - Revenue indicators

2. Create executive dashboard (weekly email report)

3. Set up automated anomaly detection

### Week 4: Optimization

1. Review metrics and identify bottlenecks
2. Optimize slow database queries
3. Tune alert thresholds to reduce noise
4. Document runbooks for common incidents

---

## Cost Tracking

Track monthly costs to ensure you stay within budget:

| Service | Free Tier | Current Usage | Cost |
|---------|-----------|---------------|------|
| OCI VM | 24GB RAM, 4 OCPU | 8GB, 2 OCPU | $0 |
| Prometheus | Unlimited | 50k series | $0 |
| Grafana | Unlimited (self-hosted) | 1 instance | $0 |
| Loki | Unlimited (self-hosted) | 5GB/month | $0 |
| UptimeRobot | 50 monitors | 4 monitors | $0 |
| Sentry | 5k errors/month | 200 errors/month | $0 |
| Cloudflare Analytics | Unlimited | - | $0 |
| **TOTAL** | - | - | **$0/month** |

**Expected cost at 1,000 users**: $0-29/month (if Sentry free tier exceeded)

---

## Support & Resources

**Documentation**:
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
- Loki: https://grafana.com/docs/loki/
- Sentry: https://docs.sentry.io/

**Dashboards**:
- Grafana Dashboard Library: https://grafana.com/grafana/dashboards/

**Community**:
- Prometheus Community: https://prometheus.io/community/
- Grafana Community: https://community.grafana.com/

**Troubleshooting**:
- See `MONITORING-OBSERVABILITY-ARCHITECTURE.md` → Runbook section
- Check logs: `journalctl -u prometheus -f`
- Ask in Grafana Slack: https://grafana.slack.com/

---

**Last Updated**: 2025-11-03
**Estimated Implementation Time**: 2-4 hours
**Total Cost**: $0/month
