# Förder-Finder Grundschule - Comprehensive Project Structure Overview

**Generated:** 2025-10-25  
**Project Type:** Full-Stack SaaS Application  
**Status:** Code-Complete, Ready for Deployment

---

## 1. PROJECT CLASSIFICATION

### Type
- **Full-Stack Application** - Both frontend and backend included
- **SaaS Platform** - Multi-tenant capable (school-based tenancy)
- **AI-Powered** - Integrates DeepSeek API for draft generation

### Current State
- ✅ **Backend:** Production-ready code
- ✅ **Frontend:** Production-ready code  
- ✅ **Infrastructure:** Scripts and configs prepared
- ⚠️ **Deployment:** Code ready, awaiting secrets/credentials
- ⚠️ **Database:** Schema defined, awaiting Oracle setup

---

## 2. DIRECTORY STRUCTURE

```
/Users/winzendwyers/Papa Projekt/
├── .claude/                              # Claude Code configuration
│   └── settings.local.json               # MCP servers & permissions
├── .git/                                 # Git repository
├── .gitignore                            # Git ignore rules
│
├── README.md                             # Project overview & quick links
├── CLAUDE.md                             # Project-specific memory (German)
├── DEPLOYMENT-STATUS.md                  # Current deployment readiness report
├── TEST-REPORT.md                        # Test suite results
├── UI-UPDATE-REPORT.md                   # Frontend component status
│
├── backend/                              # FastAPI Backend (Python)
│   ├── .env.example                      # Environment variables template
│   ├── requirements.txt                  # Python dependencies (54 packages)
│   ├── api/                              # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app entrypoint
│   │   ├── models.py                     # Pydantic request/response models
│   │   ├── auth_utils.py                 # JWT + bcrypt utilities
│   │   ├── middleware.py                 # HTTP middleware (logging)
│   │   └── routers/                      # API route handlers
│   │       ├── auth.py                   # Login/Register endpoints
│   │       ├── funding.py                # Funding opportunities API
│   │       ├── applications.py           # Application management API
│   │       └── drafts.py                 # AI draft generation API
│   ├── database/                         # Database layer
│   │   └── schema.sql                    # Oracle schema definition
│   ├── scraper/                          # Scrapy web scraping engine
│   │   └── foerder_scraper/
│   │       ├── settings.py               # Scrapy configuration
│   │       ├── items.py                  # Data structures
│   │       ├── pipelines.py              # Data processing pipelines
│   │       ├── middlewares.py            # Proxy & user-agent rotation
│   │       └── spiders/
│   │           └── bmbf_spider.py        # Example spider (BMBF funding)
│   ├── rag_indexer/                      # RAG indexing service
│   │   ├── __init__.py
│   │   └── build_index.py                # ChromaDB index builder
│   ├── utils/                            # Utility modules
│   │   ├── database.py                   # Oracle connection pool
│   │   └── oci_secrets.py                # OCI Vault secret retrieval
│   └── config/                           # Configuration module
│       └── __init__.py
│
├── frontend/                             # React Frontend (JavaScript/JSX)
│   ├── .env.production                   # Production environment config
│   ├── .eslintrc.cjs                     # ESLint configuration
│   ├── package.json                      # Node.js dependencies (19 packages)
│   ├── package-lock.json                 # Dependency lock file
│   ├── vite.config.js                    # Vite build configuration
│   ├── tailwind.config.js                # Tailwind CSS configuration
│   ├── postcss.config.js                 # PostCSS configuration
│   ├── index.html                        # HTML entry point
│   ├── .wrangler/                        # Cloudflare Wrangler cache
│   ├── dist/                             # Production build output
│   ├── public/                           # Static assets
│   ├── src/                              # Source code
│   │   ├── main.jsx                      # React entrypoint
│   │   ├── App.jsx                       # Root component
│   │   ├── components/                   # Reusable components
│   │   │   ├── Layout.jsx                # App shell & navigation
│   │   │   ├── LoadingSpinner.jsx        # Loading indicator
│   │   │   └── EmptyState.jsx            # Empty state display
│   │   ├── pages/                        # Page components
│   │   │   ├── LoginPage.jsx             # Authentication page
│   │   │   ├── DashboardPage.jsx         # Main dashboard
│   │   │   ├── FundingListPage.jsx       # Funding programs list
│   │   │   ├── FundingDetailPage.jsx     # Funding details view
│   │   │   ├── ApplicationsPage.jsx      # Application management
│   │   │   └── ApplicationDetailPage.jsx # Application details
│   │   ├── services/                     # API client layer
│   │   │   └── api.js                    # Axios HTTP client
│   │   └── store/                        # State management
│   │       └── authStore.js              # Zustand auth store
│   └── node_modules/                     # Dependencies (323 packages)
│
├── deployment/                           # Infrastructure & deployment
│   ├── scripts/                          # Deployment automation
│   │   ├── deploy-backend.sh             # OCI VM deployment script
│   │   └── deploy-frontend.sh            # Cloudflare Pages deployment
│   ├── systemd/                          # systemd service definitions
│   │   ├── foerder-api.service           # FastAPI service
│   │   ├── foerder-scraper.service       # Scrapy scraper service
│   │   ├── foerder-scraper.timer         # 12-hourly scraper schedule
│   │   ├── foerder-indexer.service       # RAG indexer service
│   │   └── foerder-indexer.timer         # Post-scrape indexing schedule
│   └── nginx/                            # nginx configuration (if used)
│
└── docs/                                 # Documentation
    └── QUICKSTART.md                     # 30-minute setup guide
```

