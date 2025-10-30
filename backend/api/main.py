"""
FastAPI Backend - Förder-Finder Grundschule
Haupteinstiegspunkt der API
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.middleware import log_requests

load_dotenv()

# Auto-detect database mode and load appropriate routers
USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() == 'true'
USE_ADVANCED_RAG = os.getenv('USE_ADVANCED_RAG', 'false').lower() == 'true'

if USE_SQLITE:
    print('[STARTUP] Using SQLite routers (Development Mode)')
    from api.routers import auth_sqlite as auth
    from api.routers import funding_sqlite as funding
    from api.routers import applications_sqlite as applications
    from api.routers import drafts_sqlite as drafts
    from utils.database_sqlite import init_sqlite_schema, seed_demo_data
else:
    print('[STARTUP] Using Oracle routers (Production Mode)')
    from api.routers import auth, funding, applications, drafts

# Advanced RAG Router (v2)
if USE_ADVANCED_RAG:
    print('[STARTUP] Loading Advanced RAG Router (v2)...')
    from api.routers import drafts_advanced

# Search Router
from api.routers import search

# Admin Router (Protected)
from api.routers import admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan Events (Startup & Shutdown)"""
    # Startup
    print('[STARTUP] Förder-Finder API startet...')
    print(f'[STARTUP] CORS Origins: {os.getenv("CORS_ORIGINS")}')

    # Initialize SQLite if needed
    if USE_SQLITE:
        print('[STARTUP] Initializing SQLite database...')
        init_sqlite_schema()
        # seed_demo_data()  # Disabled - using real data from ChromaDB import
        print('[STARTUP] Using production data (ChromaDB import)')

    yield
    # Shutdown
    print('[SHUTDOWN] API wird heruntergefahren...')


# FastAPI App
app = FastAPI(
    title='Förder-Finder Grundschule API',
    description='Backend API für automatisierte Fördermittel-Antragstellung',
    version='1.0.0',
    lifespan=lifespan
)

# CORS Middleware
cors_origins = os.getenv('CORS_ORIGINS', '["http://localhost:3000"]')
if isinstance(cors_origins, str):
    import json
    cors_origins = json.loads(cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Custom Middleware
app.middleware('http')(log_requests)

# Routers
app.include_router(auth.router, prefix='/api/v1/auth', tags=['Authentication'])
app.include_router(funding.router, prefix='/api/v1/funding', tags=['Funding'])
app.include_router(applications.router, prefix='/api/v1/applications', tags=['Applications'])
app.include_router(drafts.router, prefix='/api/v1/drafts', tags=['AI Drafts'])
app.include_router(search.router, prefix='/api/v1/search', tags=['RAG Search'])
app.include_router(admin.router, prefix='/api/v1/admin', tags=['Admin (Protected)'])

# Advanced RAG Router (v2) - A/B Testing
if USE_ADVANCED_RAG:
    app.include_router(drafts_advanced.router, prefix='/api/v2/drafts', tags=['AI Drafts (Advanced RAG)'])


@app.get('/')
async def root():
    """Root Endpoint"""
    return {
        'message': 'Förder-Finder Grundschule API',
        'version': '1.0.0',
        'docs': '/docs'
    }


@app.get('/api/v1/health')
async def health_check():
    """Health Check Endpoint"""
    db_status = 'sqlite (dev)' if USE_SQLITE else 'oracle (prod)'

    # Check ChromaDB if Advanced RAG is enabled
    chromadb_status = 'not configured'
    if USE_ADVANCED_RAG:
        try:
            import chromadb
            chroma_path = os.getenv('CHROMA_DB_PATH', './chroma_db_dev')
            chroma_client = chromadb.PersistentClient(path=chroma_path)
            collection = chroma_client.get_collection(name='funding_docs')
            chromadb_status = f'healthy ({collection.count()} docs)'
        except Exception as e:
            chromadb_status = f'error: {str(e)}'

    return {
        'status': 'healthy',
        'database': db_status,
        'chromadb': chromadb_status,
        'advanced_rag': 'enabled' if USE_ADVANCED_RAG else 'disabled',
        'mode': 'development' if USE_SQLITE else 'production'
    }


if __name__ == '__main__':
    import uvicorn

    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))

    uvicorn.run(
        'main:app',
        host=host,
        port=port,
        reload=True,
        log_level='info'
    )
