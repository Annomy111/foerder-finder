# Monitoring Tools Comparison - EduFunds 2025

**Last Updated**: 2025-11-03
**Purpose**: Detailed comparison of all monitoring solutions evaluated

---

## Application Performance Monitoring (APM)

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| **Prometheus + Grafana** ⭐ | Open Source | $0 (self-hosted) | Industry standard, powerful PromQL, unlimited scale, OCI free tier covers storage | Requires self-hosting, learning curve | ✅ **RECOMMENDED** |
| Datadog | SaaS | $15/host/month + $0.10/GB logs | Best-in-class UX, all-in-one, great integrations | Very expensive, vendor lock-in, complex pricing | ❌ Too expensive |
| New Relic | SaaS | Free (100GB), then $49/month | Excellent free tier, easy setup, good docs | Sudden jump to $49/month, less flexible | ⚠️ Consider if prefer SaaS |
| SigNoz | Open Source | $0 (self-hosted) or $19/month | All-in-one (metrics + traces + logs), modern UI | Heavier resource usage, smaller community | ⚠️ Alternative to Prometheus |
| Dynatrace | SaaS | $70+/host/month | AI-powered, automatic discovery | Enterprise pricing, overkill for startup | ❌ Too expensive |
| AppDynamics | SaaS | $900+/month | Full-stack visibility | Enterprise only, very expensive | ❌ Too expensive |

**Winner**: **Prometheus + Grafana** (free, battle-tested, OCI-optimized)

---

## Error Tracking

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| **Sentry** ⭐ | SaaS | Free (5k errors), $26/month (50k) | Best React integration, session replay, excellent UX, source maps | Free tier limited | ✅ **RECOMMENDED** |
| Rollbar | SaaS | Free (5k events), $19/month (25k) | Similar to Sentry, good pricing | Smaller community, fewer integrations | ⚠️ Alternative to Sentry |
| Bugsnag | SaaS | Free (7.5k events), $59/month | Good mobile support | More expensive than Sentry | ❌ Not needed |
| LogRocket | SaaS | Free (1k sessions), $99/month | Session replay + analytics | Very expensive after free tier | ❌ Too expensive |
| PostHog | Open Source | Free (100k events), $0.00025/event | Generous free tier, analytics included | Less mature error tracking | ⚠️ If Sentry costs too high |

**Winner**: **Sentry** (best UX, free tier sufficient for 6-12 months)

---

## Log Aggregation

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| **Loki** ⭐ | Open Source | $0 (self-hosted) | Grafana-native, efficient storage (140x cheaper than ES), simple to operate | Less powerful full-text search | ✅ **RECOMMENDED** |
| Elasticsearch (ELK) | Open Source | $0 (self-hosted) | Powerful full-text search, mature ecosystem | Resource-heavy (4GB+ RAM), complex cluster management | ❌ Overkill |
| Splunk | SaaS | $150+/GB/month | Enterprise features, powerful search | Extremely expensive, complex licensing | ❌ Too expensive |
| Graylog | Open Source | $0 (self-hosted) | Good alternative to ELK, simpler | Smaller community than Loki/ELK | ⚠️ Alternative to Loki |
| Datadog Logs | SaaS | $0.10/GB ingested | Integrated with APM | Adds up quickly, vendor lock-in | ❌ Included in Datadog (not standalone) |

**Winner**: **Loki** (efficient, Grafana-native, free forever)

---

## Uptime Monitoring

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| **UptimeRobot** ⭐ | SaaS | Free (50 monitors, 5-min), $7/month (1-min) | Most generous free tier, multi-region, status page | 5-min interval (acceptable) | ✅ **RECOMMENDED** |
| Uptime Kuma | Open Source | $0 (self-hosted) | Unlimited monitors, beautiful UI | Requires self-hosting, maintenance | ⚠️ If need >50 monitors |
| Pingdom | SaaS | $10/month (10 checks) | Reliable, good UX | No free tier, expensive | ❌ No free tier |
| Better Stack | SaaS | Free (3 monitors), $18/month | Modern UI, good alerting | Free tier very limited | ❌ Free tier too small |
| StatusCake | SaaS | Free (10 monitors, 5-min) | Decent free tier | Less generous than UptimeRobot | ⚠️ Alternative |

**Winner**: **UptimeRobot** (50 free monitors unbeatable)

---

