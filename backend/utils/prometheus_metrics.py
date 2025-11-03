"""
Prometheus Metrics for EduFunds Backend
Defines custom business and application metrics
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
from typing import Callable, Any


# =============================================================================
# HTTP Metrics (automatically collected by prometheus-fastapi-instrumentator)
# =============================================================================
# - http_requests_total (counter)
# - http_request_duration_seconds (histogram)
# - http_requests_in_progress (gauge)


# =============================================================================
# Application Metrics
# =============================================================================

# Draft Generation
draft_generation_total = Counter(
    'draft_generation_total',
    'Total AI drafts generated',
    ['status', 'funding_type', 'school_id']
)

draft_generation_duration = Histogram(
    'draft_generation_duration_seconds',
    'Time to generate AI draft',
    buckets=[1, 2, 5, 10, 15, 30, 60, 120, 300]
)

draft_generation_tokens = Histogram(
    'draft_generation_tokens_total',
    'Tokens consumed per draft generation',
    labelnames=['type'],  # prompt or completion
    buckets=[100, 500, 1000, 2000, 5000, 10000, 20000]
)

# RAG Search
rag_search_total = Counter(
    'rag_search_total',
    'Total RAG searches performed',
    ['status', 'search_type']
)

rag_search_duration = Histogram(
    'rag_search_duration_seconds',
    'RAG search latency',
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2, 5]
)

rag_search_results = Histogram(
    'rag_search_results_count',
    'Number of results returned by RAG search',
    buckets=[0, 1, 3, 5, 10, 20, 50]
)

# Database Metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query execution time',
    labelnames=['operation', 'table'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5]
)

db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Database connection pool size',
    ['state']  # active, idle
)

# ChromaDB Metrics
chromadb_documents_total = Gauge(
    'chromadb_documents_total',
    'Total documents indexed in ChromaDB',
    ['collection']
)

chromadb_query_duration = Histogram(
    'chromadb_query_duration_seconds',
    'ChromaDB query execution time',
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5]
)

# External API Metrics (DeepSeek)
deepseek_api_calls_total = Counter(
    'deepseek_api_calls_total',
    'Total DeepSeek API calls',
    ['endpoint', 'status']
)

deepseek_api_duration = Histogram(
    'deepseek_api_duration_seconds',
    'DeepSeek API call duration',
    buckets=[1, 2, 5, 10, 15, 30, 60]
)

deepseek_tokens_total = Counter(
    'deepseek_tokens_total',
    'Total tokens consumed',
    ['type']  # prompt or completion
)

deepseek_cost_usd = Counter(
    'deepseek_cost_usd_total',
    'Estimated DeepSeek API cost in USD'
)

# Scraper Metrics
scraper_runs_total = Counter(
    'scraper_runs_total',
    'Total scraper runs',
    ['status', 'source']  # success/error, ministerien/stiftungen
)

scraper_programs_discovered = Counter(
    'scraper_programs_discovered_total',
    'Total funding programs discovered',
    ['source']
)

scraper_duration = Histogram(
    'scraper_duration_seconds',
    'Scraper execution time',
    labelnames=['source'],
    buckets=[60, 300, 600, 1800, 3600, 7200]
)


# =============================================================================
# Business Metrics
# =============================================================================

# User Metrics
active_schools_total = Gauge(
    'active_schools_total',
    'Total active schools (all time)'
)

active_users_total = Gauge(
    'active_users_total',
    'Total active users (all time)'
)

# Application Metrics
applications_total = Counter(
    'applications_total',
    'Total applications created',
    ['status', 'funding_type']
)

applications_submitted_total = Counter(
    'applications_submitted_total',
    'Total applications submitted',
    ['school_id', 'funding_type']
)

# Funding Programs
funding_programs_total = Gauge(
    'funding_programs_total',
    'Total funding programs in database',
    ['source', 'status']
)

funding_programs_indexed = Gauge(
    'funding_programs_indexed_total',
    'Total funding programs indexed in RAG'
)


# =============================================================================
# System Information
# =============================================================================

app_info = Info('edufunds_app', 'Application information')
app_info.info({
    'version': '1.0.0',
    'env': 'production',
    'database': 'sqlite',  # or 'oracle'
    'rag_enabled': 'true',
})


# =============================================================================
# Metric Helper Functions
# =============================================================================

def track_draft_generation(func: Callable) -> Callable:
    """
    Decorator to track draft generation metrics

    Usage:
        @track_draft_generation
        async def generate_draft(...):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)

            # Track success
            duration = time.time() - start_time
            draft_generation_duration.observe(duration)
            draft_generation_total.labels(
                status='success',
                funding_type=kwargs.get('funding_type', 'unknown'),
                school_id=kwargs.get('school_id', 'unknown')
            ).inc()

            return result

        except Exception as e:
            # Track failure
            draft_generation_total.labels(
                status='error',
                funding_type=kwargs.get('funding_type', 'unknown'),
                school_id=kwargs.get('school_id', 'unknown')
            ).inc()
            raise

    return wrapper


