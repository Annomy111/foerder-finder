"""
AI Drafts Router - Advanced RAG Version
KI-generierte Antragsentwürfe mit Advanced RAG Pipeline

Improvements over v1:
- Hybrid search (Dense + BM25)
- Query expansion (RAG Fusion)
- Reranking (Cross-encoder)
- Contextual compression
- Enhanced prompting (Few-shot + CoT)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import httpx
from datetime import datetime
import json

from api.models import DraftGenerateRequest, DraftGenerateResponse, DraftFeedback
from api.auth_utils import get_current_user
from utils.db_adapter import get_db_cursor
from utils.oci_secrets import get_deepseek_api_key

# Advanced RAG imports
from rag_indexer.advanced_rag_pipeline import AdvancedRAGPipeline

from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# ============================================================================
# Global RAG Pipeline (Initialized once)
# ============================================================================

# Initialize Advanced RAG Pipeline
print('[INFO] Initializing Advanced RAG Pipeline for API...')
rag_pipeline = AdvancedRAGPipeline(
    enable_query_expansion=True,
    enable_reranking=True,
    enable_compression=True,
    enable_crag=True,
    verbose=os.getenv('RAG_VERBOSE', 'false').lower() == 'true'
)
print('[SUCCESS] Advanced RAG Pipeline ready')

# DeepSeek Config
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
DEEPSEEK_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', 3000))  # Increased for better drafts
DEEPSEEK_TEMPERATURE = float(os.getenv('DEEPSEEK_TEMPERATURE', 0.5))

# ============================================================================
# Enhanced Prompt Template (Few-Shot + Chain-of-Thought)
# ============================================================================

ENHANCED_PROMPT_TEMPLATE = """
Du bist ein professioneller Experte für Fördermittelanträge im deutschen Grundschulsystem mit 10+ Jahren Erfahrung bei erfolgreichen Bewerbungen.

---
KONTEXT (Relevante Auszüge aus der offiziellen Ausschreibung):
{context_chunks}

---
ANTRAGSTELLER (Stammdaten der Schule):
{school_profile}

---
PROJEKTBESCHREIBUNG (Nutzereingabe):
{user_query}

---
BEISPIEL-ANTRAG (Few-Shot Learning):

**Beispiel 1: Tablet-Förderung**

Anfrage: "Wir brauchen 20 Tablets für unsere 3. Klasse für digitalen Unterricht"

Professioneller Entwurf:

**1. Ausgangslage**
Die Grundschule am Musterberg verfügt aktuell über keine mobilen Endgeräte für den Unterricht der Klassenstufe 3. Dies erschwert die Umsetzung der KMK-Strategie "Bildung in der digitalen Welt" und benachteiligt unsere Schülerinnen und Schüler beim Erwerb digitaler Kompetenzen.

**2. Projektziele**
Ziel ist die Anschaffung von 20 Tablets (iPad 10. Generation oder vergleichbar) zur Förderung digitaler Kompetenzen in den Bereichen Mathematik, Deutsch und Sachunterricht. Die Geräte sollen im Klassensatz eingesetzt werden, um allen 22 Schülerinnen und Schülern der Klasse 3a gleichberechtigten Zugang zu ermöglichen.

**3. Geplante Maßnahmen**
- Beschaffung von 20 Tablets inkl. Schutzhüllen und Ladewagen
- Lehrerfortbildung zur Integration digitaler Medien (2 Tage)
- Entwicklung eines Medienkonzepts für Klasse 3
- Pilotierung digitaler Lernmaterialien in Mathematik (Anton-App, Einmaleins-Trainer)

**4. Erwartete Ergebnisse**
- Alle Schüler*innen der Klasse 3a erwerben grundlegende digitale Kompetenzen
- Individuelle Förderung durch adaptive Lernprogramme
- Dokumentation der Projekterfahrungen für andere Klassen

**5. Budget**
- 20 Tablets à 400€: 8.000€
- Zubehör (Hüllen, Ladewagen): 1.500€
- Fortbildung: 500€
- **Gesamtsumme: 10.000€**

---
SCHRITT-FÜR-SCHRITT ANLEITUNG (Chain-of-Thought):

1. **Analysiere die Ausschreibung**: Welche Ziele und Keywords werden genannt? (z.B. "Digitalisierung", "Bildungsgerechtigkeit", "Teilhabe")

2. **Verknüpfe Projektziele mit Ausschreibungszielen**: Zeige direkte Bezüge auf (z.B. "Unser Projekt trägt zur digitalen Teilhabe bei, indem...")