## Frontend Analytics

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| **Cloudflare Web Analytics** ⭐ | SaaS | $0 (unlimited) | Free, privacy-first, no cookies, Core Web Vitals, zero overhead | Less detailed than GA | ✅ **RECOMMENDED** |
| **Plausible** | Open Source | $0 (self-hosted), $9/month (cloud) | Privacy-first, beautiful UI, GDPR compliant | Self-hosted requires maintenance | ✅ **RECOMMENDED** |
| Google Analytics 4 | SaaS | Free | Most features, industry standard | Privacy concerns, cookie consent needed, complex | ⚠️ Use if GA required |
| Mixpanel | SaaS | Free (20M events), $25/month | Product analytics, funnels, cohorts | Free tier limited, expensive after | ❌ Overkill for now |
| Amplitude | SaaS | Free (10M events) | Good product analytics | Complex, overkill for startup | ❌ Overkill for now |

**Winner**: **Cloudflare Web Analytics** (free, instant setup) + **Plausible** (self-hosted for detailed analytics)

---

## Business Metrics Dashboard

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| **Metabase** ⭐ | Open Source | $0 (self-hosted), $85/month (cloud) | Beautiful UI, SQL queries, auto-refresh, easy to use | Self-hosted requires Docker | ✅ **RECOMMENDED** |
| Redash | Open Source | $0 (self-hosted) | SQL queries, good for technical users | Less pretty than Metabase | ⚠️ Alternative |
| Grafana | Open Source | $0 (already installed) | Can query databases directly | Not optimized for business metrics | ⚠️ Use for infra only |
| Tableau | SaaS | $15/user/month | Very powerful, enterprise features | Expensive, overkill for startup | ❌ Too expensive |
| Looker | SaaS | $3,000+/month | Enterprise BI | Extremely expensive | ❌ Too expensive |

**Winner**: **Metabase** (beautiful, free, easy for non-technical users)

---

## Distributed Tracing (Optional)

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| Jaeger | Open Source | $0 (self-hosted) | CNCF project, good Grafana integration | Requires setup, storage | ⚠️ Add later if needed |
| Tempo | Open Source | $0 (self-hosted) | Grafana-native, cost-effective storage | Newer, smaller community | ⚠️ Add later if needed |
| Zipkin | Open Source | $0 (self-hosted) | Mature, Twitter-proven | Older, less active development | ⚠️ Alternative |
| Honeycomb | SaaS | Free (20M events), $200+/month | Excellent observability-driven dev | Expensive after free tier | ❌ Too expensive |

**Winner**: **Not needed yet** (add Tempo in Phase 4 if distributed tracing becomes critical)

---

## Database Monitoring

### SQLite (Development)

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| **Custom Prometheus Exporter** ⭐ | DIY | $0 | Perfect fit for our stack | Need to write custom code | ✅ **RECOMMENDED** |
| sqlite-web | Open Source | $0 | Web interface, query explorer | Not metrics-focused | ⚠️ For debugging only |

**Winner**: **Custom Prometheus exporter** (log slow queries, track DB size)

### Oracle ATP (Production)

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| **OCI Monitoring** ⭐ | Built-in | $0 (free tier) | Free, native integration, performance insights | OCI-specific | ✅ **RECOMMENDED** |
| Prometheus + Exporter | Open Source | $0 | Unified with other metrics | Requires oracle_exporter setup | ⚠️ Add if OCI insufficient |

**Winner**: **OCI Monitoring** (free, included with ATP)

---

## Alert Management

| Tool | Type | Cost | Pros | Cons | Verdict |
|------|------|------|------|------|---------|
| **Grafana Alertmanager** ⭐ | Open Source | $0 (built-in) | Integrated with Prometheus, flexible routing | Learning curve | ✅ **RECOMMENDED** |
| PagerDuty | SaaS | Free (1 user), $19/user/month | Industry standard, on-call scheduling | Expensive for teams | ⚠️ Add if team grows |
| Opsgenie | SaaS | Free (5 users) | Good free tier, Atlassian integration | Less features than PagerDuty | ⚠️ Alternative |
| VictorOps | SaaS | $9/user/month | Good UX | No free tier | ❌ Not needed yet |

**Winner**: **Grafana Alertmanager** (free, sufficient for solo/small team)

---

## Summary Comparison Table

### Free Tier Limits

