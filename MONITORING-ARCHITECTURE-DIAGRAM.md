# EduFunds Monitoring Architecture - Visual Diagrams

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER TRAFFIC (HTTPS)                               │
│                                                                              │
│  Browser → Cloudflare DNS → Cloudflare CDN → [Frontend/Backend]            │
│                      │                                                       │
│                      └──► Cloudflare Web Analytics (FREE)                   │
│                           - Page views, devices, countries                  │
│                           - Core Web Vitals (LCP, FID, CLS)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
        ┌───────────────────────┐      ┌───────────────────────┐
        │   Frontend (React)    │      │  Backend (FastAPI)    │
        │  Cloudflare Pages     │      │  OCI VM 130.61.76.199 │
        └───────────┬───────────┘      └───────────┬───────────┘
                    │                               │
                    │                               │
        ┌───────────▼───────────┐      ┌───────────▼────────────────────┐
        │  Sentry (Error Track) │      │  Prometheus (Metrics Storage)  │
        │  ───────────────────  │      │  ──────────────────────────── │
        │  • 5k errors/month    │      │  • /metrics endpoint           │
        │  • Session replays    │      │  • 500M datapoints/month FREE  │
        │  • Stack traces       │      │  • 15-day retention            │
        │  • Source maps        │      │  • Custom metrics              │
        │                       │      └───────────┬────────────────────┘
        │  FREE TIER            │                  │
        └───────────────────────┘                  │
                                         ┌─────────┴─────────┐
                                         │                   │
                                ┌────────▼────────┐ ┌────────▼────────┐
                                │  Grafana (UI)   │ │  Loki (Logs)    │
                                │  ────────────── │ │  ────────────── │
                                │  • Dashboards   │ │  • JSON logs    │
                                │  • Alerting     │ │  • 30d retention│
                                │  • Explore      │ │  • Label indexing│
                                │                 │ │  • Free forever │
                                │  FREE (self-    │ │                 │
                                │  hosted)        │ │  FREE           │
                                └─────────────────┘ └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        External Monitoring                                   │
│  ───────────────────────────────────────────────────────────────────────    │
│                                                                              │
│  UptimeRobot (FREE)                    Business Metrics (FREE)              │
│  ─────────────────                     ──────────────────────               │
│  • 50 monitors (5-min checks)          • Metabase / Plausible               │
│  • SSL certificate monitoring          • User acquisition funnel            │
│  • DNS monitoring                      • Draft generation stats             │
│  • Multi-region checks                 • Revenue indicators                 │
│  • Status page                         • PostgreSQL backend                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION INSTRUMENTATION                          │
└─────────────────────────────────────────────────────────────────────────────┘

   FastAPI Application (api.main:app)
          │
          │ [1] Prometheus Instrumentator
          │     → Captures all HTTP requests automatically
          │        ├─ http_requests_total (counter)
          │        ├─ http_request_duration_seconds (histogram)
          │        └─ http_requests_in_progress (gauge)
          │
          │ [2] Structured Logging (structlog)
          │     → All log events in JSON format
          │        ├─ timestamp (ISO 8601)
          │        ├─ level (DEBUG/INFO/WARNING/ERROR)
          │        ├─ event (message)
          │        ├─ user_id, school_id (context)
          │        └─ exc_info (stack traces)
          │
          │ [3] Custom Metrics
          │     → Business-specific tracking
          │        ├─ draft_generation_total
          │        ├─ rag_search_duration
          │        ├─ deepseek_api_calls_total
          │        └─ funding_programs_total
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA COLLECTION                                 │
└─────────────────────────────────────────────────────────────────────────────┘

   [Metrics Path]                        [Logs Path]
          │                                     │
          │                                     │
   Prometheus                              Promtail
   (scrapes /metrics)                      (reads /var/log/foerder-api.log)
   every 15 seconds                        real-time streaming
          │                                     │
          │                                     │
          ▼                                     ▼
   Prometheus TSDB                         Loki
   (time-series storage)                   (log aggregation)
   - 500M datapoints/month                 - Index by labels only
   - 15-day retention                      - 30-day retention
   - PromQL queries                        - LogQL queries
          │                                     │
          └──────────────┬──────────────────────┘
                         │
                         ▼
                    Grafana
                    (visualization + alerting)
                         │
                         ├─► Dashboards (real-time)
                         ├─► Alert Rules (Prometheus)
                         └─► Log Explorer (Loki)


