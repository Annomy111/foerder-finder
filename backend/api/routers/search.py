"""
Search Router
RAG-basierte semantische Suche über Fördermöglichkeiten
"""

# CRITICAL: pysqlite3-binary workaround MUST be at the very top
# ChromaDB requires SQLite 3.35+, but system SQLite may be older
# This substitutes pysqlite3 module before ChromaDB imports sqlite3
try:
    __import__('pysqlite3')
    import sys as _sys
    _sys.modules['sqlite3'] = _sys.modules.pop('pysqlite3')
except ImportError:
    # pysqlite3-binary not installed, will use system SQLite (may fail)
    pass

import sys
import os
import time
import asyncio
from typing import List, Optional, Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from api.auth_utils import get_current_user
from rag_indexer.advanced_rag_pipeline import AdvancedRAGPipeline

router = APIRouter()


# ========== Request/Response Models ==========

class SearchRequest(BaseModel):
    """Suchanfrage für RAG-Pipeline"""
    query: str = Field(..., description="Suchquery (z.B. 'Tablets für Grundschule in Berlin')")
    top_k: int = Field(5, ge=1, le=20, description="Anzahl der Ergebnisse")
    funding_id: Optional[str] = Field(None, description="Optional: Filter auf spezifisches Funding")
    region: Optional[str] = Field(None, description="Optional: Filter nach Region (Berlin, Brandenburg, etc.)")
    expand_queries: bool = Field(True, description="Query Expansion aktivieren (RAG Fusion)")
    rerank_results: bool = Field(True, description="Reranking aktivieren (Cross-Encoder)")


class SearchResultChunk(BaseModel):
    """Einzelnes Such-Ergebnis (Chunk)"""
    chunk_id: str = Field(..., description="Eindeutige Chunk-ID")
    funding_id: str = Field(..., description="Zugehörige Funding-Opportunity-ID")
    text: str = Field(..., description="Relevanter Text-Chunk")
    score: float = Field(..., description="Relevanz-Score (0-1, höher = relevanter)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Zusätzliche Metadaten (source, region, etc.)")


class SearchResponse(BaseModel):
    """Antwort auf Suchanfrage"""
    query: str = Field(..., description="Original-Query")
    results: List[SearchResultChunk] = Field(..., description="Gefundene Chunks sortiert nach Relevanz")
    total_results: int = Field(..., description="Anzahl der Ergebnisse")
    retrieval_time_ms: float = Field(..., description="Retrieval-Zeit in Millisekunden")
    expanded_queries: Optional[List[str]] = Field(None, description="Erweiterte Queries (falls Query Expansion aktiv)")
    pipeline_config: Dict[str, bool] = Field(..., description="Pipeline-Konfiguration")


class RAGHealthResponse(BaseModel):
    """RAG-System Health Check"""
    status: str = Field(..., description="Status (ok, degraded, error)")
    chromadb_collection_count: int = Field(..., description="Anzahl Chunks in ChromaDB")
    embedder_model: str = Field(..., description="Verwendetes Embedding-Modell")
    reranker_model: str = Field(..., description="Verwendetes Reranking-Modell")
    query_expander_enabled: bool = Field(..., description="Query Expansion aktiviert")
    compression_enabled: bool = Field(..., description="Contextual Compression aktiviert")
    crag_enabled: bool = Field(..., description="CRAG Evaluation aktiviert")


# ========== Endpoints ==========