| Category | Tool | Free Tier Limit | Sufficient Until | Upgrade Cost |
|----------|------|-----------------|------------------|--------------|
| APM | Prometheus + Grafana | Unlimited (self-hosted) | Forever | $0 (always free) |
| Errors | Sentry | 5,000 errors/month | 6-12 months | $26/month |
| Logs | Loki | Unlimited (self-hosted) | Forever | $0 (always free) |
| Uptime | UptimeRobot | 50 monitors, 5-min | Forever | $7/month (1-min) |
| Analytics | Cloudflare | Unlimited | Forever | $0 (always free) |
| Analytics | Plausible | Unlimited (self-hosted) | Forever | $9/month (cloud) |
| Metrics | Metabase | Unlimited (self-hosted) | Forever | $0 (always free) |
| Alerts | Grafana | Unlimited | Forever | $0 (always free) |

**Total Monthly Cost (Current)**: **$0**

**Total Monthly Cost (After Growth)**: **$0-42**
- Sentry Team: $26/month (if >5k errors)
- UptimeRobot Pro: $7/month (optional)
- Plausible Cloud: $9/month (optional, can self-host)

---

## Feature Comparison Matrix

### Metrics Collection

| Feature | Prometheus | Datadog | New Relic | SigNoz |
|---------|-----------|---------|-----------|--------|
| HTTP metrics | ✅ Auto | ✅ Auto | ✅ Auto | ✅ Auto |
| Custom metrics | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| Query language | ✅ PromQL | ✅ DQL | ✅ NRQL | ✅ PromQL |
| Storage cost | ✅ $0 (OCI) | ❌ $15/host | ⚠️ $49/month | ✅ $0 (self) |
| Retention | ✅ 15+ days | ✅ 15 months | ✅ 90 days | ✅ Configurable |
| Alerting | ✅ Built-in | ✅ Advanced | ✅ Advanced | ✅ Built-in |
| Community | ✅ Huge | ✅ Large | ✅ Large | ⚠️ Growing |

**Winner**: **Prometheus** (free, powerful, large community)

### Error Tracking

| Feature | Sentry | Rollbar | Bugsnag | PostHog |
|---------|--------|---------|---------|---------|
| React integration | ✅ Excellent | ✅ Good | ✅ Good | ⚠️ Basic |
| Session replay | ✅ 50/month | ❌ No | ❌ No | ✅ 5k/month |
| Source maps | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Limited |
| Free tier | ✅ 5k errors | ✅ 5k events | ✅ 7.5k events | ✅ 100k events |
| Upgrade cost | ✅ $26/month | ✅ $19/month | ❌ $59/month | ✅ $0.00025/event |
| UX | ✅ Excellent | ⚠️ Good | ⚠️ Good | ⚠️ Basic |

**Winner**: **Sentry** (best UX, session replay, mature)

### Log Aggregation

| Feature | Loki | Elasticsearch | Splunk | Graylog |
|---------|------|---------------|--------|---------|
| Storage cost | ✅ Very low | ❌ High | ❌ Very high | ⚠️ Medium |
| Query language | ✅ LogQL | ✅ Lucene | ✅ SPL | ✅ Lucene |
| Grafana integration | ✅ Native | ⚠️ Plugin | ⚠️ Plugin | ⚠️ Plugin |
| Resource usage | ✅ Low | ❌ High (4GB+) | ❌ High | ⚠️ Medium |
| Full-text search | ⚠️ Limited | ✅ Excellent | ✅ Excellent | ✅ Good |
| Setup complexity | ✅ Simple | ❌ Complex | ❌ Complex | ⚠️ Medium |

**Winner**: **Loki** (efficient, Grafana-native, simple)

---

## Decision Matrix

### When to Use What

**Use Prometheus + Grafana If**:
- ✅ You have OCI/cloud infrastructure (free tier)
- ✅ You want complete control and no vendor lock-in
- ✅ You're comfortable with self-hosting
- ✅ You want free forever solution
- ✅ You value open-source ecosystems

**Use Datadog/New Relic If**:
- ❌ Budget is not a constraint ($180-900/month OK)
- ❌ You prefer all-in-one SaaS over self-hosting
- ❌ You need enterprise support and SLAs
- ✅ You want best-in-class UX
- ⚠️ You're willing to accept vendor lock-in

**Use Sentry If**:
- ✅ You have a frontend (React/Vue/Angular)
- ✅ You want best-in-class error tracking
- ✅ Free tier (5k errors) is sufficient
- ✅ You're willing to upgrade at $26/month later

