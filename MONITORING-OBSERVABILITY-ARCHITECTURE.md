# EduFunds Monitoring & Observability Architecture

**Date**: 2025-11-03
**Status**: Research Complete - Implementation Ready
**Budget Target**: $0-50/month (early-stage startup)

---

## Executive Summary

Comprehensive monitoring strategy for EduFunds (Förder-Finder Grundschule) leveraging **95% free/open-source tools** with optional low-cost upgrades. Total estimated cost: **$0-30/month** for early stage.

**Core Philosophy**:
- Start with free tier / open-source
- Instrument everything from day one
- Pay only when you scale
- Leverage existing OCI + Cloudflare infrastructure

---

## Current Infrastructure Baseline

### Backend
- **Framework**: FastAPI on OCI VM (130.61.76.199:8009)
- **Database**: SQLite (dev) / Oracle ATP (production)
- **Vector Store**: ChromaDB (local filesystem)
- **Process Manager**: Gunicorn + systemd
- **Logging**: Basic print statements + structlog (installed but not configured)

### Frontend
- **Platform**: Cloudflare Pages
- **Framework**: React 18 + Vite
- **CDN**: Cloudflare global network

### External Services
- **Scraper**: Crawl4AI (replacing self-hosted Firecrawl)
- **AI**: DeepSeek API
- **DNS/SSL**: Cloudflare

---

## Monitoring Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER TRAFFIC                             │
└────────────────┬────────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │   Cloudflare    │──────► Cloudflare Web Analytics (FREE)
        │   DNS + CDN     │        - Page views, devices, countries
        └────────┬────────┘        - Core Web Vitals
                 │                 - Zero setup required
                 │
    ┌────────────┴──────────────┐
    │                           │
┌───▼────┐              ┌───────▼──────┐
│Frontend│              │   Backend    │
│(Pages) │              │  OCI VM      │
└───┬────┘              └───────┬──────┘
    │                           │
    │                           │
    ├──► Sentry (FREE)          ├──► Prometheus (FREE)
    │    - 5k errors/mo         │    - Metrics collection
    │    - Source maps          │    - 500M datapoints/mo (OCI free)
    │    - Stack traces         │
    │                           ├──► Grafana (FREE)
    │                           │    - Dashboards
    │                           │    - Alerting
    │                           │
    │                           ├──► Loki (FREE)
    │                           │    - Log aggregation
    │                           │    - Structured JSON logs
    │                           │
    │                           ├──► Tempo (Optional)
    │                           │    - Distributed tracing
    │                           │
    │                           └──► UptimeRobot (FREE)
    │                                - 50 monitors
    │                                - 5-min checks
    │                                - SSL monitoring
    │
    └──► Business Metrics ──────────► Custom Dashboard
         - Applications created         - Metabase (FREE)
         - Funding programs found        - PostgreSQL
         - User journeys                 - Self-hosted
```

---

## Layer 1: Application Performance Monitoring (APM)

### Backend: Prometheus + Grafana Stack (100% FREE)

**Why**: Industry-standard, battle-tested, unlimited scale on OCI free tier.

#### Prometheus Setup (Metrics Collection)

**Installation on OCI VM**:
```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-arm64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-2.48.0.linux-arm64 /opt/prometheus
```

**Configuration** (`/opt/prometheus/prometheus.yml`):
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # FastAPI metrics
  - job_name: 'fastapi'
    static_configs:
      - targets: ['localhost:8009']
    metrics_path: '/metrics'

  # Node exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # ChromaDB metrics (custom exporter)
  - job_name: 'chromadb'
    static_configs:
      - targets: ['localhost:9101']
```

**FastAPI Integration** (`backend/api/monitoring.py`):
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

# Custom metrics
draft_generation_counter = Counter(
    'draft_generation_total',
    'Total AI drafts generated',
    ['status', 'funding_type']
)