---

## 3. CONFIGURATION FILES & ENDPOINTS

### Backend Configuration (`.env.example`)

**Database:**
```
ORACLE_USER=ADMIN
ORACLE_PASSWORD=your_password_here
ORACLE_DSN=your_db_host:1522/your_service_name
ORACLE_WALLET_PATH=/path/to/wallet
```

**OCI Integration:**
```
OCI_CONFIG_PATH=~/.oci/config
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxx
SECRET_DEEPSEEK_API_KEY=ocid1.vaultsecret.oc1..xxx
SECRET_BRIGHTDATA_PROXY=ocid1.vaultsecret.oc1..xxx
SECRET_JWT_SECRET=ocid1.vaultsecret.oc1..xxx
```

**AI & RAG:**
```
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=2048
DEEPSEEK_TEMPERATURE=0.5
CHROMA_DB_PATH=/opt/chroma_db
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

**RAG Tuning:**
```
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_TOP_K_RESULTS=5
```

**API:**
```
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
CORS_ORIGINS=["https://app.foerder-finder.de"]
```

**Scraping:**
```
SCRAPER_USER_AGENT=Mozilla/5.0 (compatible; FoerderFinderBot/1.0)
SCRAPER_DELAY=2.0
SCRAPER_CONCURRENT_REQUESTS=8
```

**JWT:**
```
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Frontend Configuration (`.env.production`)

```
VITE_API_URL=http://130.61.76.199:8000/api/v1
```

---

## 4. API ENDPOINTS

### Base URL (Production)
```
http://130.61.76.199:8000
```

### API Documentation
```
Swagger UI: http://130.61.76.199:8000/docs
```

### Authentication Endpoints (`/api/v1/auth`)
- `POST /login` - User login with email/password
- `POST /register` - New user registration
- `POST /logout` - User logout
- `GET /me` - Current user profile

### Funding Endpoints (`/api/v1/funding`)
- `GET /` - List all funding opportunities
- `GET /{funding_id}` - Get funding details
- `GET /search` - Search/filter funding (by region, area, provider)

### Application Endpoints (`/api/v1/applications`)
- `GET /` - List user's applications
- `POST /` - Create new application
- `GET /{application_id}` - Get application details
- `PUT /{application_id}` - Update application
- `DELETE /{application_id}` - Delete application

### AI Draft Endpoints (`/api/v1/drafts`)
- `POST /generate` - Generate AI draft for application
- `GET /{draft_id}` - Get draft details

### Health Check
- `GET /api/v1/health` - API health status

---

## 5. BACKEND TECHNICAL STACK

### Framework & Server
- **FastAPI** 0.104.1 - Modern Python async web framework
- **Uvicorn** 0.24.0 - ASGI server
- **Gunicorn** 21.2.0 - Process manager (production)

### Database
- **cx_Oracle** 8.3.0 - Oracle client
- **Target:** Oracle Autonomous Database (ATP) on OCI
- **Connection:** Wallet-based authentication

### Authentication & Security
- **PyJWT** 2.8.0 - JWT token handling
- **passlib[bcrypt]** 1.7.4 - Password hashing
- **python-jose** 3.3.0 - JOSE/JWT crypto

### Scraping Engine
- **Scrapy** 2.11.0 - Web scraping framework
- **Bright Data Proxy** - Rotating proxy integration
- **BeautifulSoup4** 4.12.2 - HTML parsing
- **lxml** 4.9.3 - XML/HTML processing

### RAG & AI
- **ChromaDB** 0.4.18 - Vector database (local on OCI VM)
- **LangChain** 0.1.0 - LLM orchestration
- **sentence-transformers** 2.2.2 - Embeddings (all-MiniLM-L6-v2)
- **torch** 2.1.1 - ML framework
- **transformers** 4.35.2 - HuggingFace models

