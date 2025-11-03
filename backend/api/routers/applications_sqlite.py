"""
Applications Router (SQLite-compatible)
Antragsverwaltung für Schulen
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import uuid

from api.models import Application, ApplicationCreate, ApplicationUpdate
from api.auth_utils import get_current_user
from utils.db_adapter import get_db_cursor

router = APIRouter()


def generate_id():
    """Generate UUID without dashes for SQLite"""
    return str(uuid.uuid4()).replace('-', '').upper()


@router.get('/', response_model=List[Application])
async def list_applications(current_user: dict = Depends(get_current_user)):
    """
    Liste aller Anträge der Schule des aktuellen Users

    Returns:
        Liste von Anträgen (nur der eigenen Schule!)
    """
    query = """
    SELECT
        application_id,
        school_id,
        user_id,
        funding_id,
        title,
        status,
        draft_text,
        final_text,
        submitted_at,
        created_at
    FROM APPLICATIONS
    WHERE school_id = ?
    ORDER BY created_at DESC
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, (current_user['school_id'],))

        results = []
        for row in cursor:
            data = {
                'application_id': row['application_id'],
                'school_id': row['school_id'],
                'user_id': row['user_id'],
                'funding_id': row['funding_id'],
                'title': row['title'],
                'status': row['status'],
                'projektbeschreibung': row['draft_text'] or row['final_text'],
                'budget_total': None,
                'submission_date': row['submitted_at'],
                'decision_status': None,
                'notes': None,
                'created_at': row['created_at'],
                'updated_at': row['created_at']  # SQLite doesn't have updated_at
            }
            results.append(Application(**data))

    return results


@router.get('/{application_id}', response_model=Application)
async def get_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Details eines Antrags

    Args:
        application_id: ID des Antrags

    Returns:
        Antrags-Details

    Raises:
        404: Antrag nicht gefunden
        403: Zugriff verweigert (andere Schule)
    """
    query = """
    SELECT
        application_id,
        school_id,
        user_id,
        funding_id,
        title,
        status,
        draft_text,
        final_text,
        submitted_at,
        created_at
    FROM APPLICATIONS
    WHERE application_id = ?
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, (application_id,))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail='Application not found')

    # Parse Result
    data = {
        'application_id': row['application_id'],
        'school_id': row['school_id'],
        'user_id': row['user_id'],
        'funding_id': row['funding_id'],
        'title': row['title'],
        'status': row['status'],
        'projektbeschreibung': row['draft_text'] or row['final_text'],
        'budget_total': None,
        'submission_date': row['submitted_at'],
        'decision_status': None,
        'notes': None,
        'created_at': row['created_at'],
        'updated_at': row['created_at']  # SQLite doesn't have updated_at
    }

    # Verify School Access
    if data['school_id'] != current_user['school_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access to this application denied'
        )

    return Application(**data)


@router.post('/', response_model=Application, status_code=status.HTTP_201_CREATED)
async def create_application(
    app_data: ApplicationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Erstellt einen neuen Antrag

    Args:
        app_data: Antrags-Daten

    Returns:
        Erstellter Antrag
    """
    # Verify Funding exists
    funding_check = """
    SELECT funding_id FROM FUNDING_OPPORTUNITIES
    WHERE funding_id = ?
    """

    with get_db_cursor() as cursor:
        cursor.execute(funding_check, (app_data.funding_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail='Funding not found')

    # Generate new application ID
    application_id = generate_id()

    # Insert Application
    insert_query = """
    INSERT INTO APPLICATIONS (
        application_id,
        school_id,
        user_id,
        funding_id,
        title,
        draft_text,
        status
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    with get_db_cursor() as cursor:
        cursor.execute(insert_query, (
            application_id,
            current_user['school_id'],
            current_user['user_id'],
            app_data.funding_id,
            app_data.title,
            app_data.projektbeschreibung,
            'draft'
        ))

    # Return created application
    return await get_application(application_id, current_user)


@router.patch('/{application_id}', response_model=Application)
async def update_application(
    application_id: str,
    updates: ApplicationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Aktualisiert einen Antrag

    Args:
        application_id: ID des Antrags
        updates: Zu aktualisierende Felder

    Returns:
        Aktualisierter Antrag
    """
    # Verify Access
    app = await get_application(application_id, current_user)

    # Build UPDATE query
    update_fields = []
    params = []

    if updates.title is not None:
        update_fields.append('title = ?')
        params.append(updates.title)

    if updates.projektbeschreibung is not None:
        update_fields.append('draft_text = ?')
        params.append(updates.projektbeschreibung)

    if updates.status is not None:
        update_fields.append('status = ?')
        params.append(updates.status)

    if not update_fields:
        # Keine Updates
        return app

    # Add application_id to params
    params.append(application_id)

    # Execute Update
    update_query = f"""
    UPDATE APPLICATIONS
    SET {', '.join(update_fields)}
    WHERE application_id = ?
    """

    with get_db_cursor() as cursor:
        cursor.execute(update_query, tuple(params))

    # Return updated
    return await get_application(application_id, current_user)


@router.delete('/{application_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Löscht einen Antrag (nur Entwürfe)

    Args:
        application_id: ID des Antrags

    Raises:
        400: Antrag bereits eingereicht
    """
    # Verify Access
    app = await get_application(application_id, current_user)

    # Check Status
    if app.status != 'draft':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only draft applications can be deleted'
        )

    # Delete
    delete_query = """
    DELETE FROM APPLICATIONS
    WHERE application_id = ?
    """

    with get_db_cursor() as cursor:
        cursor.execute(delete_query, (application_id,))

    return None
