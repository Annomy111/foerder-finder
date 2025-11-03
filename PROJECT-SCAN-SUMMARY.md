# Förder-Finder Grundschule - Project Scan Summary

**Scan Date:** 2025-10-25  
**Comprehensive Report:** See `PROJECT-STRUCTURE-OVERVIEW.md` (18 KB)

---

## Executive Summary

**Förder-Finder Grundschule** is a **complete, production-ready full-stack SaaS application** for automated funding opportunity discovery and AI-assisted grant application for German primary schools.

- **Backend:** ✅ Complete FastAPI REST API with 4 router modules
- **Frontend:** ✅ Complete React application with 6 page components
- **Infrastructure:** ✅ Deployment scripts, systemd configs, database schema ready
- **Status:** Code 100% ready; awaiting only deployment secrets and database provisioning

---

## What Exists

### Source Code
- **Backend:** 23 Python files, 54 dependencies
- **Frontend:** 13 JSX/JS files, 342 total dependencies (19 direct + 323 transitive)
- **Database:** Complete Oracle schema (7 tables, triggers, views)
- **Deployment:** Shell scripts, systemd service files, nginx configs
- **Docs:** README, CLAUDE.md, QUICKSTART, TEST-REPORT, UI-REPORT

### Ready to Deploy
- Production frontend build (225 KB gzipped in `dist/`)
- Deployment automation scripts (`deploy-backend.sh`, `deploy-frontend.sh`)
- systemd service definitions for auto-scaling
- Environment variable templates

---

## Project Structure at a Glance

```
/Users/winzendwyers/Papa Projekt/
├── backend/                    # FastAPI API
├── frontend/                   # React application + dist/ (production build)
├── deployment/                 # Infrastructure automation
├── docs/                       # Documentation
├── PROJECT-STRUCTURE-OVERVIEW.md    # FULL DETAILS (15 sections)
└── PROJECT-SCAN-SUMMARY.md     # THIS FILE
```

---

## Key Addresses & URLs

| Component | Address | Purpose |
|-----------|---------|---------|
| Backend API (IP) | `130.61.76.199:8000` | Production API server |
| Backend Docs | `130.61.76.199:8000/docs` | Swagger OpenAPI docs |
| Frontend Dev | `localhost:3000` | Development URL |
| Frontend Prod | `foerder-finder.pages.dev` | Cloudflare Pages URL |
| Frontend Custom | `app.foerder-finder.de` | Custom domain (after DNS setup) |
| API Custom | `api.foerder-finder.de` | API custom domain (after DNS) |
| DeepSeek API | `api.deepseek.com/v1` | AI generation service |
| Database | OCI Cloud | Oracle Autonomous DB (not yet provisioned) |

---

## Technology Stack

### Backend (Python)
- **Framework:** FastAPI 0.104.1 + Uvicorn + Gunicorn
- **Database:** cx_Oracle 8.3.0 → Oracle Autonomous Database
- **Auth:** PyJWT + passlib[bcrypt]
- **Scraping:** Scrapy 2.11.0
- **RAG/AI:** ChromaDB + LangChain + sentence-transformers + torch

### Frontend (JavaScript)
- **Framework:** React 18.2.0 + Vite 5.0.8
- **State:** Zustand 4.4.7
- **Styling:** Tailwind CSS 3.3.6
- **HTTP:** Axios 1.6.2
- **Icons:** Lucide React

### Infrastructure
- **Backend Host:** Oracle Cloud VM (130.61.76.199)
- **Frontend Host:** Cloudflare Pages
- **Database:** Oracle ATP (Autonomous Database)
- **Vector Store:** ChromaDB (on OCI VM at `/opt/chroma_db`)
- **DNS/CDN:** Cloudflare

---

## API Endpoints

**Base URL:** `http://130.61.76.199:8000/api/v1`

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - New user
- `POST /auth/logout` - Logout
- `GET /auth/me` - Current user

### Funding Programs
- `GET /funding/` - List all
- `GET /funding/{id}` - Details
- `GET /funding/search` - Search/filter

