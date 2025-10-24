# 🎯 Förder-Finder

**KI-gestützte Fördermittel-Antragstellung für Grundschulen**

[![Live Demo](https://img.shields.io/badge/Live-Demo-success)](https://f8653279.foerder-finder.pages.dev)
[![API](https://img.shields.io/badge/API-Online-success)](http://130.61.76.199:8000/docs)

---

## 🚀 Quick Start

**Demo-Login:**
- URL: https://f8653279.foerder-finder.pages.dev
- Email: `admin@gs-musterberg.de`
- Passwort: `test1234`

---

## ✨ Features

- ✅ Automatische Förderprogramm-Suche (24/7 Scraping)
- ✅ KI-gestützte Antragsgenierung (DeepSeek AI)
- ✅ JWT Authentication mit bcrypt
- ✅ RAG-System mit ChromaDB
- ✅ Mobile-responsive Design
- ✅ RESTful API mit FastAPI

---

## 🛠️ Tech Stack

**Backend:** FastAPI • SQLite • bcrypt • JWT • Scrapy
**Frontend:** React 18 • Vite • TailwindCSS • Zustand
**AI:** DeepSeek AI • ChromaDB • OpenRouter
**Infrastructure:** OCI (Backend) • Cloudflare Pages (Frontend)

---

## 🏗️ Installation

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with real credentials
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

---

## 🌐 Deployment

**Backend:** OCI VM (130.61.76.199:8000)
```bash
ssh opc@130.61.76.199
cd /opt/foerder-finder-backend
source venv/bin/activate
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 api.main:app --daemon
```

**Frontend:** Cloudflare Pages
```bash
cd frontend
npm run build
npx wrangler pages deploy dist --project-name foerder-finder
```

---

## 📖 API Dokumentation

**Swagger UI:** http://130.61.76.199:8000/docs

### Login
```bash
curl -X POST http://130.61.76.199:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gs-musterberg.de","password":"test1234"}'
```

Response:
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer",
  "user_id": "1",
  "school_id": "1",
  "role": "admin"
}
```

---

## 🧪 Testing

### API Test Suite
```bash
bash scripts/api_test.sh
```

### Backend Tests
```bash
cd backend
pytest tests/ --cov=api
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 📁 Project Structure

```
foerder-finder/
├── backend/
│   ├── api/
│   │   ├── main.py                # FastAPI App
│   │   ├── auth_utils.py          # bcrypt + JWT
│   │   └── routers/
│   │       ├── auth.py            # Login/Register
│   │       ├── funding.py         # Förderprogramme
│   │       └── applications.py    # Anträge
│   ├── scraper/
│   │   └── spiders/
│   │       ├── kfw_spider.py
│   │       └── foerderdatenbank_spider.py
│   ├── foerder_finder.db          # SQLite Database
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/api.js
│   │   └── store/authStore.js
│   └── package.json
└── README.md
```

---

## 🔑 Environment Variables

**Backend (.env):**
```bash
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
OPENROUTER_API_KEY=your-openrouter-key
```

**Frontend (.env.local):**
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

**Production Frontend (.env.production):**
```bash
VITE_API_URL=http://130.61.76.199:8000/api/v1
```

---

## 🐛 Troubleshooting

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Scraper not finding data:**
```bash
cd backend/scraper
scrapy crawl kfw_spider -L DEBUG
```

**JWT Token expired:**
```bash
# Login again to get new token
# Or increase JWT_EXPIRATION_HOURS in .env
```

---

## 🎯 Completed Features

- ✅ User Authentication (JWT + bcrypt)
- ✅ SQLite Database with demo data
- ✅ Auth Router (Login/Register)
- ✅ Funding Programs API
- ✅ Web Scraping System (24/7)
- ✅ Frontend Deployment (Cloudflare)
- ✅ Backend Deployment (OCI)
- ✅ API Testing Suite
- ✅ Mobile-Responsive UI

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Development

**Code Style:**
- Backend: PEP 8, Type Hints, Google Docstrings
- Frontend: ESLint + Prettier, Functional Components

**Git Workflow:**
- `main` - Production
- `develop` - Development
- `feature/*` - Features
- `fix/*` - Bug Fixes

---

## 📮 Contact

GitHub: [Repository Link]
Email: [your-email@example.com]

---

**Made with ❤️ for German Schools**
