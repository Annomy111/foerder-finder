# Förder-Finder Grundschule - Projektspezifisches Memory

## Projektübersicht

**Name**: Förder-Finder Grundschule
**Typ**: SaaS-Plattform
**Ziel**: Automatisierte Aggregation und KI-gestützte Antragstellung für Fördermittel im Grundschulbereich

## Technologie-Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: Oracle Autonomous Database (ATP)
- **Vector Store**: ChromaDB (lokal auf OCI VM)
- **Scraping**: Scrapy mit Bright Data Proxy
- **AI**: DeepSeek API (RAG-basierte Antragsgenerierung)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **ORM**: cx_Oracle (direkte SQL-Queries)

### Frontend
- **Framework**: React 18 mit Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Routing**: React Router v6
- **API Client**: Axios

### Infrastructure
- **Backend Hosting**: Oracle Cloud Infrastructure (OCI VM - VM.Standard.A1.Flex)
- **Frontend Hosting**: Cloudflare Pages
- **DNS/CDN**: Cloudflare
- **SSL**: Let's Encrypt (certbot)
- **Secrets**: OCI Vault
- **Proxy**: Bright Data Rotating Proxies

## Architektur-Komponenten

### 1. Scraping Engine (Modul 1)
- **Zweck**: Kontinuierliche Extraktion von Fördermitteldaten
- **Scheduling**: cronjob alle 12 Stunden
- **Datenfluss**: Internet → Scrapy → OCI Autonomous DB
- **Proxy**: Bright Data für ethisches Scraping

### 2. RAG Indexing Service (Modul 2a)
- **Zweck**: Vektorisierung der Fördermitteltexte
- **Scheduling**: cronjob 30 Min nach Scraper
- **Datenfluss**: OCI DB → Chunking → Embedding → ChromaDB
- **Storage**: /opt/chroma_db/ auf OCI VM (Block Volume)

### 3. Backend API (Modul 2b & 3)
- **Zweck**: REST API für Frontend, RAG-Pipeline, Authentifizierung
- **Key Endpoints**:
  - `POST /api/v1/auth/login` - JWT Authentication
  - `GET /api/v1/funding` - Liste aller Fördermittel
  - `POST /api/v1/generate-draft` - KI-Antragsentwurf
  - `GET /api/v1/applications` - Antragsverwaltung
- **Process Manager**: gunicorn + systemd

### 4. Frontend (Modul 3)
- **Zweck**: Web-UI für Grundschulen
- **Features**:
  - Multi-Tenancy (Mandantenfähigkeit)
  - Förderübersicht mit Filtern
  - KI-Antragsgenerator
  - Antragsverwaltung

## Datenbank-Schema

**Haupttabellen**:
1. `SCHOOLS` - Mandanten (Grundschulen)
2. `USERS` - Nutzer mit Rollen (admin, lehrkraft)
3. `FUNDING_OPPORTUNITIES` - Gescrapte Fördermittel (inkl. cleaned_text für RAG)
4. `APPLICATIONS` - Anträge der Schulen
5. `APPLICATION_DRAFTS` - KI-generierte Entwürfe

**Wichtig**: KEINE Vektor-Tabelle in Oracle! Vektoren leben in ChromaDB.

## Deployment-Workflow

### OCI VM Setup
1. Provisioning: VM.Standard.A1.Flex (ARM, Free Tier)
2. Block Volume für ChromaDB mounten: `/opt/chroma_db/`
3. Security Lists: Port 443 (Cloudflare IPs), Port 22 (Admin IP)
4. Oracle Wallet für DB-Connection installieren

### Backend Deployment
```bash
# OCI VM
cd /opt/foerder-finder-backend
git pull
pip install -r requirements.txt
sudo systemctl restart foerder-api
sudo systemctl restart foerder-scraper.timer
sudo systemctl restart foerder-indexer.timer
```

### Frontend Deployment
```bash
# Lokal
cd frontend/
npm run build
npx wrangler pages deploy dist --project-name foerder-finder
```

### Cloudflare Configuration
- **DNS**:
  - `app.foerder-finder.de` → Cloudflare Pages
  - `api.foerder-finder.de` → OCI VM IP
- **SSL/TLS**: Full (Strict)
- **WAF**: Aktiv für `/api/`
- **Rate Limiting**:
  - `/api/v1/auth/login`: 10 req/min
  - `/api/v1/generate-draft`: 5 req/min

## Secrets Management (OCI Vault)

**Gespeicherte Secrets**:
- `ORACLE_WALLET` - DB Connection Wallet
- `DEEPSEEK_API_KEY` - DeepSeek API Key
- `BRIGHTDATA_PROXY_URL` - Proxy Connection String
- `JWT_SECRET_KEY` - JWT Signing Key

