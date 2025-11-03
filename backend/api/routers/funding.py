"""
Funding Router
Fördermittel-Übersicht, Filter, Details
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List

from api.models import FundingOpportunity, FundingDetail, FundingFilter
from api.auth_utils import get_current_user
from utils.db_adapter import get_db_cursor

router = APIRouter()


@router.get('/', response_model=List[FundingOpportunity])
async def list_funding(
    region: str = Query(None),
    funding_area: str = Query(None),
    provider: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Liste aller aktiven Fördermittel mit optionalen Filtern

    Args:
        region: Filter nach Region
        funding_area: Filter nach Förderbereich
        provider: Filter nach Fördergeber
        limit: Anzahl Ergebnisse
        offset: Offset für Pagination

    Returns:
        Liste von Fördermitteln
    """
    # Build Query
    query = """
    SELECT
        RAWTOHEX(funding_id) as funding_id,
        title,
        source_url,
        deadline,
        provider,
        region,
        funding_area,
        min_funding_amount,
        max_funding_amount,
        tags,
        scraped_at
    FROM FUNDING_OPPORTUNITIES
    WHERE is_active = 1
    """

    params = {}

    # Filters
    if region:
        query += ' AND region = :region'
        params['region'] = region

    if funding_area:
        query += ' AND funding_area = :funding_area'
        params['funding_area'] = funding_area

    if provider:
        query += ' AND provider = :provider'
        params['provider'] = provider

    # Nur zukünftige Deadlines
    query += ' AND (deadline IS NULL OR deadline > SYSTIMESTAMP)'

    # Order & Limit
    query += ' ORDER BY deadline ASC NULLS LAST'
    query += ' OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY'

    params['offset'] = offset
    params['limit'] = limit

    # Execute
    with get_db_cursor() as cursor:
        cursor.execute(query, params)

        columns = [col[0].lower() for col in cursor.description]
        results = []

        for row in cursor:
            data = dict(zip(columns, row))

            # Parse tags (JSON Array -> List)
            if data.get('tags'):
                try:
                    data['tags'] = json.loads(data['tags'])
                except json.JSONDecodeError:
                    data['tags'] = []

            results.append(FundingOpportunity(**data))

    return results


@router.get('/{funding_id}', response_model=FundingDetail)
async def get_funding_detail(
    funding_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Detaillierte Informationen zu einer Förderausschreibung (inkl. Text)

    Args:
        funding_id: ID der Förderausschreibung

    Returns:
        Detaillierte Förderinformationen

    Raises:
        404: Förderung nicht gefunden
    """
    query = """
    SELECT
        RAWTOHEX(funding_id) as funding_id,
        title,
        source_url,
        deadline,
        provider,
        region,
        funding_area,
        min_funding_amount,
        max_funding_amount,
        tags,
        cleaned_text,
        metadata_json,
        scraped_at,
        eligibility,
        target_groups,
        evaluation_criteria,
        requirements,
        eligible_costs,
        application_process,
        contact_person,
        decision_timeline,
        funding_period,
        application_url,
        extraction_quality_score
    FROM FUNDING_OPPORTUNITIES
    WHERE RAWTOHEX(funding_id) = :funding_id
      AND is_active = 1
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, {'funding_id': funding_id})
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail='Funding not found')

    # Parse Result
    columns = [col[0].lower() for col in cursor.description]
    data = dict(zip(columns, row))

    # Parse JSON fields
    if data.get('tags'):
        try:
            data['tags'] = json.loads(data['tags'])
        except json.JSONDecodeError:
            data['tags'] = []

    if data.get('metadata_json'):
        try:
            data['metadata'] = json.loads(data['metadata_json'])
        except json.JSONDecodeError:
            data['metadata'] = {}
        del data['metadata_json']

    # Parse structured JSON array fields
    json_array_fields = [
        'eligibility', 'target_groups', 'evaluation_criteria',
        'requirements', 'eligible_costs'
    ]
    for field in json_array_fields:
        if data.get(field):
            try:
                data[field] = json.loads(data[field])
            except (json.JSONDecodeError, TypeError):
                data[field] = []
        else:
            data[field] = []

    return FundingDetail(**data)


@router.get('/filters/options')
async def get_filter_options(current_user: dict = Depends(get_current_user)):
    """
    Gibt verfügbare Filter-Optionen zurück (für Dropdown-Menüs)

    Returns:
        Dict mit Listen von verfügbaren Regionen, Areas, Providern
    """
    # Regionen
    regions_query = """
    SELECT DISTINCT region
    FROM FUNDING_OPPORTUNITIES
    WHERE is_active = 1 AND region IS NOT NULL
    ORDER BY region
    """

    # Funding Areas
    areas_query = """
    SELECT DISTINCT funding_area
    FROM FUNDING_OPPORTUNITIES
    WHERE is_active = 1 AND funding_area IS NOT NULL
    ORDER BY funding_area
    """

    # Providers
    providers_query = """
    SELECT DISTINCT provider
    FROM FUNDING_OPPORTUNITIES
    WHERE is_active = 1 AND provider IS NOT NULL
    ORDER BY provider
    """

    with get_db_cursor() as cursor:
        # Regions
        cursor.execute(regions_query)
        regions = [row[0] for row in cursor.fetchall()]

        # Areas
        cursor.execute(areas_query)
        areas = [row[0] for row in cursor.fetchall()]

        # Providers
        cursor.execute(providers_query)
        providers = [row[0] for row in cursor.fetchall()]

    return {
        'regions': regions,
        'funding_areas': areas,
        'providers': providers
    }