**Use Loki If**:
- ✅ You already use Grafana for metrics
- ✅ You want cost-effective log storage
- ✅ Structured JSON logs are sufficient
- ⚠️ Full-text search is not critical

**Use UptimeRobot If**:
- ✅ You need external uptime monitoring
- ✅ Free tier (50 monitors) is sufficient
- ✅ 5-minute check interval is acceptable
- ✅ You want zero-maintenance solution

---

## Migration Paths

### From Free to Paid

**Sentry (5k → 50k errors)**:
- Trigger: >5,000 errors/month
- Cost: $26/month
- Timeline: Month 6-12
- Action: Enable error sampling first to delay

**UptimeRobot (5-min → 1-min)**:
- Trigger: SLA requires faster detection
- Cost: $7/month
- Timeline: Month 12+ (if needed)
- Action: Evaluate if 5-min truly insufficient

**Plausible (Self-Hosted → Cloud)**:
- Trigger: Self-hosting becomes burden
- Cost: $9/month
- Timeline: Month 6+ (optional)
- Action: Migrate data via export/import

### From Self-Hosted to SaaS

**Prometheus → Grafana Cloud**:
- Trigger: Self-hosting overhead too high
- Cost: $0 (free tier: 10k series, 50GB logs)
- Timeline: Month 12+ (if team <5 people)
- Action: Grafana Cloud has generous free tier

**Loki → Grafana Cloud Logs**:
- Trigger: Same as above
- Cost: Included in Grafana Cloud free tier
- Timeline: Same migration as Prometheus
- Action: Seamless transition

**Entire Stack → Datadog**:
- Trigger: Series B+ funding, engineering time > cost savings
- Cost: $180+/month
- Timeline: Year 2+
- Action: Export historical data, retrain team

---

## Cost Forecast (24 Months)

| Month | MAU | Errors/Month | Monitoring Cost | Notes |
|-------|-----|--------------|-----------------|-------|
| 1 | 10 | 50 | $0 | All free tiers |
| 3 | 50 | 200 | $0 | Well within limits |
| 6 | 200 | 800 | $0 | Still free |
| 9 | 500 | 2,000 | $0 | Still under 5k errors |
| 12 | 1,000 | 5,500 | $26 | Sentry upgrade |
| 15 | 2,000 | 8,000 | $26 | Stable |
| 18 | 5,000 | 15,000 | $26 | Still 50k errors tier |
| 21 | 8,000 | 25,000 | $26 | Stable |
| 24 | 10,000 | 40,000 | $26 | Still under 50k |

**Total Cost Year 1**: **~$78** ($6.50/month average)

**Total Cost Year 2**: **$312** ($26/month)

**Total 24 Months**: **$390** ($16.25/month average)

**Savings vs. Datadog**: **~$4,000** over 24 months

---

## Evaluation Checklist

Use this checklist when evaluating new monitoring tools:

### Must-Have Features
- [ ] Free tier or low-cost option
- [ ] Supports FastAPI/Python
- [ ] Supports React
- [ ] Clear pricing (no surprises)
- [ ] Export/migration path (no lock-in)
- [ ] Active community
- [ ] Good documentation

### Nice-to-Have Features
- [ ] Self-hosting option
- [ ] Open source
- [ ] Grafana integration
- [ ] Prometheus-compatible
- [ ] Multi-tenancy support
- [ ] API access
- [ ] Custom dashboards

### Deal-Breakers
- [ ] ❌ No free tier
- [ ] ❌ Unclear pricing
- [ ] ❌ Vendor lock-in (no export)
- [ ] ❌ Poor documentation
- [ ] ❌ Unmaintained (no updates >1 year)
- [ ] ❌ No Python/React support

---

## Conclusion

After evaluating 30+ monitoring tools, the recommended stack is:

1. **Prometheus + Grafana** (APM, $0)
2. **Loki** (Logs, $0)
3. **Sentry** (Errors, $0-26/month)
4. **UptimeRobot** (Uptime, $0)
5. **Cloudflare Analytics** (Frontend, $0)
6. **Metabase** (Business Metrics, $0)

**Total Cost**: **$0-26/month** for first 12 months

**Savings**: **$150-800/month** vs. commercial alternatives

**Recommendation**: **Implement immediately** - no downside, massive upside.

---

**Last Updated**: 2025-11-03
**Next Review**: 2026-02-03 (3 months after implementation)