3. **Strukturiere klar und professionell**:
   - Ausgangslage: Aktueller Zustand, Problemstellung
   - Projektziele: SMART-Ziele (Spezifisch, Messbar, Erreichbar, Relevant, Terminiert)
   - Maßnahmen: Konkrete Schritte mit Zeitplan
   - Erwartete Ergebnisse: Messbare Outcomes
   - Budget: Detaillierte Kostenkalkulation

4. **Verwende konkrete Zahlen**: Anzahl Schüler, Beträge, Zeiträume, Mengenangaben

5. **Nutze Fachvokabular aus der Ausschreibung**: Übernimm wichtige Begriffe wie "Bildungsgerechtigkeit", "KMK-Strategie", "digitale Kompetenzen"

6. **Zeige Nachhaltigkeit**: Wie wird das Projekt nach Förderung weiterlaufen?

---
GENERIERE NUN DEN PROFESSIONELLEN ANTRAGSENTWURF:

(Beginne direkt mit dem Entwurf. Keine Meta-Kommentare wie "Hier ist der Entwurf...")
""".strip()

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
    profile = dict(zip(columns, row))

    # Format for prompt
    profile_str = '\n'.join([f'- {k}: {v}' for k, v in profile.items() if v])
    return profile_str


async def call_deepseek_api(prompt: str, temperature: float = DEEPSEEK_TEMPERATURE) -> str:
    """
    Ruft DeepSeek API auf

    Args:
        prompt: Vollständiger Prompt
        temperature: Temperature setting

    Returns:
        Generierter Text
    """
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
        'temperature': temperature
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
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
    Generiert einen KI-Antragsentwurf mittels Advanced RAG + DeepSeek

    Improvements:
    - Hybrid search (Dense + BM25)
    - Query expansion for better recall
    - Reranking for better precision
    - Enhanced prompting (Few-shot + CoT)

    Args:
        request: funding_id, application_id, user_query

    Returns:
        Generierter Entwurf mit Metadaten
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

    # 4. Advanced RAG Retrieval
    print(f'[INFO] Starting Advanced RAG retrieval for query: "{request.user_query[:100]}..."')

    try:
        rag_result = await rag_pipeline.generate_draft(
            query=request.user_query,
            funding_id=request.funding_id,
            school_profile={'data': school_profile},
            top_k=5
        )
    except Exception as e:
        print(f'[ERROR] Advanced RAG failed: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'RAG retrieval failed: {str(e)}'
        )

    if 'error' in rag_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=rag_result['error']
        )

    compressed_context = rag_result['compressed_context']
    retrieval_metadata = rag_result.get('retrieval_metadata', {})

    # 5. Build Enhanced Prompt
    prompt = ENHANCED_PROMPT_TEMPLATE.format(
        context_chunks=compressed_context,
        school_profile=school_profile,
        user_query=request.user_query
    )

    # 6. Call DeepSeek API
    print('[INFO] Calling DeepSeek API for generation...')
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

    metadata = json.dumps({
        'model': DEEPSEEK_MODEL,
        'temperature': DEEPSEEK_TEMPERATURE,
        'max_tokens': DEEPSEEK_MAX_TOKENS,
        'rag_version': 'advanced_v2',
        'retrieval_metadata': retrieval_metadata,
        'features_used': {
            'hybrid_search': True,
            'query_expansion': rag_pipeline.enable_query_expansion,
            'reranking': rag_pipeline.enable_reranking,
            'compression': rag_pipeline.enable_compression
        }
    })

    draft_id_var = cursor.var(str)

    with get_db_cursor() as cursor:
        cursor.execute(insert_query, {
            'application_id': request.application_id,
            'generated_content': generated_content,
            'model_used': f'{DEEPSEEK_MODEL}_advanced_rag_v2',
            'prompt_used': prompt,
            'metadata': metadata,
            'draft_id': draft_id_var
        })

    draft_id = draft_id_var.getvalue()[0]

    print(f'[SUCCESS] Draft generated: {draft_id}')

    return DraftGenerateResponse(
        draft_id=draft_id,
        application_id=request.application_id,
        generated_content=generated_content,
        model_used=f'{DEEPSEEK_MODEL}_advanced_rag_v2',
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
    # Verify Access
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


@router.get('/pipeline/info')
async def get_pipeline_info(current_user: dict = Depends(get_current_user)):
    """
    Get Advanced RAG Pipeline information

    Returns:
        Pipeline configuration and stats
    """
    info = rag_pipeline.get_pipeline_info()
    return info
