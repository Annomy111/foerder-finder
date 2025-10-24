"""
FastAPI Backend - Förder-Finder Grundschule
Haupteinstiegspunkt der API
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routers import auth, funding, applications, drafts
from api.middleware import log_requests

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan Events (Startup & Shutdown)"""
    # Startup
    print('[STARTUP] Förder-Finder API startet...')
    print(f'[STARTUP] CORS Origins: {os.getenv("CORS_ORIGINS")}')
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
    # TODO: Prüfe DB-Verbindung, ChromaDB, etc.
    return {
        'status': 'healthy',
        'database': 'ok',
        'chromadb': 'ok'
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
