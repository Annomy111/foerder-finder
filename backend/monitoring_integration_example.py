"""
EduFunds Backend - Monitoring Integration Examples
Shows how to integrate Prometheus metrics and structured logging into FastAPI routers
"""

import time
from fastapi import APIRouter, Depends, HTTPException, Request
from utils.logging_config import get_logger
from utils.prometheus_metrics import (
    track_draft_generation,
    track_rag_search,
    track_deepseek_call,
    draft_generation_tokens,
    applications_total,
    rag_search_results,
    deepseek_tokens_total,
    deepseek_cost_usd,
)

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()


# =============================================================================
# Example 1: Draft Generation with Full Monitoring
# =============================================================================

@router.post('/generate-draft')
@track_draft_generation  # Automatic metric tracking
async def generate_draft(
    request: DraftRequest,
    user: User = Depends(get_current_user),
    http_request: Request = None,
):
    """
    Generate AI draft with comprehensive monitoring
    """
    # Log request started
    logger.info(
        'draft_generation_started',
        user_id=user.id,
        school_id=user.school_id,
        funding_id=request.funding_id,
        client_ip=http_request.client.host if http_request else None,
    )

    try:
        # Fetch funding program
        funding = await get_funding_program(request.funding_id)

        # RAG search for relevant context
        search_start = time.time()
        context = await search_funding_context(funding.title, funding.description)
        search_duration = time.time() - search_start

        logger.debug(
            'rag_search_completed',
            funding_id=request.funding_id,
            results_count=len(context),
            duration_ms=search_duration * 1000,
        )

        # Track RAG search metrics
        rag_search_results.observe(len(context))

        # Generate draft via DeepSeek
        deepseek_start = time.time()
        draft = await call_deepseek_for_draft(
            funding=funding,
            context=context,
            school_info=user.school,
        )
        deepseek_duration = time.time() - deepseek_start

        # Track token usage
        draft_generation_tokens.labels(type='prompt').observe(draft.prompt_tokens)
        draft_generation_tokens.labels(type='completion').observe(draft.completion_tokens)
        deepseek_tokens_total.labels(type='prompt').inc(draft.prompt_tokens)
        deepseek_tokens_total.labels(type='completion').inc(draft.completion_tokens)

        # Calculate cost
        cost = (draft.prompt_tokens + draft.completion_tokens) * 0.00000014
        deepseek_cost_usd.inc(cost)

        # Track application creation
        applications_total.labels(
            status='draft',
            funding_type=funding.source_type,
        ).inc()

        # Log success
        logger.info(
            'draft_generation_success',
            user_id=user.id,
            school_id=user.school_id,
            funding_id=request.funding_id,
            prompt_tokens=draft.prompt_tokens,
            completion_tokens=draft.completion_tokens,
            cost_usd=cost,
            rag_duration_ms=search_duration * 1000,
            deepseek_duration_ms=deepseek_duration * 1000,
            total_duration_ms=(search_duration + deepseek_duration) * 1000,
        )

        return {
            'draft_id': draft.id,
            'content': draft.content,
            'metadata': {
                'tokens_used': draft.prompt_tokens + draft.completion_tokens,
                'cost_usd': round(cost, 6),
                'generation_time_ms': round((search_duration + deepseek_duration) * 1000, 2),
            }
        }

    except Exception as e:
        # Log error with full context
        logger.error(
            'draft_generation_failed',
            user_id=user.id,
            school_id=user.school_id,
            funding_id=request.funding_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,  # Include stack trace
        )

        # Re-raise (metrics tracked by decorator)
        raise HTTPException(
            status_code=500,
            detail='Draft generation failed. Please try again.',
        )


# =============================================================================
# Example 2: RAG Search with Monitoring
# =============================================================================

@router.get('/search')
@track_rag_search  # Automatic metric tracking
async def search_funding_programs(
    query: str,
    limit: int = 10,
    user: User = Depends(get_current_user),
):
    """
    Search funding programs with RAG
    """
    logger.info(
        'funding_search_started',
        user_id=user.id,
        school_id=user.school_id,
        query=query[:100],  # Truncate long queries
        limit=limit,
    )

    try:
        # Perform RAG search
        results = await chromadb_search(
            query=query,
            n_results=limit,
            filter={'school_eligible': True},
        )

        logger.info(
            'funding_search_success',
            user_id=user.id,
            query=query[:100],
            results_count=len(results),
        )

        return {
            'results': results,
            'count': len(results),
            'query': query,
        }

    except Exception as e:
        logger.error(
            'funding_search_failed',
            user_id=user.id,
            query=query[:100],
            error=str(e),
            exc_info=True,
        )
        raise


# =============================================================================
# Example 3: DeepSeek API Call with Monitoring
# =============================================================================

