"""
AI Drafts Router
KI-generierte Antragsentwürfe mit RAG + DeepSeek
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import httpx
from datetime import datetime

import chromadb
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

from api.models import DraftGenerateRequest, DraftGenerateResponse, DraftFeedback
from api.auth_utils import get_current_user
from utils.database import get_db_cursor
from utils.oci_secrets import get_deepseek_api_key

load_dotenv()

router = APIRouter()

# ============================================================================
# RAG Setup (Global - wird beim API-Start initialisiert)
# ============================================================================

CHROMA_PATH = os.getenv('CHROMA_DB_PATH', '/opt/chroma_db')
CHROMA_COLLECTION_NAME = os.getenv('CHROMA_COLLECTION_NAME', 'funding_docs')
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', 'sentence-transformers/all-MiniLM-L6-v2')

# ChromaDB Client
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

# Embedding Model (MUSS identisch mit build_index.py sein!)
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# DeepSeek Config
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
DEEPSEEK_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', 2048))
DEEPSEEK_TEMPERATURE = float(os.getenv('DEEPSEEK_TEMPERATURE', 0.5))
RAG_TOP_K = int(os.getenv('RAG_TOP_K_RESULTS', 5))

# ============================================================================
# Prompt Template
# ============================================================================

DEEPSEEK_PROMPT_TEMPLATE = """
Du bist ein professioneller Experte für Fördermittelanträge im deutschen Grundschulsystem.
Deine Aufgabe ist es, einen überzeugenden, formellen und fehlerfreien Entwurf für einen Förderantrag zu schreiben.
Verwende das Vokabular und die Schlüsselkonzepte aus den bereitgestellten Richtlinien (KONTEXT).

---
KONTEXT (Relevante Auszüge aus der offiziellen Ausschreibung):
{context_chunks}
---
ANTRAGSTELLER (Stammdaten der Schule):
{school_profile}
---
PROJEKTIDEE (Input des Nutzers):
{user_query}
---

AUFGABE:
Generiere nun einen professionellen Antragsentwurf. Strukturiere ihn klar (z.B. 1. Ausgangslage, 2. Projektziele, 3. Maßnahmen, 4. Erfolgsindikatoren).
Verknüpfe die Projektziele direkt mit den Zielen aus dem KONTEXT.
Beginne direkt mit dem Entwurf. KEINE Meta-Kommentare wie "Hier ist der Entwurf...".
"""

# ============================================================================
# Helper Functions
# ============================================================================


async def get_school_profile(school_id: str) -> dict:
    """Holt Stammdaten der Schule für Prompt"""
    query = """
    SELECT
        school_name,
        school_number,
        address,
        schultyp,
        schuelerzahl,
        traeger
    FROM SCHOOLS
    WHERE RAWTOHEX(school_id) = :school_id
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, {'school_id': school_id})
        row = cursor.fetchone()

    if not row:
        return {}

    columns = ['school_name', 'school_number', 'address', 'schultyp', 'schuelerzahl', 'traeger']
    return dict(zip(columns, row))


def retrieve_context(funding_id: str, user_query: str, top_k: int = RAG_TOP_K) -> List[str]:
    """
    RAG Retrieval - Findet relevante Chunks aus ChromaDB

    Args:
        funding_id: ID der Förderausschreibung
        user_query: User-Query für semantische Suche
        top_k: Anzahl der Chunks

    Returns:
        Liste von relevanten Text-Chunks
    """
    # Embedde Query
    query_vector = embeddings.embed_query(user_query)

    # Suche in ChromaDB (gefiltert nach funding_id)
    results = chroma_collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        where={'funding_id': funding_id}
    )

    # Extrahiere Dokumente
    if results and results['documents']:
        return results['documents'][0]
    else:
        return []


async def call_deepseek_api(prompt: str) -> str:
    """
    Ruft DeepSeek API auf

    Args:
        prompt: Vollständiger Prompt

    Returns:
        Generierter Text

    Raises:
        HTTPException: Bei API-Fehlern
    """
    # Hole API Key aus OCI Vault
    api_key = get_deepseek_api_key()

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': DEEPSEEK_MODEL,
        'messages': [
            {
                'role': 'system',
                'content': 'Du bist ein professioneller Experte für Fördermittelanträge im deutschen Grundschulsystem.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': DEEPSEEK_MAX_TOKENS,
        'temperature': DEEPSEEK_TEMPERATURE
    }

    # API Call
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(DEEPSEEK_API_URL, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f'DeepSeek API error: {e.response.text}'
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f'DeepSeek API connection error: {str(e)}'
            )

    # Parse Response
    response_data = response.json()

    if 'choices' not in response_data or not response_data['choices']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Invalid DeepSeek API response'
        )

    generated_text = response_data['choices'][0]['message']['content']
    return generated_text


# ============================================================================
# Endpoints
# ============================================================================