draft_generation_duration = Histogram(
    'draft_generation_duration_seconds',
    'Time to generate draft',
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

rag_search_duration = Histogram(
    'rag_search_duration_seconds',
    'RAG search latency',
    buckets=[0.1, 0.5, 1, 2, 5]
)

funding_programs_total = Gauge(
    'funding_programs_total',
    'Total funding programs in database'
)

chromadb_documents = Gauge(
    'chromadb_documents_total',
    'Documents indexed in ChromaDB'
)

# Add to main.py
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

**systemd Service** (`/etc/systemd/system/prometheus.service`):
```ini
[Unit]
Description=Prometheus Monitoring System
After=network.target

[Service]
Type=simple
User=opc
ExecStart=/opt/prometheus/prometheus \
  --config.file=/opt/prometheus/prometheus.yml \
  --storage.tsdb.path=/opt/prometheus/data \
  --web.listen-address=127.0.0.1:9090
Restart=always

[Install]
WantedBy=multi-user.target
```

**Cost**: $0 (uses OCI free tier 500M datapoints/month)

#### Grafana Setup (Visualization)

**Installation**:
```bash
sudo apt-get install -y software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo apt-get update
sudo apt-get install grafana
```

**Pre-built Dashboards**:
1. **FastAPI Performance**
   - Request rate (req/sec)
   - Response time (p50, p95, p99)
   - Error rate by endpoint
   - Active connections

2. **Business Metrics**
   - Drafts generated (total, success rate)
   - Funding programs indexed
   - RAG search performance
   - User activity heatmap

3. **Infrastructure**
   - CPU, memory, disk usage
   - Database connections
   - ChromaDB document count

**Alerting Rules** (`/opt/prometheus/alerts.yml`):
```yaml
groups:
  - name: edufunds_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        annotations:
          summary: "High error rate detected"

      # Slow API responses
      - alert: SlowAPIResponses
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
        for: 5m
        annotations:
          summary: "95th percentile response time > 2s"

      # Draft generation failures
      - alert: DraftGenerationFailures
        expr: rate(draft_generation_total{status="error"}[10m]) > 0.1
        for: 5m
        annotations:
          summary: "Draft generation failing frequently"

      # Disk space
      - alert: DiskSpaceRunningOut
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.2
        for: 5m
        annotations:
          summary: "Less than 20% disk space remaining"
```

**Cost**: $0 (self-hosted on OCI VM)

---

### Frontend: Sentry (Error Tracking)

**Why**: Best-in-class error tracking, free tier perfect for early stage.

**Free Tier Limits**:
- 5,000 errors/month
- 50 session replays/month
- 1 user
- Source map support
- Stack traces with context

**Setup** (`frontend/src/main.jsx`):
```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  integrations: [
    new Sentry.BrowserTracing({
      // Track React Router navigation
      routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        React.useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes
      ),
    }),
    new Sentry.Replay({
      // Session replay for debugging
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],

  // Performance monitoring
  tracesSampleRate: 0.1, // 10% of transactions

  // Session replay
  replaysSessionSampleRate: 0.1, // 10% of sessions
  replaysOnErrorSampleRate: 1.0, // 100% of errors

  // Environment
  environment: import.meta.env.MODE,

  // Release tracking
  release: __APP_VERSION__,
});
```

**Custom Context**:
```javascript
// Add user context after login
Sentry.setUser({
  id: user.id,
  email: user.email,
  school_id: user.school_id,
});

// Track custom events
Sentry.addBreadcrumb({
  category: "funding",
  message: "User viewed funding program",
  data: { funding_id: id },
  level: "info",
});
```

**Cost**: $0/month (free tier sufficient for 6-12 months)

**Upgrade Path**: Team plan at $26/month when exceeding 5k errors

---

## Layer 2: Logging & Log Aggregation

### Structured Logging with Loki (100% FREE)

**Why**:
- Grafana-native (same dashboard as metrics)
- Stores logs efficiently (indexed by labels only)
- Free forever, unlimited scale

#### Backend: structlog + Loki

**Configuration** (`backend/utils/logging_config.py`):
```python
import structlog
import logging
import sys

def configure_logging(env: str = "development"):
    """
    Configure structured logging for FastAPI
    """

    # Processors chain
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Development: pretty console output
    if env == "development":
        processors.append(structlog.dev.ConsoleRenderer())
    # Production: JSON for Loki
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if env == "production" else logging.DEBUG,
    )

# Usage in routers
logger = structlog.get_logger()

@router.post("/generate-draft")
async def generate_draft(request: DraftRequest, user: User = Depends(get_current_user)):
    logger.info(
        "draft_generation_started",
        user_id=user.id,
        school_id=user.school_id,
        funding_id=request.funding_id,
    )

    try:
        draft = await generate_ai_draft(request)
        logger.info(
            "draft_generation_success",
            user_id=user.id,
            funding_id=request.funding_id,
            duration_ms=draft.generation_time,
        )
        return draft
    except Exception as e:
        logger.error(
            "draft_generation_failed",
            user_id=user.id,
            funding_id=request.funding_id,
            error=str(e),
            exc_info=True,
        )
        raise
```

**PII Redaction** (`backend/utils/logging_config.py`):
```python
import re

def redact_pii(logger, method_name, event_dict):
    """Redact sensitive information from logs"""
    sensitive_keys = ['password', 'token', 'api_key', 'secret', 'ssn']

    for key in event_dict.keys():
        if any(s in key.lower() for s in sensitive_keys):
            event_dict[key] = "***REDACTED***"

    # Redact email addresses
    message = event_dict.get('event', '')
    event_dict['event'] = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '***EMAIL***',
        message
    )

    return event_dict

# Add to processors
processors.insert(0, redact_pii)
```

#### Loki Setup

**Installation**:
```bash
wget https://github.com/grafana/loki/releases/download/v2.9.3/loki-linux-arm64.zip
unzip loki-linux-arm64.zip
sudo mv loki-linux-arm64 /opt/loki
```

**Configuration** (`/opt/loki/loki-config.yml`):
```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2023-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /opt/loki/index
    cache_location: /opt/loki/cache
    shared_store: filesystem
  filesystem:
    directory: /opt/loki/chunks

limits_config:
  retention_period: 30d  # Keep logs for 30 days
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20
```

**Promtail Setup** (Log Shipper):
```bash
wget https://github.com/grafana/loki/releases/download/v2.9.3/promtail-linux-arm64.zip
unzip promtail-linux-arm64.zip
sudo mv promtail-linux-arm64 /opt/promtail
```

**Promtail Config** (`/opt/promtail/promtail-config.yml`):
```yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  # FastAPI application logs
  - job_name: fastapi
    static_configs:
      - targets:
          - localhost
        labels:
          job: fastapi
          env: production
          __path__: /var/log/foerder-api.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            timestamp: timestamp
            message: event
            user_id: user_id
            school_id: school_id
      - labels:
          level:
          user_id:
          school_id:

  # Scraper logs
  - job_name: scraper
    static_configs:
      - targets:
          - localhost
        labels:
          job: scraper
          env: production
          __path__: /var/log/foerder-scraper.log

  # System logs
  - job_name: syslog
    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          __path__: /var/log/syslog
```

**Cost**: $0 (self-hosted)

**Log Retention**: 30 days (configurable)

---

## Layer 3: Uptime & Availability Monitoring

### UptimeRobot (100% FREE)

**Why**: Most generous free tier, perfect for startups.

**Free Tier**:
- 50 monitors
- 5-minute check intervals
- Multi-location checks
- SSL certificate monitoring
- Status page (public or private)

**Monitors to Create**:

1. **Frontend Health**
   - URL: `https://app.foerder-finder.de/`
   - Type: HTTP(s)
   - Interval: 5 minutes
   - Alert: Email + Slack

2. **Backend API Health**
   - URL: `https://api.foerder-finder.de/api/v1/health`
   - Type: HTTP(s)
   - Interval: 5 minutes
   - Keyword: `"status": "healthy"`
   - Alert: Email + Slack + PagerDuty (optional)

3. **SSL Certificate**
   - URL: `https://app.foerder-finder.de`
   - Type: SSL Certificate Monitoring
   - Alert: 30 days before expiry

4. **DNS Resolution**
   - Domain: `foerder-finder.de`
   - Type: DNS
   - Interval: 30 minutes

5. **ChromaDB Availability**
   - URL: `https://api.foerder-finder.de/api/v1/health`
   - Type: HTTP(s)
   - Keyword: `"chromadb": "healthy"`
   - Interval: 15 minutes

**Multi-Region Checks**: Automatically included (US, EU, Asia)

**Public Status Page**: `https://status.foerder-finder.de` (optional)

**Cost**: $0/month

**Upgrade Path**: $7/month for 1-minute intervals if needed

**Alternative**: **Uptime Kuma** (self-hosted, unlimited monitors)
```bash
docker run -d --restart=always -p 3001:3001 \
  -v uptime-kuma:/app/data \
  --name uptime-kuma louislam/uptime-kuma:1
```

---

## Layer 4: Business Metrics & Analytics

### Cloudflare Web Analytics (100% FREE)

**What You Get**:
- Page views
- Unique visitors
- Countries & devices
- Top pages & referrers
- Core Web Vitals (LCP, FID, CLS)
- Zero JavaScript overhead (server-side)

**Setup**: One-click in Cloudflare Pages dashboard

**Cost**: $0 (unlimited traffic)

### Custom Business Metrics Dashboard

**PostgreSQL + Metabase** (FREE, Self-Hosted)

**Metrics to Track**:
1. **User Acquisition**
   - New schools registered (daily/weekly/monthly)
   - Activation rate (% users creating first draft)
   - User retention (7-day, 30-day)

2. **Product Usage**
   - Applications created per school
   - Funding programs viewed
   - Draft generation success rate
   - Average time from search to application

3. **Content Health**
   - Total funding programs indexed
   - Programs scraped per day
   - Scraper success rate
   - RAG index freshness

4. **Revenue Indicators** (future)
   - Premium feature usage
   - Conversion to paid tier
   - MRR (Monthly Recurring Revenue)

**Metabase Setup**:
```bash
docker run -d -p 3000:3000 \
  -e "MB_DB_TYPE=postgres" \
  -e "MB_DB_DBNAME=edufunds" \
  -e "MB_DB_PORT=5432" \
  -e "MB_DB_USER=metabase" \
  -e "MB_DB_PASS=***" \
  -e "MB_DB_HOST=localhost" \
  --name metabase metabase/metabase
```

**Sample SQL Queries**:
```sql
-- Daily active schools
SELECT DATE(created_at) as date, COUNT(DISTINCT school_id) as active_schools
FROM applications
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at);

-- Draft generation funnel
SELECT
  COUNT(*) FILTER (WHERE status = 'started') as started,
  COUNT(*) FILTER (WHERE status = 'generated') as generated,
  COUNT(*) FILTER (WHERE status = 'submitted') as submitted,
  ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'submitted') /
    NULLIF(COUNT(*) FILTER (WHERE status = 'started'), 0), 2) as conversion_rate
FROM applications
WHERE created_at >= NOW() - INTERVAL '7 days';

-- Top funding programs by applications
SELECT f.title, COUNT(a.id) as applications
FROM funding_opportunities f
JOIN applications a ON a.funding_id = f.id
WHERE a.created_at >= NOW() - INTERVAL '30 days'
GROUP BY f.id, f.title
ORDER BY applications DESC
LIMIT 10;
```

**Cost**: $0 (self-hosted on OCI VM)

---

## Layer 5: Database Monitoring

### SQLite Monitoring (Development)

**Query Performance**:
```python
import time
import structlog

logger = structlog.get_logger()

def query_with_timing(query: str, params: tuple = ()):
    """Execute query with performance logging"""
    start = time.time()
    cursor.execute(query, params)
    duration = (time.time() - start) * 1000

    if duration > 100:  # Log slow queries
        logger.warning(
            "slow_query_detected",
            query=query[:100],
            duration_ms=duration,
        )

    return cursor.fetchall()
```

**Pragma Optimization**:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;  -- 64MB cache
PRAGMA temp_store = MEMORY;
```

### Oracle ATP Monitoring (Production)

**OCI Monitoring (FREE)**:
- Database CPU utilization
- Storage used vs allocated
- User calls per second
- Query response time

**Performance Insights** (included in ATP):
- Top SQL statements
- Wait events analysis
- Session activity

**Access**: OCI Console → Autonomous Database → Performance Hub

**Cost**: $0 (included in OCI free tier)

### ChromaDB Monitoring

**Custom Prometheus Exporter** (`backend/utils/chromadb_exporter.py`):
```python
from prometheus_client import Gauge
import chromadb
import os

chroma_client = chromadb.PersistentClient(
    path=os.getenv('CHROMA_DB_PATH', './chroma_db_dev')
)

chromadb_documents = Gauge('chromadb_documents_total', 'Total documents indexed')
chromadb_collections = Gauge('chromadb_collections_total', 'Total collections')

def update_chromadb_metrics():
    """Update ChromaDB metrics for Prometheus"""
    try:
        collection = chroma_client.get_collection(name='funding_docs')
        chromadb_documents.set(collection.count())
        chromadb_collections.set(1)
    except Exception as e:
        logger.error("chromadb_metrics_error", error=str(e))

# Call from background task every 60 seconds
```

---

## Layer 6: Cost Monitoring

### OCI Cost Analysis (FREE)

**Access**: OCI Console → Governance → Cost Analysis

**Alerts to Set**:
- Monthly budget: $50
- Alert at 80% ($40)
- Alert at 100% ($50)

**Metrics to Track**:
- Compute instance hours
- Block storage GB/month
- Database OCPUs
- Network egress (should be $0)

### API Cost Monitoring (DeepSeek)

**Track in Application**:
```python
import structlog
from prometheus_client import Counter, Histogram

logger = structlog.get_logger()

deepseek_api_calls = Counter(
    'deepseek_api_calls_total',
    'Total DeepSeek API calls',
    ['endpoint', 'status']
)

deepseek_tokens_used = Counter(
    'deepseek_tokens_total',
    'Total tokens consumed',
    ['type']  # prompt or completion
)

deepseek_cost_estimate = Counter(
    'deepseek_cost_usd_total',
    'Estimated DeepSeek API cost in USD'
)

async def call_deepseek_api(prompt: str, max_tokens: int = 2048):
    """Call DeepSeek with cost tracking"""
    start = time.time()

    try:
        response = await openai.ChatCompletion.acreate(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.5,
        )

        # Track usage
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens

        deepseek_tokens_used.labels(type='prompt').inc(prompt_tokens)
        deepseek_tokens_used.labels(type='completion').inc(completion_tokens)

        # DeepSeek pricing: ~$0.14 per 1M tokens
        cost = (prompt_tokens + completion_tokens) * 0.00000014
        deepseek_cost_estimate.inc(cost)

        deepseek_api_calls.labels(endpoint='chat', status='success').inc()

        logger.info(
            "deepseek_api_call",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
            duration_ms=(time.time() - start) * 1000,
        )

        return response

    except Exception as e:
        deepseek_api_calls.labels(endpoint='chat', status='error').inc()
        logger.error("deepseek_api_error", error=str(e))
        raise
```

**Monthly Report Query** (Prometheus):
```promql
# Total DeepSeek API cost this month
sum(increase(deepseek_cost_usd_total[30d]))

# Average tokens per request
rate(deepseek_tokens_total[1h]) / rate(deepseek_api_calls_total[1h])
```

---

## Alerting Strategy

### Alert Channels

**Free Options**:
1. **Email** (Gmail, any provider)
2. **Slack** (Free workspace)
3. **Telegram** (Free, instant notifications)
4. **Discord** (Free webhook)

**Paid (Optional)**:
5. **PagerDuty** ($0 for 1 user, then $19/user/month)
6. **Opsgenie** (Free tier: 5 users)

### Alert Severity Levels

**P0 - Critical** (wake up at 3am)
- API completely down (UptimeRobot)
- Database unreachable
- Error rate > 50%

**P1 - High** (respond within 1 hour)
- Error rate > 10%
- p95 response time > 5s
- Disk space < 10%

**P2 - Medium** (respond within 4 hours)
- Error rate > 5%
- p95 response time > 2s
- Draft generation success rate < 80%

**P3 - Low** (review next business day)
- Slow queries detected
- ChromaDB index stale (> 24h)
- SSL cert expiring in 30 days

### Alert Configuration (Grafana)

**Contact Points**:
```yaml
# Slack
- name: slack-alerts
  type: slack
  settings:
    url: https://hooks.slack.com/services/***
    recipient: "#edufunds-alerts"

# Email
- name: email-oncall
  type: email
  settings:
    addresses: oncall@foerder-finder.de
```

**Notification Policies**:
```yaml
# Route by severity
- matchers:
    - severity = "critical"
  contact_point: slack-alerts
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 30m

- matchers:
    - severity = "warning"
  contact_point: email-oncall
  group_wait: 5m
  group_interval: 1h
  repeat_interval: 24h
```

---

## User Analytics & Session Tracking

### Privacy-First Analytics

**Recommended**: **Plausible Analytics** (self-hosted, FREE)

**Why**:
- GDPR compliant (no cookies)
- Lightweight (<1KB script)
- Real-time dashboard
- Self-hosted = free forever

**Installation**:
```bash
docker run -d \
  --name plausible \
  -p 8000:8000 \
  -v plausible-data:/var/lib/postgresql/data \
  -e BASE_URL=https://analytics.foerder-finder.de \
  -e SECRET_KEY_BASE=$(openssl rand -base64 64) \
  plausible/analytics:latest
```

**Frontend Integration**:
```html
<script defer data-domain="app.foerder-finder.de"
  src="https://analytics.foerder-finder.de/js/script.js"></script>
```

**Custom Events**:
```javascript
// Track key user actions
plausible('Draft Generated', {
  props: { funding_type: 'Stiftung', status: 'success' }
});

plausible('Application Submitted', {
  props: { school_id: user.school_id }
});
```

**Cost**: $0 (self-hosted)

**Alternative**: Cloudflare Web Analytics (already included, but less granular)

---

## Security Monitoring

### 1. Fail2Ban (Brute Force Protection)

**Install on OCI VM**:
```bash
sudo apt install fail2ban
```

**Configuration** (`/etc/fail2ban/jail.local`):
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log

[fastapi-auth]
enabled = true
filter = fastapi-auth
logpath = /var/log/foerder-api.log
maxretry = 3
bantime = 7200
```

**Custom Filter** (`/etc/fail2ban/filter.d/fastapi-auth.conf`):
```ini
[Definition]
failregex = ^.*"POST /api/v1/auth/login.*401.*<HOST>.*$
ignoreregex =
```

### 2. OSSEC (Host Intrusion Detection)

**Optional for production**:
```bash
wget https://github.com/ossec/ossec-hids/archive/3.7.0.tar.gz
tar -xvzf 3.7.0.tar.gz
cd ossec-hids-3.7.0
sudo ./install.sh
```

**Monitors**:
- File integrity (config files, binaries)
- Log analysis (auth logs, API logs)
- Rootkit detection

**Cost**: $0 (open source)

### 3. Cloudflare WAF (Web Application Firewall)

**Free Tier Includes**:
- OWASP Top 10 protection
- DDoS mitigation
- Rate limiting (basic)
- Bot detection

**Enable**: Cloudflare Dashboard → Security → WAF

**Custom Rules** (Free):
```
# Block suspicious user agents
(http.user_agent contains "curl") and not (ip.src in {YOUR_MONITORING_IPS})

# Rate limit login endpoint
(http.request.uri.path eq "/api/v1/auth/login") and
(rate(1m) > 10)
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1) - FREE

**Day 1-2: Structured Logging**
- ✅ Configure structlog for FastAPI
- ✅ Add PII redaction
- ✅ Set up log rotation
- ✅ Test JSON output in production

**Day 3-4: Prometheus + Grafana**
- ✅ Install Prometheus on OCI VM
- ✅ Add FastAPI metrics endpoint
- ✅ Install Grafana
- ✅ Create first dashboard (API performance)

**Day 5-7: Uptime Monitoring**
- ✅ Create UptimeRobot account
- ✅ Add 5 monitors (frontend, API, SSL, DNS, ChromaDB)
- ✅ Configure Slack alerts
- ✅ Test incident workflow

**Outcome**: Basic observability operational, $0 cost

---

### Phase 2: Enrichment (Week 2) - $0-29/month

**Day 1-2: Loki + Promtail**
- ✅ Install Loki on OCI VM
- ✅ Configure Promtail log shipping
- ✅ Create Grafana log dashboard
- ✅ Set up log-based alerts

**Day 3-4: Sentry Error Tracking**
- ✅ Create Sentry project (free tier)
- ✅ Integrate frontend (React)
- ✅ Add source maps to build pipeline
- ✅ Configure error grouping rules

**Day 5-7: Business Metrics**
- ✅ Install Metabase (or Plausible)
- ✅ Create user acquisition dashboard
- ✅ Create product usage dashboard
- ✅ Create content health dashboard

**Outcome**: Production-grade observability, likely $0 (unless Sentry upgrade needed)

---

### Phase 3: Optimization (Week 3) - Optional

**Advanced Features**:
- Distributed tracing (Tempo)
- Custom ChromaDB exporter
- Automated anomaly detection
- Performance budgets

**Cost Optimization**:
- Review Prometheus retention (adjust to 15 days if needed)
- Implement log sampling for high-volume endpoints
- Optimize Sentry error grouping to stay under 5k/month

**Documentation**:
- Runbook for common incidents
- On-call rotation setup (if team grows)
- Monthly observability review process

---

### Phase 4: Scale (Month 2+)

**If traffic grows significantly**:

**Option A: Managed Prometheus** ($29/month)
- Grafana Cloud (free tier: 10k series, 50GB logs, 50GB traces)
- Upgrade when self-hosted Prometheus struggles

**Option B: All-in-One SaaS** ($49-99/month)
- New Relic (excellent free tier, then $49/month)
- Datadog (powerful but expensive, $15/host/month)
- SignalFx / Honeycomb

**My Recommendation**: Stay on free tier until **10k+ monthly active users**, then evaluate based on actual costs vs. engineering time.

---

## Cost Summary

### Year 1 Projection

| Month | Users | Costs | Notes |
|-------|-------|-------|-------|
| 1-3   | 10-50 | $0    | All free tiers |
| 4-6   | 50-200 | $0    | Still within free limits |
| 7-9   | 200-500 | $0-29 | May exceed Sentry free tier |
| 10-12 | 500-1000 | $29-79 | Sentry Team + possible Grafana Cloud |

**Total Year 1 Estimated Cost**: **$150-500** ($12-41/month average)

### At Scale (10k+ MAU)

| Service | Free Tier | Paid Tier | Annual |
|---------|-----------|-----------|--------|
| Sentry | 5k errors | $26/month (50k errors) | $312 |
| Grafana Cloud | 10k series, 50GB logs | Free likely sufficient | $0 |
| UptimeRobot | 50 monitors, 5min | $7/month (1min checks) | $84 |
| Plausible | Self-hosted | $9/month (managed) | $108 |
| **TOTAL** | **$0-29/month** | **$42-79/month** | **$504-948/year** |

**Conclusion**: Even at scale, monitoring costs stay under **$1000/year** (~2% of typical SaaS revenue at 10k MAU).

---

## Success Metrics

### Leading Indicators (Week 1)
- ✅ Logs flowing to Loki
- ✅ Prometheus scraping metrics
- ✅ UptimeRobot checks green
- ✅ Grafana dashboards populated

### Operational Metrics (Month 1)
- Mean Time to Detect (MTTD): < 5 minutes
- Mean Time to Resolve (MTTR): < 1 hour
- False positive alert rate: < 10%
- Uptime: > 99.5%

### Business Metrics (Month 3)
- Track 10+ business KPIs
- Weekly metrics review with team
- Data-driven product decisions
- User behavior insights actionable

---

## Alternatives Considered

### Why NOT These Options?

**Datadog** ($15/host/month = $180/year minimum)
- ❌ Too expensive for early stage
- ❌ Complex pricing model
- ✅ Best-in-class features (if budget allows)

**New Relic** (Free tier, then $49/month)
- ✅ Excellent free tier (100GB/month)
- ⚠️ Jump to $49/month if exceeded
- 🤔 Consider if you prefer all-in-one SaaS

**Elastic Stack (ELK)** (Free, self-hosted)
- ❌ Resource-heavy (needs 4GB+ RAM)
- ❌ Complex to maintain
- ✅ Great if you already have Elasticsearch

**AWS CloudWatch** ($0.30/GB ingested)
- ❌ Not on AWS
- ❌ Vendor lock-in

**Dynatrace / AppDynamics** ($70+/host/month)
- ❌ Enterprise pricing, overkill for startup

---

## Monitoring Dashboard Screenshot Concepts

### Dashboard 1: API Health (Grafana)

```
┌─────────────────────────────────────────────────────────────────┐
│  EduFunds API Health Dashboard                      🟢 HEALTHY  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Request Rate             Error Rate              Response Time │
│  ┌──────────────┐        ┌──────────────┐        ┌───────────┐│
│  │ 145 req/min  │        │   0.3% ⚠️    │        │  p95: 1.2s││
│  │      ↑ 12%   │        │   ↑ 0.1%     │        │  p99: 2.8s││
│  └──────────────┘        └──────────────┘        └───────────┘│
│                                                                  │
│  Top Endpoints by Traffic                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ GET  /api/v1/funding          │ 89 req/min │ 120ms avg │  │
│  │ POST /api/v1/drafts           │ 23 req/min │ 5.2s avg  │  │
│  │ POST /api/v1/auth/login       │ 12 req/min │  80ms avg │  │
│  │ GET  /api/v1/applications     │  8 req/min │ 200ms avg │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Draft Generation Performance (Last 24h)                        │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Success Rate: 94.2% ✅                                   │  │
│  │ Avg Duration: 4.8s                                       │  │
│  │ Total Drafts: 1,847                                      │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Dashboard 2: Business Metrics (Metabase)

```
┌─────────────────────────────────────────────────────────────────┐
│  EduFunds Business Metrics - October 2025                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Active Schools        Applications Created    Funding Programs │
│  ┌──────────────┐     ┌──────────────┐        ┌──────────────┐│
│  │     47       │     │    1,203     │        │     8,942    ││
│  │   ↑ +12      │     │   ↑ +187     │        │   ↑ +324     ││
│  └──────────────┘     └──────────────┘        └──────────────┘│
│                                                                  │
│  User Acquisition Funnel (Last 30 days)                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Signups       │ ████████████████████ 100% (58)         │  │
│  │ Activated     │ ███████████████░░░░░  75% (43)         │  │
│  │ Created Draft │ ████████████░░░░░░░░  60% (35)         │  │
│  │ Submitted App │ ██████████░░░░░░░░░░  52% (30)         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Top Funding Categories by Applications                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Stiftungen                    │ █████████████░ 487      │  │
│  │ Ministerien (Bund)            │ ███████████░░░ 412      │  │
│  │ Ministerien (Bundesländer)    │ ██████░░░░░░░░ 234      │  │
│  │ Sonstige                      │ ██░░░░░░░░░░░░  70      │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Runbook: Common Incidents

### Incident: High Error Rate Alert

**Triggered**: Error rate > 5% for 5 minutes

**Response**:
1. Check Grafana dashboard for affected endpoints
2. View recent errors in Sentry
3. Check Loki logs for stack traces
4. Identify root cause:
   - Database connection pool exhausted?
   - DeepSeek API timeout?
   - ChromaDB unavailable?
5. Mitigate:
   - Restart FastAPI service if needed
   - Increase connection pool size
   - Temporarily disable draft generation if DeepSeek down
6. Document in incident log

**Prevention**:
- Add retry logic with exponential backoff
- Increase timeouts for external APIs
- Add circuit breaker pattern

### Incident: Slow API Responses

**Triggered**: p95 response time > 2s for 10 minutes

**Response**:
1. Check Prometheus query performance dashboard
2. Identify slow queries in Loki logs
3. Check database CPU usage (OCI Monitoring)
4. Check ChromaDB index size
5. Optimize:
   - Add database indexes
   - Increase cache size
   - Reduce RAG search depth
6. Monitor improvement

### Incident: Draft Generation Failing

**Triggered**: Draft success rate < 80%

**Response**:
1. Check DeepSeek API status
2. View Sentry errors for stack traces
3. Check RAG search quality (empty results?)
4. Test manually with sample funding program
5. Fix:
   - Increase DeepSeek timeout
   - Rebuild ChromaDB index if stale
   - Adjust RAG search parameters
6. Re-enable draft generation

---

## Security & Compliance

### Data Retention

**Logs**: 30 days (configurable)
**Metrics**: 15 days (Prometheus), 1 year (aggregated)
**Error Reports**: 90 days (Sentry)
**User Analytics**: 12 months (Plausible)

### GDPR Compliance

**Personal Data in Logs**:
- ✅ PII redaction enabled (emails, names)
- ✅ User IDs pseudonymized
- ✅ IP addresses hashed
- ✅ Right to erasure: Script to delete user logs

**Analytics**:
- ✅ No cookies (Plausible)
- ✅ No personal identifiers
- ✅ Aggregated data only

### Access Control

**Grafana**:
- Admin: 1 user (you)
- Viewer: Team members (read-only dashboards)

**Sentry**:
- Admin: 1 user
- Member: Developers (can view/comment on errors)

**OCI Monitoring**:
- OCI admin only

---

## Next Steps

### Immediate (This Week)

1. **Install Prometheus + Grafana** on OCI VM
   - Estimated time: 2 hours
   - Risk: Low
   - Value: High

2. **Configure structlog** in FastAPI
   - Estimated time: 1 hour
   - Risk: Low
   - Value: High

3. **Set up UptimeRobot** monitors
   - Estimated time: 30 minutes
   - Risk: None
   - Value: High

### Short-Term (This Month)

4. **Add Sentry** error tracking to frontend
   - Estimated time: 1 hour
   - Risk: Low (free tier)
   - Value: High

5. **Install Loki + Promtail** for log aggregation
   - Estimated time: 3 hours
   - Risk: Medium (new service)
   - Value: Medium

6. **Create business metrics dashboard** (Metabase)
   - Estimated time: 4 hours
   - Risk: Low
   - Value: High (data-driven decisions)

### Long-Term (Quarter 1)

7. **Distributed tracing** with Tempo (optional)
8. **Automated anomaly detection** (ML-based)
9. **On-call rotation** setup (if team grows)
10. **Monthly observability review** process

---

## Conclusion

This monitoring architecture provides **enterprise-grade observability at startup costs**:

✅ **$0-29/month** for first 6-12 months
✅ **Complete visibility** into application health
✅ **Proactive alerting** before users notice issues
✅ **Data-driven decisions** with business metrics
✅ **Scalable** to 100k+ users without major changes

**Key Differentiators**:
- 100% free core stack (Prometheus, Grafana, Loki, UptimeRobot)
- Leverages existing OCI + Cloudflare infrastructure
- No vendor lock-in (can switch components anytime)
- Production-ready from day one

**Recommended First Step**: Install Prometheus + Grafana this week. You'll have real-time API metrics in 2 hours, setting the foundation for all other monitoring.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-03
**Maintainer**: Claude Code
**Review Cadence**: Quarterly (or when traffic 2x)