@track_deepseek_call  # Automatic metric tracking
async def call_deepseek_for_draft(funding, context, school_info):
    """
    Call DeepSeek API with automatic monitoring
    """
    import openai
    import os

    openai.api_key = os.getenv('DEEPSEEK_API_KEY')
    openai.api_base = 'https://api.deepseek.com/v1'

    prompt = f"""
    Du bist ein Experte für Fördermittelanträge im Bildungsbereich.

    Erstelle einen Antrag für folgende Fördermöglichkeit:

    **Förderprogramm:** {funding.title}
    **Beschreibung:** {funding.description}

    **Schule:**
    - Name: {school_info.name}
    - Typ: {school_info.type}
    - PLZ/Ort: {school_info.postal_code} {school_info.city}

    **Relevanter Kontext:**
    {context}

    Erstelle einen professionellen Antragsentwurf (max. 2000 Wörter).
    """

    logger.debug(
        'deepseek_api_call_started',
        model='deepseek-chat',
        prompt_length=len(prompt),
    )

    try:
        response = await openai.ChatCompletion.acreate(
            model='deepseek-chat',
            messages=[
                {'role': 'system', 'content': 'Du bist ein Experte für Fördermittelanträge.'},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=2048,
            temperature=0.5,
        )

        draft_content = response.choices[0].message.content

        logger.debug(
            'deepseek_api_call_success',
            model='deepseek-chat',
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            response_length=len(draft_content),
        )

        # Return draft with metadata
        return {
            'id': generate_uuid(),
            'content': draft_content,
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
        }

    except Exception as e:
        logger.error(
            'deepseek_api_call_failed',
            model='deepseek-chat',
            error=str(e),
            exc_info=True,
        )
        raise


# =============================================================================
# Example 4: Database Query with Monitoring
# =============================================================================

from utils.prometheus_metrics import track_db_query

@track_db_query('SELECT', 'funding_opportunities')
def get_funding_program(funding_id: int):
    """
    Fetch funding program from database with monitoring
    """
    logger.debug(
        'db_query_started',
        operation='SELECT',
        table='funding_opportunities',
        funding_id=funding_id,
    )

    try:
        # Execute query
        query = 'SELECT * FROM funding_opportunities WHERE id = ?'
        result = execute_query(query, (funding_id,))

        if not result:
            logger.warning(
                'funding_program_not_found',
                funding_id=funding_id,
            )
            raise HTTPException(status_code=404, detail='Funding program not found')

        logger.debug(
            'db_query_success',
            operation='SELECT',
            table='funding_opportunities',
            funding_id=funding_id,
        )

        return result[0]

    except Exception as e:
        logger.error(
            'db_query_failed',
            operation='SELECT',
            table='funding_opportunities',
            funding_id=funding_id,
            error=str(e),
            exc_info=True,
        )
        raise


# =============================================================================
# Example 5: Middleware for Request Logging
# =============================================================================

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests with structured logging
    """

    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = generate_uuid()
        request.state.request_id = request_id

        # Log request started
        start_time = time.time()

        logger.info(
            'http_request_started',
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host,
            user_agent=request.headers.get('user-agent', 'unknown'),
        )

        try:
            # Process request
            response = await call_next(request)

            # Log request completed
            duration = time.time() - start_time

            logger.info(
                'http_request_completed',
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )

            return response

        except Exception as e:
            # Log request failed
            duration = time.time() - start_time

            logger.error(
                'http_request_failed',
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration * 1000, 2),
                exc_info=True,
            )

            raise


# =============================================================================
# Add Middleware to FastAPI App (in main.py)
# =============================================================================

"""
from api.main import app
from monitoring_integration_example import RequestLoggingMiddleware

app.add_middleware(RequestLoggingMiddleware)
"""


# =============================================================================
# Example 6: Background Task Monitoring
# =============================================================================

from utils.prometheus_metrics import scraper_runs_total, scraper_duration

async def run_scraper_job(source: str):
    """
    Run scraper with monitoring
    """
    logger.info(
        'scraper_job_started',
        source=source,
    )

    start_time = time.time()

    try:
        # Run scraper
        result = await scrape_funding_programs(source)

        duration = time.time() - start_time

        # Track metrics
        scraper_runs_total.labels(status='success', source=source).inc()
        scraper_duration.labels(source=source).observe(duration)

        logger.info(
            'scraper_job_success',
            source=source,
            programs_discovered=result.count,
            duration_seconds=round(duration, 2),
        )

        return result

    except Exception as e:
        duration = time.time() - start_time

        # Track failure
        scraper_runs_total.labels(status='error', source=source).inc()
        scraper_duration.labels(source=source).observe(duration)

        logger.error(
            'scraper_job_failed',
            source=source,
            error=str(e),
            duration_seconds=round(duration, 2),
            exc_info=True,
        )

        raise


# =============================================================================
# Helper Functions
# =============================================================================

def generate_uuid():
    """Generate UUID for request tracking"""
    import uuid
    return str(uuid.uuid4())


def execute_query(query: str, params: tuple):
    """Execute database query (placeholder)"""
    pass


async def chromadb_search(query: str, n_results: int, filter: dict):
    """Search ChromaDB (placeholder)"""
    pass


async def scrape_funding_programs(source: str):
    """Scrape funding programs (placeholder)"""
    pass