┌─────────────────────────────────────────────────────────────────────────────┐
│                           ALERTING & NOTIFICATION                            │
└─────────────────────────────────────────────────────────────────────────────┘

   Grafana Alert Manager
          │
          ├─► [Critical] Error rate > 10%
          │      └─► Slack (#edufunds-alerts) + Email
          │
          ├─► [Warning] Response time p95 > 2s
          │      └─► Email only
          │
          └─► [Info] Disk usage > 80%
                 └─► Email only

   UptimeRobot
          │
          ├─► Frontend down (5-min check)
          │      └─► SMS + Email + Slack
          │
          ├─► Backend API down (5-min check)
          │      └─► SMS + Email + Slack
          │
          └─► SSL certificate expiring (daily check)
                 └─► Email (30 days before)
```

---

## Metrics Collection Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROMETHEUS SCRAPE TARGETS                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   FastAPI App        │  Port: 8009
│   (localhost:8009)   │  Path: /metrics
└──────────┬───────────┘
           │  Scrape every 15s
           │  ───────────────────────────────────────────────────────
           │  # HTTP Metrics (auto-generated)
           │  http_requests_total{method="POST",path="/api/v1/drafts"} 1847
           │  http_request_duration_seconds_bucket{le="0.5"} 1520
           │  http_requests_in_progress 12
           │
           │  # Custom Metrics
           │  draft_generation_total{status="success",funding_type="Stiftung"} 1740
           │  draft_generation_duration_seconds_sum 8934.2
           │  rag_search_duration_seconds_bucket{le="0.1"} 1650
           │  deepseek_tokens_total{type="prompt"} 3847293
           │  deepseek_cost_usd_total 0.538622
           │
           ▼
┌──────────────────────┐
│  Prometheus          │  Port: 9090
│  (localhost:9090)    │  Storage: /opt/prometheus/data
└──────────┬───────────┘
           │
           │  Query with PromQL
           │  ───────────────────────────────────────────────────────
           │  # Average response time (last 5 min)
           │  rate(http_request_duration_seconds_sum[5m]) /
           │    rate(http_request_duration_seconds_count[5m])
           │
           │  # Draft generation success rate
           │  sum(rate(draft_generation_total{status="success"}[5m])) /
           │    sum(rate(draft_generation_total[5m]))
           │
           │  # API requests per minute
           │  sum(rate(http_requests_total[1m])) by (path)
           │
           ▼
┌──────────────────────┐
│  Grafana Dashboard   │  Port: 3000
│  (localhost:3000)    │  http://localhost:3000
└──────────────────────┘


┌──────────────────────┐
│  Node Exporter       │  Port: 9100
│  (localhost:9100)    │  Path: /metrics
└──────────┬───────────┘
           │  Scrape every 15s
           │  ───────────────────────────────────────────────────────
           │  # System Metrics
           │  node_cpu_seconds_total{mode="idle"} 145832.21
           │  node_memory_MemAvailable_bytes 6442450944
           │  node_disk_io_time_seconds_total{device="sda"} 4328.1
           │  node_network_receive_bytes_total{device="eth0"} 9847293847
           │
           ▼
   Prometheus (same as above)
```

---

## Logging Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOG GENERATION                                     │
└─────────────────────────────────────────────────────────────────────────────┘

   FastAPI App (with structlog)
          │
          │  [Example Log Entry]
          │  {
          │    "timestamp": "2025-11-03T14:32:18.482Z",
          │    "level": "info",
          │    "event": "draft_generation_success",
          │    "user_id": 42,
          │    "school_id": 7,
          │    "funding_id": 1293,
          │    "duration_ms": 4821.3,
          │    "tokens_used": 3847,
          │    "cost_usd": 0.000538,
          │    "app": "edufunds-backend",
          │    "env": "production",
          │    "version": "1.0.0"
          │  }
          │
          ▼  (stdout → systemd → file)
   /var/log/foerder-api.log
          │
          │  [File contains NDJSON (newline-delimited JSON)]
          │  {"timestamp":"2025-11-03T14:32:18.482Z","level":"info",...}
          │  {"timestamp":"2025-11-03T14:32:19.123Z","level":"info",...}
          │  {"timestamp":"2025-11-03T14:32:20.847Z","level":"error",...}
          │
          ▼  (read by Promtail)
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOG SHIPPING (Promtail)                            │
└─────────────────────────────────────────────────────────────────────────────┘

   Promtail
          │
          │  [1] Read log file (tail -f)
          │  [2] Parse JSON
          │  [3] Extract labels (level, user_id, school_id)
          │  [4] Ship to Loki
          │
          ▼  (HTTP push to Loki)
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LOG STORAGE (Loki)                                    │
└─────────────────────────────────────────────────────────────────────────────┘

   Loki
          │
          │  [Storage Strategy]
          │  - Index ONLY by labels (efficient!)
          │    ├─ {job="fastapi", level="info"}
          │    ├─ {job="fastapi", level="error"}
          │    └─ {job="scraper", level="info"}
          │
          │  - Store log content in chunks
          │    └─ Full JSON preserved for querying
          │
          │  [Query Example - LogQL]
          │  {job="fastapi"} |= "draft_generation_failed" | json
          │
          ▼  (query via Grafana)
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LOG VISUALIZATION (Grafana)                             │
└─────────────────────────────────────────────────────────────────────────────┘

   Grafana → Explore Tab
          │
          │  [Query 1] All errors in last hour
          │  {job="fastapi", level="error"} [1h]
          │
          │  [Query 2] Draft generation failures
          │  {job="fastapi"} |= "draft_generation_failed" | json | line_format "{{.error}}"
          │
          │  [Query 3] Errors by user
          │  sum by (user_id) (count_over_time({job="fastapi", level="error"}[1h]))
          │
          └─► Output: Real-time log stream + filtering
```

---

## Alert Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ALERT RULES (Grafana)                               │
└─────────────────────────────────────────────────────────────────────────────┘

   [Rule 1] High Error Rate
   ────────────────────────
   Query: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
   For: 2 minutes
   Severity: Critical
          │
          │  [Triggered when error rate > 5% for 2 minutes]
          │
          ▼
   Alert Manager
          │
          ├─► [Notification 1] Slack (#edufunds-alerts)
          │      Message: "🚨 CRITICAL: Error rate at 8.3%"
          │               "Affected endpoints: /api/v1/drafts (92 errors)"
          │               "View logs: <Grafana link>"
          │
          └─► [Notification 2] Email (oncall@foerder-finder.de)
                 Subject: "[CRITICAL] High Error Rate - EduFunds API"
                 Body: Same as Slack + runbook link


   [Rule 2] Slow API Responses
   ────────────────────────────
   Query: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
   For: 5 minutes
   Severity: Warning
          │
          │  [Triggered when p95 latency > 2s for 5 minutes]
          │
          ▼
   Alert Manager
          │
          └─► [Notification] Email only
                 Subject: "[WARNING] Slow API Responses"
                 Body: "p95 latency: 2.8s (threshold: 2s)"


   [Rule 3] Draft Generation Failures
   ───────────────────────────────────
   Query: rate(draft_generation_total{status="error"}[10m]) > 0.1
   For: 5 minutes
   Severity: High
          │
          │  [Triggered when >10% draft generation fails]
          │
          ▼
   Alert Manager
          │
          ├─► [Notification 1] Slack
          │      Message: "⚠️ HIGH: Draft generation failing frequently"
          │               "Failure rate: 18.3% (threshold: 10%)"
          │               "Check DeepSeek API status"
          │
          └─► [Notification 2] Email
```

---

## Cost Breakdown Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONITORING COSTS (Monthly)                                │
└─────────────────────────────────────────────────────────────────────────────┘

   Component                     Free Tier Limit        Current Usage    Cost
   ─────────────────────────────────────────────────────────────────────────────

   ┌─────────────────────┐
   │ OCI Infrastructure  │      Always Free           8GB RAM          $0
   │  - VM compute       │      24GB, 4 OCPU          2 OCPU
   │  - Block storage    │      200GB                 50GB
   │  - Monitoring       │      500M datapoints/mo    50M datapoints
   └─────────────────────┘

   ┌─────────────────────┐
   │ Prometheus          │      Unlimited (self)      50k series       $0
   │  - TSDB storage     │      Disk limited          2.4GB
   │  - Retention        │      Configurable          15 days
   └─────────────────────┘

   ┌─────────────────────┐
   │ Grafana             │      Unlimited (self)      1 instance       $0
   │  - Dashboards       │      Unlimited             5 dashboards
   │  - Users            │      Unlimited             3 users
   └─────────────────────┘

   ┌─────────────────────┐
   │ Loki                │      Unlimited (self)      5GB/month        $0
   │  - Log ingestion    │      Disk limited          150MB/day
   │  - Retention        │      Configurable          30 days
   └─────────────────────┘

   ┌─────────────────────┐
   │ UptimeRobot         │      50 monitors           4 monitors       $0
   │  - Check interval   │      5 minutes             5 minutes
   │  - Status page      │      1 public page         1 page
   └─────────────────────┘

   ┌─────────────────────┐
   │ Sentry              │      5,000 errors/mo       ~200/month       $0
   │  - Session replays  │      50 replays/mo         ~10/month
   │  - Users            │      1 user                1 user
   └─────────────────────┘      [Upgrade: $26/mo for 50k errors]

   ┌─────────────────────┐
   │ Cloudflare Analytics│      Unlimited             All traffic      $0
   │  - Page views       │      No limit              5k views/mo
   │  - Core Web Vitals  │      Included              Yes
   └─────────────────────┘

   ┌─────────────────────┐
   │ Metabase            │      Unlimited (self)      1 instance       $0
   │  - Queries          │      Unlimited             15 queries
   │  - Dashboards       │      Unlimited             3 dashboards
   └─────────────────────┘

   ─────────────────────────────────────────────────────────────────────────────
   TOTAL MONTHLY COST (Current)                                         $0

   TOTAL MONTHLY COST (At 10k users, Sentry upgrade)                    $26

   TOTAL YEARLY COST (Year 1 average)                                   $150-300
```

---

## Deployment Timeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONITORING DEPLOYMENT TIMELINE                            │
└─────────────────────────────────────────────────────────────────────────────┘

Week 1: Foundation (Total: 4 hours)
────────────────────────────────────────────────────────────────────────────────

Day 1-2 (2 hours)
   ├─► Install dependencies (structlog, prometheus-client)
   ├─► Configure structured logging
   ├─► Update main.py with Prometheus instrumentator
   └─► Test locally (verify /metrics endpoint)

Day 3-4 (1.5 hours)
   ├─► SSH to OCI VM
   ├─► Run monitoring_setup.sh
   ├─► Configure systemd log output (JSON)
   └─► Verify services running

Day 5-7 (30 minutes)
   ├─► Create UptimeRobot account
   ├─► Add 4 monitors
   ├─► Configure alert channels
   └─► Test alerts

✓ Status: Basic observability operational ($0 cost)


Week 2: Enrichment (Total: 6 hours)
────────────────────────────────────────────────────────────────────────────────

Day 1-2 (2 hours)
   ├─► Access Grafana via SSH tunnel
   ├─► Add Prometheus + Loki data sources
   ├─► Import pre-built dashboards
   └─► Customize for EduFunds metrics

Day 3-4 (2 hours)
   ├─► Create Sentry account
   ├─► Install @sentry/react
   ├─► Configure error tracking
   └─► Test error capture

Day 5-7 (2 hours)
   ├─► Install Metabase (or Plausible)
   ├─► Connect to database
   ├─► Create business metrics queries
   └─► Build initial dashboard

✓ Status: Production-grade observability ($0 cost)


Week 3: Optimization (Total: 4 hours)
────────────────────────────────────────────────────────────────────────────────

   ├─► Review metrics and identify bottlenecks
   ├─► Configure Grafana alert rules
   ├─► Create runbooks for common incidents
   ├─► Optimize slow queries
   └─► Fine-tune alert thresholds

✓ Status: Optimized and automated ($0 cost)


Month 2+: Maintenance (Total: 2 hours/month)
────────────────────────────────────────────────────────────────────────────────

   ├─► Weekly metrics review (30 min/week)
   ├─► Monthly cost review
   ├─► Update dashboards as needed
   └─► Tune alerting based on incidents

✓ Status: Ongoing monitoring ($0-29/month)
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-03
**Maintainer**: Claude Code