@router.post('/', response_model=SearchResponse)
async def search_funding_opportunities(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Semantische Suche über Fördermöglichkeiten mit Advanced RAG Pipeline

    Verwendet:
    - Hybrid Search (BM25 + BGE-M3 Vector Search)
    - Query Expansion (RAG Fusion)
    - Cross-Encoder Reranking
    - CRAG Quality Evaluation
    - Contextual Compression

    Args:
        request: Suchanfrage mit Query und Parametern
        current_user: Authentifizierter User

    Returns:
        SearchResponse mit relevanten Chunks und Metadaten

    Example:
        POST /api/v1/search
        {
            "query": "Tablets für Grundschule in Berlin",
            "top_k": 5,
            "region": "Berlin",
            "expand_queries": true,
            "rerank_results": true
        }
    """
    try:
        start_time = time.time()

        # Initialize Advanced RAG Pipeline
        pipeline = AdvancedRAGPipeline(
            enable_query_expansion=request.expand_queries,
            enable_reranking=request.rerank_results,
            enable_compression=True,
            enable_crag=True,
            verbose=False  # Disable verbose logging in API
        )

        # Build metadata filter from request
        where_filter = None
        if request.funding_id or request.region:
            where_filter = {}
            if request.funding_id:
                where_filter['funding_id'] = request.funding_id
            if request.region:
                where_filter['region'] = request.region

        # Execute retrieval
        results = await pipeline.retrieve(
            query=request.query,
            funding_id=request.funding_id,
            top_k=request.top_k,
            expand_queries=request.expand_queries,
            rerank_results=request.rerank_results
        )

        retrieval_time_ms = (time.time() - start_time) * 1000

        # Format results
        search_results = [
            SearchResultChunk(
                chunk_id=result.get('id', 'unknown'),
                funding_id=result.get('metadata', {}).get('funding_id', 'unknown'),
                text=result.get('text', ''),
                score=result.get('score', 0.0),
                metadata=result.get('metadata', {})
            )
            for result in results
        ]

        # Extract expanded queries if available
        expanded_queries = None
        if request.expand_queries and pipeline.query_expander:
            # Query expander generates multiple queries internally
            # We'll return this info for transparency
            expanded_queries = [request.query]  # Original query always included

        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            retrieval_time_ms=retrieval_time_ms,
            expanded_queries=expanded_queries,
            pipeline_config={
                'query_expansion': request.expand_queries,
                'reranking': request.rerank_results,
                'compression': True,
                'crag': True
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Search failed: {str(e)}'
        )


@router.get('/health', response_model=RAGHealthResponse)
async def rag_health_check(
    current_user: dict = Depends(get_current_user)
):
    """
    RAG-System Health Check

    Prüft Status des RAG-Systems:
    - ChromaDB Collection Count
    - Embedder und Reranker Models
    - Pipeline-Konfiguration

    Returns:
        RAGHealthResponse mit System-Status
    """
    try:
        # Initialize pipeline to check components
        pipeline = AdvancedRAGPipeline(verbose=False)

        # Get ChromaDB collection count
        collection = pipeline.searcher.collection
        collection_count = collection.count()

        # Get embedder model name
        embedder_model = pipeline.embedder.model_name if hasattr(pipeline.embedder, 'model_name') else 'BAAI/bge-m3'

        # Get reranker model name
        reranker_model = 'BAAI/bge-reranker-base' if pipeline.reranker else 'disabled'

        # Determine status
        if collection_count == 0:
            status = 'degraded'  # No data indexed
        elif collection_count < 50:
            status = 'degraded'  # Very little data
        else:
            status = 'ok'

        return RAGHealthResponse(
            status=status,
            chromadb_collection_count=collection_count,
            embedder_model=embedder_model,
            reranker_model=reranker_model,
            query_expander_enabled=pipeline.query_expander is not None,
            compression_enabled=True,  # Always enabled in current pipeline
            crag_enabled=True  # Always enabled in current pipeline
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'RAG health check failed: {str(e)}'
        )


@router.get('/quick', response_model=SearchResponse)
async def quick_search(
    q: str = Query(..., description="Suchquery", min_length=3),
    limit: int = Query(5, ge=1, le=10, description="Anzahl Ergebnisse"),
    current_user: dict = Depends(get_current_user)
):
    """
    Schnelle Suche (GET-Endpoint für einfache Queries)

    Simplified search endpoint optimized for speed:
    - No query expansion
    - No reranking
    - Fast hybrid search only

    Args:
        q: Suchquery
        limit: Anzahl Ergebnisse (max 10)
        current_user: Authentifizierter User

    Returns:
        SearchResponse mit relevanten Chunks

    Example:
        GET /api/v1/search/quick?q=Tablets&limit=5
    """
    try:
        start_time = time.time()

        # Initialize pipeline with minimal features for speed
        pipeline = AdvancedRAGPipeline(
            enable_query_expansion=False,
            enable_reranking=False,
            enable_compression=False,
            enable_crag=False,
            verbose=False
        )

        # Execute fast retrieval
        results = await pipeline.retrieve(
            query=q,
            top_k=limit,
            expand_queries=False,
            rerank_results=False
        )

        retrieval_time_ms = (time.time() - start_time) * 1000

        # Format results
        search_results = [
            SearchResultChunk(
                chunk_id=result.get('id', 'unknown'),
                funding_id=result.get('metadata', {}).get('funding_id', 'unknown'),
                text=result.get('text', ''),
                score=result.get('score', 0.0),
                metadata=result.get('metadata', {})
            )
            for result in results
        ]

        return SearchResponse(
            query=q,
            results=search_results,
            total_results=len(search_results),
            retrieval_time_ms=retrieval_time_ms,
            expanded_queries=None,
            pipeline_config={
                'query_expansion': False,
                'reranking': False,
                'compression': False,
                'crag': False
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Quick search failed: {str(e)}'
        )