def track_rag_search(func: Callable) -> Callable:
    """
    Decorator to track RAG search metrics

    Usage:
        @track_rag_search
        async def search_funding_programs(...):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            results = await func(*args, **kwargs)

            # Track success
            duration = time.time() - start_time
            rag_search_duration.observe(duration)
            rag_search_total.labels(
                status='success',
                search_type=kwargs.get('search_type', 'semantic')
            ).inc()
            rag_search_results.observe(len(results) if results else 0)

            return results

        except Exception as e:
            # Track failure
            rag_search_total.labels(
                status='error',
                search_type=kwargs.get('search_type', 'semantic')
            ).inc()
            raise

    return wrapper


def track_db_query(operation: str, table: str):
    """
    Decorator factory to track database query metrics

    Usage:
        @track_db_query('SELECT', 'funding_opportunities')
        def get_funding_programs(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                db_query_duration.labels(operation=operation, table=table).observe(duration)
                return result

            except Exception as e:
                # Still track duration even on error
                duration = time.time() - start_time
                db_query_duration.labels(operation=operation, table=table).observe(duration)
                raise

        return wrapper
    return decorator


def track_deepseek_call(func: Callable) -> Callable:
    """
    Decorator to track DeepSeek API calls

    Usage:
        @track_deepseek_call
        async def call_deepseek_api(...):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            response = await func(*args, **kwargs)

            # Track success
            duration = time.time() - start_time
            deepseek_api_duration.observe(duration)
            deepseek_api_calls_total.labels(endpoint='chat', status='success').inc()

            # Track token usage (if response contains usage)
            if hasattr(response, 'usage'):
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens

                deepseek_tokens_total.labels(type='prompt').inc(prompt_tokens)
                deepseek_tokens_total.labels(type='completion').inc(completion_tokens)

                # DeepSeek pricing: ~$0.14 per 1M tokens
                cost = (prompt_tokens + completion_tokens) * 0.00000014
                deepseek_cost_usd.inc(cost)

            return response

        except Exception as e:
            # Track failure
            deepseek_api_calls_total.labels(endpoint='chat', status='error').inc()
            raise

    return wrapper


# =============================================================================
# Example Usage in Routers
# =============================================================================

"""
from utils.prometheus_metrics import (
    track_draft_generation,
    draft_generation_tokens,
    applications_total,
)

@router.post('/generate-draft')
@track_draft_generation
async def generate_draft(
    request: DraftRequest,
    user: User = Depends(get_current_user)
):
    # Generate draft
    draft = await ai_service.generate_draft(
        funding_id=request.funding_id,
        school_id=user.school_id,
    )

    # Track additional metrics
    draft_generation_tokens.labels(type='prompt').observe(draft.prompt_tokens)
    draft_generation_tokens.labels(type='completion').observe(draft.completion_tokens)
    applications_total.labels(status='draft', funding_type=draft.funding_type).inc()

    return draft
"""
