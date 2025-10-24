# Quick Start Guide - Förder-Finder Grundschule

**Ziel:** In 30 Minuten lokal lauffähiges System

---

## Schritt 1: Voraussetzungen prüfen

Stelle sicher, dass du Folgendes installiert hast:

- **Python 3.11+**
- **Node.js 18+** & npm
- **Oracle Instant Client** (für cx_Oracle)
- **Git**

Optional (für lokales Testing):
- **Docker** (falls Oracle DB lokal laufen soll)

---

## Schritt 2: Repository klonen

```bash
cd ~/projects
git clone <repository-url> foerder-finder
cd foerder-finder
```

---

## Schritt 3: Datenbank vorbereiten

### Option A: Oracle Autonomous Database (Production)

1. Logge dich in OCI Console ein
2. Erstelle Autonomous Database (ATP)
3. Lade Wallet herunter
4. Führe Schema aus:
   ```bash
   sqlplus admin@your_db @backend/database/schema.sql
   ```

### Option B: PostgreSQL lokal (Development-Alternative)

**WICHTIG:** Das Projekt ist für Oracle optimiert. Für PostgreSQL müssen Queries angepasst werden!

```bash
# Starte PostgreSQL via Docker
docker run -d \
  --name foerder-db \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15

# Schema anpassen (RAW → UUID, etc.) und ausführen
```

---

## Schritt 4: Backend-Setup

```bash
cd backend

# Virtual Environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Dependencies installieren
pip install -r requirements.txt

# .env konfigurieren
cp .env.example .env
nano .env
```

**Minimale .env für lokales Testing:**

```bash
# Database (mit lokalem PostgreSQL oder Oracle Cloud)
ORACLE_USER=ADMIN
ORACLE_PASSWORD=your_password
ORACLE_DSN=localhost:1521/XEPDB1
ORACLE_WALLET_PATH=  # Leer lassen für lokale DB ohne Wallet

# Secrets (für Testing: Hardcode statt OCI Vault)
# WICHTIG: Nur für Development! In Production OCI Vault verwenden
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
DEEPSEEK_API_KEY=sk-xxx  # Dein DeepSeek API Key
BRIGHTDATA_PROXY_URL=  # Leer lassen für Testing ohne Proxy

# ChromaDB
CHROMA_DB_PATH=./chroma_db_dev
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]
```

**Für Development ohne OCI Vault:**

Öffne `backend/utils/oci_secrets.py` und füge eine Fallback-Funktion hinzu:

```python
def get_deepseek_api_key():
    """Development Fallback"""
    return os.getenv('DEEPSEEK_API_KEY', '')

def get_jwt_secret():
    """Development Fallback"""
    return os.getenv('JWT_SECRET_KEY', 'dev-secret-key')

def get_brightdata_proxy():
    """Development Fallback"""
    return os.getenv('BRIGHTDATA_PROXY_URL', '')
```

---

## Schritt 5: Erste Daten scrapen (Optional)

```bash
cd backend/scraper

# Teste einen Spider manuell
scrapy crawl bmbf -o output.json

# ODER: Füge Test-Daten manuell in DB ein
```

**Quick SQL Test-Daten:**

```sql
INSERT INTO FUNDING_OPPORTUNITIES (
    title, source_url, cleaned_text, provider, region, funding_area
) VALUES (
    'Digitalpakt Schule 2.0',
    'https://example.com/digitalpakt',
    'Der Digitalpakt unterstützt Schulen bei der Anschaffung digitaler Endgeräte wie Tablets und Laptops. Ziel ist die Verbesserung der digitalen Bildung.',
    'BMBF',
    'Bundesweit',
    'Digitalisierung'
);
```

---

## Schritt 6: RAG Index bauen

```bash
cd backend/rag_indexer
python build_index.py
```

**Output:**
```
[INFO] ChromaDB Pfad: ./chroma_db_dev
[INFO] Fetched 1 funding documents
[INFO] Indexing 5 chunks...
[SUCCESS] Index rebuild complete!
```

---

## Schritt 7: Backend starten

```bash
cd backend/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Teste die API:**

```bash
# Health Check
curl http://localhost:8000/api/v1/health

# Login (mit Demo-User aus schema.sql)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@gs-musterberg.de", "password": "admin123"}'
```

---

## Schritt 8: Frontend starten

```bash
cd frontend
npm install

# Dev Server starten
npm run dev
```

**Frontend läuft auf:** http://localhost:3000

---

## Schritt 9: Erste Schritte in der App

1. **Login:**
   - Email: `admin@gs-musterberg.de`
   - Passwort: `admin123`

2. **Fördermittel anzeigen:**
   - Navigiere zu "Fördermittel"
   - Siehst du die Test-Ausschreibung?

3. **KI-Entwurf generieren:**
   - Erstelle einen neuen Antrag
   - Klicke auf "KI-Entwurf generieren"
   - Gebe Projektidee ein: *"Wir möchten 30 iPads für Klasse 3/4 anschaffen"*

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'cx_Oracle'"

**Oracle Instant Client fehlt:**

```bash
# macOS (Homebrew)
brew tap InstantClientTap/instantclient
brew install instantclient-basiclite

# Linux
# Download von Oracle: https://www.oracle.com/database/technologies/instant-client/downloads.html
```

### "Connection refused" beim API-Call

**CORS-Problem:**

Prüfe `backend/.env`:
```bash
CORS_ORIGINS=["http://localhost:3000"]
```

### ChromaDB "Collection not found"

**Index wurde nicht gebaut:**

```bash
cd backend/rag_indexer
python build_index.py
```

### DeepSeek API schlägt fehl

**API Key prüfen:**

```bash
# Teste API Key manuell
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer sk-xxx"
```

---

## Nächste Schritte

Nach erfolgreichem lokalem Setup:

1. **Spider erweitern:** Passe `backend/scraper/foerder_scraper/spiders/bmbf_spider.py` an echte Quellen an
2. **UI verbessern:** Implementiere fehlende Frontend-Features (Filter, PDF-Export)
3. **Deployment vorbereiten:** Siehe `README.md` für Production-Deployment

---

## Hilfreiche Befehle

```bash
# Backend Tests
cd backend && pytest

# Frontend Linting
cd frontend && npm run lint

# Datenbank zurücksetzen
# WARNUNG: Löscht alle Daten!
sqlplus admin@your_db @backend/database/schema.sql

# ChromaDB-Index löschen
rm -rf backend/chroma_db_dev
```

---

**Fertig!** 🎉

Du hast jetzt ein lokal lauffähiges Förder-Finder-System.

Bei Fragen siehe `README.md` oder `CLAUDE.md`.