### Applications
- `GET /applications/` - User's applications
- `POST /applications/` - Create
- `GET /applications/{id}` - Details
- `PUT /applications/{id}` - Update
- `DELETE /applications/{id}` - Delete

### AI Drafts
- `POST /drafts/generate` - AI draft generation
- `GET /drafts/{id}` - Draft details

### Health
- `GET /api/v1/health` - Status check

---

## Environment Variables

### Backend (`.env` from `.env.example`)

**Database:**
```
ORACLE_USER=ADMIN
ORACLE_PASSWORD=your_password
ORACLE_DSN=your_db_host:1522/service_name
ORACLE_WALLET_PATH=/path/to/wallet
```

**OCI Integration:**
```
OCI_CONFIG_PATH=~/.oci/config
OCI_COMPARTMENT_ID=ocid1.compartment...
SECRET_DEEPSEEK_API_KEY=ocid1.vaultsecret...
SECRET_BRIGHTDATA_PROXY=ocid1.vaultsecret...
SECRET_JWT_SECRET=ocid1.vaultsecret...
```

**API Configuration:**
```
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
CORS_ORIGINS=["https://app.foerder-finder.de"]
```

**RAG/AI:**
```
CHROMA_DB_PATH=/opt/chroma_db
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.5
RAG_CHUNK_SIZE=1000
RAG_TOP_K_RESULTS=5
```

### Frontend (`.env.production`)
```
VITE_API_URL=http://130.61.76.199:8000/api/v1
```

---

## Database Schema

**7 Oracle Tables:**

1. **SCHOOLS** - Tenant/organization info (multi-tenancy)
2. **USERS** - Users with roles (admin, teacher)
3. **FUNDING_OPPORTUNITIES** - Scraped funding programs (with `cleaned_text` for RAG)
4. **APPLICATIONS** - User applications to funding opportunities
5. **APPLICATION_DRAFTS** - AI-generated application drafts
6. **RAG_DOCUMENTS** - Indexed documents for retrieval
7. **AUDIT_LOG** - Security audit trail

**Demo Credentials:**
```
Email: admin@gs-musterberg.de
Password: admin123
```

---

## Deployment Status

### Ready Now
- ✅ All source code
- ✅ Frontend production build (`dist/`)
- ✅ Deployment scripts
- ✅ Database schema
- ✅ systemd service files
- ✅ Documentation

### Needed for Production
- ❌ DeepSeek API Key (free tier available)
- ❌ Bright Data proxy credentials
- ❌ OCI Vault secrets configured
- ❌ Oracle Autonomous Database provisioned
- ❌ Python 3.11+ installed on OCI VM
- ❌ Oracle Instant Client on OCI VM

---

## Automated Services (systemd)

Three scheduled services on OCI VM:

1. **foerder-api.service** (always running)
   - FastAPI backend with Gunicorn (4 workers)
   - Port: 8000
   - Auto-restart on failure

2. **foerder-scraper.timer + .service** (scheduled)
   - Runs every 12 hours
   - Scrapes funding opportunities via Scrapy
   - Logs to `/var/log/foerder-scraper.log`

3. **foerder-indexer.timer + .service** (scheduled)
   - Runs 30 min after scraper
   - Builds ChromaDB RAG index
   - Logs to `/var/log/foerder-indexer.log`

---

## Deployment Steps

### Phase 1: Acquire Secrets
```
1. Get DeepSeek API key from https://platform.deepseek.com/
2. Get Bright Data credentials from https://brightdata.com/
3. Generate JWT secret: openssl rand -base64 32
4. Create OCI Vault and store secrets
```

### Phase 2: Provision Database
```
1. Create Oracle Autonomous Database (ATP) in OCI Console
2. Download wallet
3. Execute schema.sql
4. Copy wallet to OCI VM
```

### Phase 3: Deploy Backend
```bash
cd /Users/winzendwyers/Papa\ Projekt/deployment/scripts
./deploy-backend.sh
```

