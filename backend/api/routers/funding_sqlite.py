"""
Funding Router (SQLite-compatible)
Fördermittel-Übersicht, Filter, Details
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime

from api.models import FundingOpportunity, FundingDetail, FundingFilter
from api.auth_utils import get_current_user
from utils.db_adapter import get_db_cursor, USE_SQLITE

router = APIRouter()


@router.get('/', response_model=List[FundingOpportunity])
async def list_funding(
    provider: str = Query(None),
    categories: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    Liste aller aktiven Fördermittel mit optionalen Filtern

    PUBLIC ENDPOINT - Keine Authentifizierung erforderlich (Development Mode)

    Args:
        provider: Filter nach Fördergeber
        categories: Filter nach Kategorien
        limit: Anzahl Ergebnisse
        offset: Offset für Pagination

    Returns:
        Liste von Fördermitteln
    """
    # Build Query (SQLite-compatible)
    query = """
    SELECT
        funding_id,
        title,
        provider,
        url as source_url,
        application_deadline as deadline,
        funding_amount_min as min_funding_amount,
        funding_amount_max as max_funding_amount,
        categories,
        created_at as scraped_at,
        cleaned_text
    FROM FUNDING_OPPORTUNITIES
    """

    params = []
    where_clauses = []

    # Filters
    if provider:
        where_clauses.append('provider = ?')
        params.append(provider)

    if categories:
        where_clauses.append('categories LIKE ?')
        params.append(f'%{categories}%')

    # Only future deadlines
    where_clauses.append("(application_deadline IS NULL OR application_deadline > date('now'))")

    if where_clauses:
        query += ' WHERE ' + ' AND '.join(where_clauses)

    # Order & Limit
    query += ' ORDER BY application_deadline ASC'
    query += ' LIMIT ? OFFSET ?'

    params.extend([limit, offset])

    # Execute
    with get_db_cursor() as cursor:
        cursor.execute(query, tuple(params))

        results = []
        for row in cursor:
            # Convert SQLite Row to dict with proper field names for Pydantic
            # Parse datetime if needed
            scraped_at = row['scraped_at']
            if isinstance(scraped_at, str):
                scraped_at = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))

            deadline = row['deadline']
            if deadline and isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))

            data = {
                'funding_id': row['funding_id'],
                'title': row['title'],
                'source_url': row['source_url'] or '',  # Required field, provide default
                'deadline': deadline,
                'provider': row['provider'],
                'region': None,  # Optional field
                'funding_area': None,  # Optional field
                'min_funding_amount': row['min_funding_amount'],
                'max_funding_amount': row['max_funding_amount'],
                'tags': row['categories'].split(',') if row['categories'] else [],
                'scraped_at': scraped_at,
                'cleaned_text': row['cleaned_text'] if 'cleaned_text' in row.keys() else None
            }

            results.append(FundingOpportunity(**data))

    return results


@router.get('/{funding_id}', response_model=FundingDetail)
async def get_funding_detail(
    funding_id: str
):
    """
    Detaillierte Informationen zu einer Förderausschreibung (inkl. Text)

    PUBLIC ENDPOINT - Keine Authentifizierung erforderlich (Development Mode)

    Args:
        funding_id: ID der Förderausschreibung

    Returns:
        Detaillierte Förderinformationen

    Raises:
        404: Förderung nicht gefunden
    """
    query = """
    SELECT
        funding_id,
        title,
        provider,
        description,
        eligibility,
        application_deadline as deadline,
        funding_amount_min as min_funding_amount,
        funding_amount_max as max_funding_amount,
        categories,
        target_groups,
        url as source_url,
        source_url,
        cleaned_text,
        created_at as scraped_at
    FROM FUNDING_OPPORTUNITIES
    WHERE funding_id = ?
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, (funding_id,))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail='Funding not found')

    # Convert SQLite Row to dict with proper field names
    data = {
        'funding_id': row['funding_id'],
        'title': row['title'],
        'provider': row['provider'],
        'source_url': row['source_url'] or '',
        'deadline': row['deadline'],
        'region': None,
        'funding_area': None,
        'min_funding_amount': row['min_funding_amount'],
        'max_funding_amount': row['max_funding_amount'],
        'tags': row['categories'].split(',') if row['categories'] else [],
        'scraped_at': row['scraped_at'],
        'cleaned_text': row['cleaned_text'] or '',
        'metadata': {}
    }

    return FundingDetail(**data)


@router.get('/filters/options')
async def get_filter_options(current_user: dict = Depends(get_current_user)):
    """
    Gibt verfügbare Filter-Optionen zurück (für Dropdown-Menüs)

    Returns:
        Dict mit Listen von verfügbaren Providern und Kategorien
    """
    # Providers
    providers_query = """
    SELECT DISTINCT provider
    FROM FUNDING_OPPORTUNITIES
    WHERE provider IS NOT NULL
    ORDER BY provider
    """

    # Categories (need to split comma-separated values)
    categories_query = """
    SELECT DISTINCT categories
    FROM FUNDING_OPPORTUNITIES
    WHERE categories IS NOT NULL
    """

    with get_db_cursor() as cursor:
        # Providers
        cursor.execute(providers_query)
        providers = [row[0] for row in cursor.fetchall()]

        # Categories (split and unique)
        cursor.execute(categories_query)
        categories_set = set()
        for row in cursor.fetchall():
            if row[0]:
                categories_set.update([cat.strip() for cat in row[0].split(',')])

        categories = sorted(list(categories_set))

    return {
        'providers': providers,
        'categories': categories
    }