### OCI Integration
- **oci** 2.115.0 - Oracle Cloud SDK (for Vault secrets)

### Utilities
- **pydantic** 2.5.0 - Data validation
- **python-dotenv** 1.0.0 - Environment variable loading
- **structlog** 23.2.0 - Structured logging

### Testing
- **pytest** 7.4.3 - Testing framework
- **pytest-cov** 4.1.0 - Coverage reporting
- **httpx-mock** 0.11.0 - HTTP mocking

---

## 6. FRONTEND TECHNICAL STACK

### Framework & Build
- **React** 18.2.0 - UI library
- **Vite** 5.0.8 - Fast build tool
- **React Router DOM** 6.20.0 - Client-side routing

### State Management
- **Zustand** 4.4.7 - Lightweight state management

### Styling
- **Tailwind CSS** 3.3.6 - Utility-first CSS
- **PostCSS** 8.4.32 - CSS post-processing
- **Autoprefixer** 10.4.16 - CSS vendor prefixes

### HTTP & Data
- **Axios** 1.6.2 - HTTP client

### UI Components
- **Lucide React** 0.294.0 - Icon library
- **date-fns** 2.30.0 - Date utilities

### Development Tools
- **ESLint** 8.55.0 - Code linting
- **eslint-plugin-react** 7.33.2 - React linting
- **eslint-plugin-react-hooks** 4.6.0 - Hooks linting
- **eslint-plugin-react-refresh** 0.4.5 - Vite refresh support

### Type Safety
- TypeScript types for React (@types/react, @types/react-dom)

---

## 7. DEPLOYMENT INFRASTRUCTURE

### Backend Hosting
- **VM Instance:** Oracle Cloud (OCI)
- **IP Address:** 130.61.76.199
- **Instance Type:** VM.Standard.A1.Flex (ARM architecture, Free Tier)
- **SSH User:** opc
- **SSH Key:** ~/.ssh/be-api-direct
- **Deployment Directory:** /opt/foerder-finder-backend

### Frontend Hosting
- **Platform:** Cloudflare Pages
- **Project Name:** foerder-finder
- **Build Output:** `frontend/dist/`
- **Auto-deployment:** Via Wrangler CLI

### Database
- **Type:** Oracle Autonomous Transaction Processing (ATP)
- **Hosting:** Oracle Cloud Infrastructure (OCI)
- **Connection:** Wallet-based (no IP whitelist needed)
- **Tables:** 7 main tables + views for reporting

### DNS & CDN
- **Provider:** Cloudflare
- **Planned Domains:**
  - `app.foerder-finder.de` → Cloudflare Pages
  - `api.foerder-finder.de` → OCI VM (130.61.76.199)
- **SSL:** Let's Encrypt (via certbot on VM)

### ChromaDB Storage
- **Location:** /opt/chroma_db on OCI VM
- **Storage Type:** Oracle Block Volume (persistent)
- **Purpose:** Vector store for RAG system

---

## 8. SCHEDULED SERVICES (systemd)

### 1. foerder-api.service
- **Purpose:** FastAPI backend service
- **Process Manager:** Gunicorn (4 workers, UvicornWorker)
- **Port:** 8000
- **Restart Policy:** Always (10s retry)

### 2. foerder-scraper.timer + .service
- **Purpose:** Web scraping of funding opportunities
- **Schedule:** Every 12 hours (cron)
- **Execution:** Scrapy crawl all_spiders
- **Logging:** `/var/log/foerder-scraper.log`

### 3. foerder-indexer.timer + .service
- **Purpose:** RAG index building from scraped data
- **Schedule:** 30 minutes after scraper completes
- **Execution:** build_index.py (chunking + embedding)
- **Logging:** `/var/log/foerder-indexer.log`

---

## 9. DATABASE SCHEMA OVERVIEW

### Tables (Oracle Autonomous DB)

1. **SCHOOLS** - Tenant information
   - school_id (PK)
   - name, address, phone_number
   - region, created_at, updated_at

2. **USERS** - Application users
   - user_id (PK)
   - school_id (FK) - Multi-tenancy
   - email (unique), password_hash
   - role (admin, teacher), is_active
   - created_at, updated_at

3. **FUNDING_OPPORTUNITIES** - Scraped funding programs
   - funding_id (PK)
   - title, source_url
   - cleaned_text (for RAG indexing)
   - provider, region, funding_area
   - deadline, min/max funding amount
   - tags, metadata
   - scraped_at, updated_at

4. **APPLICATIONS** - User applications to funding
   - application_id (PK)
   - user_id, school_id (FK) - Multi-tenancy
   - funding_id (FK)
   - status (draft, submitted, accepted, rejected)
   - content, notes
   - created_at, updated_at