**Abruf im Code**:
```python
from oci.secrets import SecretsClient
from oci.config import from_file

config = from_file()
secrets_client = SecretsClient(config)

def get_secret(secret_id):
    response = secrets_client.get_secret_bundle(secret_id)
    return base64.b64decode(response.data.secret_bundle_content.content).decode('utf-8')
```

## Cronjobs (OCI VM)

```bash
# /etc/crontab oder crontab -e

# Scraper: Alle 12 Stunden
0 */12 * * * cd /opt/foerder-finder-backend/scraper && /usr/bin/python3 -m scrapy crawl all_spiders >> /var/log/foerder-scraper.log 2>&1

# Indexer: 30 Min nach Scraper
30 */12 * * * cd /opt/foerder-finder-backend && /usr/bin/python3 build_index.py >> /var/log/foerder-indexer.log 2>&1
```

## Entwicklungs-Workflow

### Lokale Entwicklung
1. **Backend**: `uvicorn main:app --reload`
2. **Frontend**: `npm run dev`
3. **DB**: Verwende OCI Autonomous DB (auch für Dev - separates Schema)
4. **ChromaDB**: Lokal auf `/tmp/chroma_db_dev/`

### Testing
- **Backend**: pytest mit >80% Coverage
- **Frontend**: Vitest + React Testing Library
- **E2E**: Playwright (optional)

### Git Workflow
- **Branches**: `main` (prod), `develop` (integration)
- **Commits**: `feat: Add XY`, `fix: Fix AB`
- **Deployment**: `git push` → GitHub Actions → Cloudflare/OCI

## Monitoring & Logging

### Logs
- **Scraper**: `/var/log/foerder-scraper.log`
- **Indexer**: `/var/log/foerder-indexer.log`
- **API**: `/var/log/foerder-api.log` (gunicorn)
- **nginx**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

### Health Checks
- `GET /api/v1/health` - Backend Status
- ChromaDB Collection Count Check
- DB Connection Pool Status

## Besonderheiten & Best Practices

### RAG Pipeline
- **Chunking**: RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
- **Embedding Model**: MUSS identisch sein in Indexer + API
- **Metadaten**: Immer `funding_id` mit speichern für Filterung
- **Performance**: ChromaDB query mit `n_results=5` ist optimal

### DeepSeek API
- **Model**: `deepseek-chat`
- **Temperature**: 0.5 (Balance zwischen Kreativität und Konsistenz)
- **Max Tokens**: 2048
- **Timeout**: 60 Sekunden
- **Retry**: 3x mit exponential backoff

### Security
- **CORS**: Nur `app.foerder-finder.de` erlaubt
- **JWT**: HS256, Ablauf nach 24h
- **SQL Injection**: cx_Oracle Parameterized Queries
- **XSS**: React auto-escaping + DOMPurify für User Content

### Mandantenfähigkeit
- **Strikte Filterung**: Alle DB-Queries MÜSSEN auf `school_id` filtern
- **JWT Claim**: `school_id` im Token payload
- **Middleware**: `verify_school_access()` für alle Protected Routes

## Kosten-Optimierung

- **OCI**: Free Tier (VM.Standard.A1.Flex, ATP 20GB)
- **Cloudflare**: Free Tier (Pages, DNS, Basic WAF)
- **DeepSeek**: ~$0.14 per 1M tokens (extrem günstig vs. OpenAI)
- **Bright Data**: ~$500/Monat (notwendig für legales Scraping)

**Geschätzte monatliche Kosten**: ~$500-600

## Bekannte Herausforderungen

1. **Scraping Blockaden**: Lösung = Bright Data Rotating Proxies
2. **DeepSeek Rate Limits**: Lösung = Cloudflare Rate Limiting + Queue
3. **ChromaDB Persistence**: Lösung = Dedicated Block Volume
4. **Oracle Wallet Expiry**: Lösung = Auto-Renewal Script alle 90 Tage

## Kontakte & Links

- **DeepSeek Docs**: https://platform.deepseek.com/docs
- **ChromaDB Docs**: https://docs.trychroma.com/
- **OCI CLI**: `~/bin/oci`
- **Cloudflare Wrangler**: `npx wrangler --version` (4.43.0)

## Nächste Schritte (Roadmap)

- [ ] Phase 1: MVP (Scraper + DB + Basic API)
- [ ] Phase 2: RAG Integration (ChromaDB + DeepSeek)
- [ ] Phase 3: Frontend (React + Cloudflare)
- [ ] Phase 4: Production Deployment
- [ ] Phase 5: Monitoring + Analytics
- [ ] Phase 6: Advanced Features (PDF Export, Email Notifications)

---

**Last Updated**: 2025-10-24
**Version**: 1.0