### Phase 4: Deploy Frontend
```bash
cd /Users/winzendwyers/Papa\ Projekt/frontend
npm run build
npx wrangler pages deploy dist --project-name foerder-finder
```

### Phase 5: Configure DNS
```
In Cloudflare console:
- Add CNAME: app.foerder-finder.de → foerder-finder.pages.dev
- Add A Record: api.foerder-finder.de → 130.61.76.199
- Enable SSL/TLS (Full Strict)
```

### Phase 6: Smoke Tests
```
1. Visit https://app.foerder-finder.de
2. Login with admin@gs-musterberg.de / admin123
3. View funding list
4. Test AI draft generation
```

---

## Project Files

### Root Documentation
- **README.md** - Project overview & quick start
- **CLAUDE.md** - Architecture & deployment strategy (German)
- **DEPLOYMENT-STATUS.md** - Current readiness report
- **TEST-REPORT.md** - Test suite results
- **UI-UPDATE-REPORT.md** - Frontend component status
- **PROJECT-STRUCTURE-OVERVIEW.md** - COMPREHENSIVE (18 KB, 15 sections)
- **PROJECT-SCAN-SUMMARY.md** - THIS FILE

### Configuration Files
- `backend/.env.example` - Backend configuration template
- `frontend/.env.production` - Frontend production config
- `frontend/vite.config.js` - Vite build config
- `frontend/tailwind.config.js` - Tailwind CSS config
- `deployment/systemd/*.service` - systemd service definitions
- `deployment/scripts/*.sh` - Deployment automation

---

## File Count Summary

| Component | File Count | Type |
|-----------|-----------|------|
| Backend | 23 | Python (.py) |
| Frontend | 13 | JavaScript/JSX (.jsx, .js) |
| Config Files | 10+ | .json, .js, .sql, .sh, .service |
| Documentation | 7 | Markdown (.md) |
| Total Source | 53+ | Production-ready code |

---

## Quick Reference Commands

### Backend Development
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your config
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
# Starts on http://localhost:3000
```

### Frontend Production Build
```bash
cd frontend
npm run build
# Output in dist/
```

### Deploy Backend (when secrets ready)
```bash
cd deployment/scripts
./deploy-backend.sh
```

### Deploy Frontend
```bash
cd frontend
npm run build
npx wrangler pages deploy dist --project-name foerder-finder
```

### Check Backend Health
```bash
curl http://130.61.76.199:8000/api/v1/health
```

### Build RAG Index (on OCI VM)
```bash
cd /opt/foerder-finder-backend/rag_indexer
python build_index.py
```

### Run Scraper Manually (on OCI VM)
```bash
cd /opt/foerder-finder-backend/scraper
scrapy crawl all_spiders
```

---

## Key Insights

### Multi-Tenancy
- Database uses `school_id` foreign key across all tables
- JWT tokens include `school_id` for access control
- All API queries are filtered by authenticated school

### RAG Pipeline
- Text chunks stored in ChromaDB (on disk at `/opt/chroma_db`)
- Embeddings use sentence-transformers (embeddings locally computed)
- DeepSeek API used only for final draft generation (cost-efficient)

### Scraping Strategy
- Scrapy spiders extract funding programs 24/7 (12-hour intervals)
- Bright Data rotating proxy prevents IP blocking
- `cleaned_text` field fed into RAG system for semantic search

### Cost Optimization
- OCI Free Tier eligible (VM.Standard.A1.Flex)
- Cloudflare Pages free tier
- DeepSeek API much cheaper than OpenAI
- ChromaDB local (no cloud vector DB costs)

---

## For More Details

See **`PROJECT-STRUCTURE-OVERVIEW.md`** for comprehensive documentation:
- Complete directory tree with descriptions
- All 42 environment variables documented
- Full database schema
- Detailed deployment procedures
- Complete technology stack analysis
- Architecture diagrams and relationships

---

**Status:** Production-Ready Code (Awaiting Deployment Secrets)  
**Next Action:** Acquire API keys and provision database  
**Estimated Deployment Time:** 2-3 hours once secrets are ready
