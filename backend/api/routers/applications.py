"""
Applications Router
Antragsverwaltung für Schulen
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from api.models import Application, ApplicationCreate, ApplicationUpdate
from api.auth_utils import get_current_user
from utils.db_adapter import get_db_cursor

router = APIRouter()


@router.get('/', response_model=List[Application])
async def list_applications(current_user: dict = Depends(get_current_user)):
    """
    Liste aller Anträge der Schule des aktuellen Users

    Returns:
        Liste von Anträgen (nur der eigenen Schule!)
    """
    query = """
    SELECT
        RAWTOHEX(application_id) as application_id,
        RAWTOHEX(school_id) as school_id,
        RAWTOHEX(user_id_created) as user_id_created,
        RAWTOHEX(funding_id_linked) as funding_id_linked,
        title,
        status,
        projektbeschreibung,
        budget_total,
        submission_date,
        decision_status,
        created_at,
        updated_at
    FROM APPLICATIONS
    WHERE RAWTOHEX(school_id) = :school_id
    ORDER BY created_at DESC
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, {'school_id': current_user['school_id']})

        columns = [col[0].lower() for col in cursor.description]
        results = []

        for row in cursor:
            data = dict(zip(columns, row))
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
        RAWTOHEX(application_id) as application_id,
        RAWTOHEX(school_id) as school_id,
        RAWTOHEX(user_id_created) as user_id_created,
        RAWTOHEX(funding_id_linked) as funding_id_linked,
        title,
        status,
        projektbeschreibung,
        budget_total,
        submission_date,
        decision_status,
        notes,
        created_at,
        updated_at
    FROM APPLICATIONS
    WHERE RAWTOHEX(application_id) = :application_id
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, {'application_id': application_id})
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail='Application not found')

    # Parse Result
    columns = [col[0].lower() for col in cursor.description]
    data = dict(zip(columns, row))

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
    WHERE RAWTOHEX(funding_id) = :funding_id AND is_active = 1
    """

    with get_db_cursor() as cursor:
        cursor.execute(funding_check, {'funding_id': app_data.funding_id})
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail='Funding not found')

    # Insert Application
    insert_query = """
    INSERT INTO APPLICATIONS (
        school_id,
        user_id_created,
        funding_id_linked,
        title,
        projektbeschreibung,
        status
    ) VALUES (
        HEXTORAW(:school_id),
        HEXTORAW(:user_id),
        HEXTORAW(:funding_id),
        :title,
        :projektbeschreibung,
        'entwurf'
    ) RETURNING RAWTOHEX(application_id) INTO :application_id
    """

    application_id_var = cursor.var(str)

    with get_db_cursor() as cursor:
        cursor.execute(insert_query, {
            'school_id': current_user['school_id'],
            'user_id': current_user['user_id'],
            'funding_id': app_data.funding_id,
            'title': app_data.title,
            'projektbeschreibung': app_data.projektbeschreibung,
            'application_id': application_id_var
        })

    # Return created application
    application_id = application_id_var.getvalue()[0]
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
    params = {'application_id': application_id}

    if updates.title is not None:
        update_fields.append('title = :title')
        params['title'] = updates.title

    if updates.projektbeschreibung is not None:
        update_fields.append('projektbeschreibung = :projektbeschreibung')
        params['projektbeschreibung'] = updates.projektbeschreibung

    if updates.status is not None:
        update_fields.append('status = :status')
        params['status'] = updates.status

    if updates.budget_total is not None:
        update_fields.append('budget_total = :budget_total')
        params['budget_total'] = updates.budget_total

    if updates.notes is not None:
        update_fields.append('notes = :notes')
        params['notes'] = updates.notes

    if not update_fields:
        # Keine Updates
        return app

    # Execute Update
    update_query = f"""
    UPDATE APPLICATIONS
    SET {', '.join(update_fields)}
    WHERE RAWTOHEX(application_id) = :application_id
    """

    with get_db_cursor() as cursor:
        cursor.execute(update_query, params)

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
    if app.status != 'entwurf':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only draft applications can be deleted'
        )

    # Delete
    delete_query = """
    DELETE FROM APPLICATIONS
    WHERE RAWTOHEX(application_id) = :application_id
    """

    with get_db_cursor() as cursor:
        cursor.execute(delete_query, {'application_id': application_id})

    return None