5. **APPLICATION_DRAFTS** - AI-generated application drafts
   - draft_id (PK)
   - application_id (FK)
   - content (AI-generated text)
   - model_used, temperature, tokens_used
   - created_at

6. **RAG_DOCUMENTS** - For tracking indexed documents
   - doc_id (PK)
   - funding_id (FK)
   - chunk_id, chunk_text
   - embedding_id (references ChromaDB)

7. **AUDIT_LOG** - Security audit trail
   - log_id (PK)
   - user_id (FK)
   - action, resource, timestamp

---

## 10. CURRENT DEPLOYMENT STATUS

### ✅ What's Ready
- Full source code (backend + frontend)
- Production build artifacts (dist/)
- Deployment scripts (shell-based automation)
- systemd service configurations
- Database schema (SQL)
- API documentation (Swagger/OpenAPI)
- Environment variable templates

### ⚠️ What's Needed for Deployment

1. **OCI Configuration:**
   - OCI Vault secrets configured
   - Secret IDs in .env
   - Autonomous Database provisioned

2. **API Keys:**
   - DeepSeek API key (https://platform.deepseek.com/)
   - Bright Data rotating proxy credentials

3. **Database:**
   - Oracle Autonomous Database created
   - Wallet downloaded to VM
   - Schema executed

4. **VM Preparation:**
   - Python 3.11+ installed
   - Oracle Instant Client installed
   - ChromaDB path created (/opt/chroma_db)
   - systemd services installed

### 📋 Deployment Steps (High Level)

1. **Phase 1:** Create Oracle Autonomous Database + download wallet
2. **Phase 2:** Deploy backend to OCI VM (via deploy-backend.sh)
3. **Phase 3:** Run initial scraping & RAG indexing
4. **Phase 4:** Deploy frontend to Cloudflare Pages
5. **Phase 5:** Configure DNS & SSL (Cloudflare)
6. **Phase 6:** Health checks & smoke tests

---

## 11. LIVE DEMO CREDENTIALS

The project includes demo test data seeded in the database schema:

```
Email: admin@gs-musterberg.de
Password: admin123
School: GS Musterberg (demo school)
Role: admin
```

---

## 12. KEY ADDRESSES & ENDPOINTS

| Component | Address | Type | Status |
|-----------|---------|------|--------|
| Backend API | http://130.61.76.199:8000 | REST | Ready |
| API Docs | http://130.61.76.199:8000/docs | Swagger | Ready |
| Frontend (dev) | http://localhost:3000 | Web | Ready |
| Frontend (prod) | https://foerder-finder.pages.dev | Web | Ready to deploy |
| DeepSeek API | https://api.deepseek.com/v1 | External | Requires key |
| ChromaDB | /opt/chroma_db | Local | On VM |
| Oracle DB | OCI Cloud | Cloud | Requires provisioning |
| Cloudflare API | api.cloudflare.com | External | Authenticated |

---

## 13. PROJECT METRICS

### Code Statistics
- **Backend Python files:** 23
- **Frontend JSX/JS files:** 13
- **Backend dependencies:** 54 packages
- **Frontend dependencies:** 19 packages + 323 transitive

### File Sizes
- Frontend production build: 225 KB (gzipped)
- Backend venv (estimated): ~500 MB

### Database
- 7 main tables
- 2 indexed views
- Estimated startup data: < 1 MB

---

## 14. DOCUMENTATION REFERENCES

| Document | Purpose | Location |
|----------|---------|----------|
| README.md | Project overview, quick start | Project root |
| CLAUDE.md | Project-specific memory & architecture | Project root |
| DEPLOYMENT-STATUS.md | Current deployment readiness | Project root |
| QUICKSTART.md | 30-min local setup guide | docs/ |
| TEST-REPORT.md | Test suite results | Project root |
| .env.example | Backend configuration template | backend/ |

---

## 15. NEXT IMMEDIATE STEPS

### For Local Development
1. Copy .env.example → .env in backend/
2. Configure DB connection (Oracle or PostgreSQL)
3. Run `pip install -r requirements.txt`
4. Run `npm install` in frontend/
5. Start backend: `uvicorn api.main:app --reload`
6. Start frontend: `npm run dev`

### For Production Deployment
1. Acquire DeepSeek API key
2. Create OCI Vault secrets
3. Provision Oracle Autonomous Database
4. Execute database schema
5. Run `deployment/scripts/deploy-backend.sh`
6. Run `deployment/scripts/deploy-frontend.sh`
7. Configure DNS records in Cloudflare
8. Run health checks

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-25  
**Project Status:** MVP Phase - Code Ready, Awaiting Deployment Secrets