@router.post('/generate', response_model=DraftGenerateResponse)
async def generate_draft(
    request: DraftGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generiert einen KI-Antragsentwurf mittels RAG + DeepSeek

    Args:
        request: funding_id, application_id, user_query

    Returns:
        Generierter Entwurf

    Raises:
        404: Application oder Funding nicht gefunden
        403: Zugriff verweigert
        502/503: DeepSeek API Fehler
    """
    # 1. Verify Application Access
    app_query = """
    SELECT RAWTOHEX(school_id) as school_id
    FROM APPLICATIONS
    WHERE RAWTOHEX(application_id) = :application_id
    """

    with get_db_cursor() as cursor:
        cursor.execute(app_query, {'application_id': request.application_id})
        app_row = cursor.fetchone()

    if not app_row:
        raise HTTPException(status_code=404, detail='Application not found')

    if app_row[0] != current_user['school_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )

    # 2. Verify Funding exists
    funding_query = """
    SELECT title FROM FUNDING_OPPORTUNITIES
    WHERE RAWTOHEX(funding_id) = :funding_id AND is_active = 1
    """

    with get_db_cursor() as cursor:
        cursor.execute(funding_query, {'funding_id': request.funding_id})
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail='Funding not found')

    # 3. Get School Profile
    school_profile = await get_school_profile(current_user['school_id'])
    school_profile_str = '\n'.join([f'{k}: {v}' for k, v in school_profile.items()])

    # 4. RAG Retrieval
    context_chunks = retrieve_context(request.funding_id, request.user_query)

    if not context_chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No context found for this funding (index may not be built yet)'
        )

    # 5. Build Prompt
    prompt = DEEPSEEK_PROMPT_TEMPLATE.format(
        context_chunks='\n---\n'.join(context_chunks),
        school_profile=school_profile_str,
        user_query=request.user_query
    )

    # 6. Call DeepSeek API
    generated_content = await call_deepseek_api(prompt)

    # 7. Save Draft to Database
    insert_query = """
    INSERT INTO APPLICATION_DRAFTS (
        application_id,
        generated_content,
        model_used,
        prompt_used,
        generation_metadata
    ) VALUES (
        HEXTORAW(:application_id),
        :generated_content,
        :model_used,
        :prompt_used,
        :metadata
    ) RETURNING RAWTOHEX(draft_id) INTO :draft_id
    """

    import json
    metadata = json.dumps({
        'model': DEEPSEEK_MODEL,
        'temperature': DEEPSEEK_TEMPERATURE,
        'max_tokens': DEEPSEEK_MAX_TOKENS,
        'chunks_used': len(context_chunks)
    })

    draft_id_var = cursor.var(str)

    with get_db_cursor() as cursor:
        cursor.execute(insert_query, {
            'application_id': request.application_id,
            'generated_content': generated_content,
            'model_used': DEEPSEEK_MODEL,
            'prompt_used': prompt,
            'metadata': metadata,
            'draft_id': draft_id_var
        })

    draft_id = draft_id_var.getvalue()[0]

    return DraftGenerateResponse(
        draft_id=draft_id,
        application_id=request.application_id,
        generated_content=generated_content,
        model_used=DEEPSEEK_MODEL,
        created_at=datetime.now()
    )


@router.get('/application/{application_id}', response_model=List[DraftGenerateResponse])
async def get_drafts_for_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Holt alle Entwürfe für einen Antrag

    Args:
        application_id: ID des Antrags

    Returns:
        Liste von Entwürfen
    """
    # Verify Access (via applications router)
    from api.routers.applications import get_application
    await get_application(application_id, current_user)

    # Get Drafts
    query = """
    SELECT
        RAWTOHEX(draft_id) as draft_id,
        RAWTOHEX(application_id) as application_id,
        generated_content,
        model_used,
        created_at
    FROM APPLICATION_DRAFTS
    WHERE RAWTOHEX(application_id) = :application_id
    ORDER BY created_at DESC
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, {'application_id': application_id})

        columns = [col[0].lower() for col in cursor.description]
        results = []

        for row in cursor:
            data = dict(zip(columns, row))
            results.append(DraftGenerateResponse(**data))

    return results


@router.post('/feedback')
async def submit_feedback(
    feedback: DraftFeedback,
    current_user: dict = Depends(get_current_user)
):
    """
    Nutzer-Feedback zu einem generierten Entwurf

    Args:
        feedback: draft_id + feedback (helpful/not_helpful)

    Returns:
        Success message
    """
    update_query = """
    UPDATE APPLICATION_DRAFTS
    SET user_feedback = :feedback
    WHERE RAWTOHEX(draft_id) = :draft_id
    """

    with get_db_cursor() as cursor:
        cursor.execute(update_query, {
            'draft_id': feedback.draft_id,
            'feedback': feedback.feedback
        })

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail='Draft not found')

    return {'message': 'Feedback submitted successfully'}
