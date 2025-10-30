"""
Admin Router - Protected endpoints for system administration
Protected by ADMIN_SECRET_TOKEN from environment
"""

import sys
import os
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel
from typing import Optional

from api.auth_utils import hash_password
from utils.db_adapter import get_db_cursor, USE_SQLITE
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Admin Secret Token (must be set in environment)
ADMIN_SECRET_TOKEN = os.getenv('ADMIN_SECRET_TOKEN', 'change-me-in-production')


class SchoolCreate(BaseModel):
    """Schema for creating a new school"""
    name: str
    address: str
    city: str
    postal_code: str
    state: Optional[str] = None
    contact_email: str
    contact_phone: Optional[str] = None
    logo_url: Optional[str] = None
    admin_email: str
    admin_password: str
    admin_first_name: str
    admin_last_name: str


class SchoolResponse(BaseModel):
    """Response after creating a school"""
    school_id: str
    admin_user_id: str
    school_name: str
    admin_email: str
    message: str


def generate_hex_id():
    """Generate a hex ID compatible with both Oracle RAW and SQLite TEXT"""
    return str(uuid.uuid4()).replace('-', '').upper()


def verify_admin_token(x_admin_token: str = Header(...)):
    """Verify admin token from header"""
    if x_admin_token != ADMIN_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid admin token'
        )
    return True


@router.post('/seed-school', response_model=SchoolResponse)
async def seed_school(school: SchoolCreate, x_admin_token: str = Header(...)):
    """
    Create a new school with admin user (Protected endpoint)

    Requires X-Admin-Token header with valid admin secret

    Args:
        school: School and admin user data
        x_admin_token: Admin secret token from header

    Returns:
        School and admin user IDs

    Raises:
        401: Invalid admin token
        409: School or email already exists
    """
    # Verify admin token
    verify_admin_token(x_admin_token)

    school_id = generate_hex_id()
    admin_id = generate_hex_id()

    # Hash admin password using passlib (backend-compatible)
    admin_password_hash = hash_password(school.admin_password)

    try:
        with get_db_cursor() as cursor:
            # 1. Create school
            if USE_SQLITE:
                cursor.execute("""
                    INSERT INTO SCHOOLS (school_id, name, address, city, postal_code, contact_email, contact_phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    school_id,
                    school.name,
                    school.address,
                    school.city,
                    school.postal_code,
                    school.contact_email,
                    school.contact_phone
                ))
            else:
                # Oracle version
                cursor.execute("""
                    INSERT INTO SCHOOLS (school_id, name, address, city, state, postal_code, contact_email, contact_phone, logo_url)
                    VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
                """, (
                    school_id,
                    school.name,
                    school.address,
                    school.city,
                    school.state,
                    school.postal_code,
                    school.contact_email,
                    school.contact_phone,
                    school.logo_url
                ))

            # 2. Create admin user
            if USE_SQLITE:
                cursor.execute("""
                    INSERT INTO USERS (user_id, school_id, email, password_hash, first_name, last_name, role, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    admin_id,
                    school_id,
                    school.admin_email,
                    admin_password_hash,
                    school.admin_first_name,
                    school.admin_last_name,
                    'admin',
                    1
                ))
            else:
                # Oracle version - check if FULL_NAME or FIRST_NAME/LAST_NAME
                cursor.execute("SELECT column_name FROM user_tab_columns WHERE table_name = 'USERS' AND column_name IN ('FULL_NAME', 'FIRST_NAME')")
                columns = [row[0] for row in cursor.fetchall()]

                if 'FULL_NAME' in columns:
                    cursor.execute("""
                        INSERT INTO USERS (user_id, school_id, email, password_hash, full_name, role, is_active)
                        VALUES (:1, :2, :3, :4, :5, :6, :7)
                    """, (
                        admin_id,
                        school_id,
                        school.admin_email,
                        admin_password_hash,
                        f"{school.admin_first_name} {school.admin_last_name}",
                        'admin',
                        1
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO USERS (user_id, school_id, email, password_hash, first_name, last_name, role, is_active)
                        VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
                    """, (
                        admin_id,
                        school_id,
                        school.admin_email,
                        admin_password_hash,
                        school.admin_first_name,
                        school.admin_last_name,
                        'admin',
                        1
                    ))

            # Commit transaction
            if not USE_SQLITE:
                cursor.connection.commit()

        return SchoolResponse(
            school_id=school_id,
            admin_user_id=admin_id,
            school_name=school.name,
            admin_email=school.admin_email,
            message=f"School '{school.name}' created successfully with admin user"
        )

    except Exception as e:
        # Check if it's a unique constraint error
        error_msg = str(e).lower()
        if 'unique' in error_msg or 'duplicate' in error_msg or 'constraint' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='School or email already exists'
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Failed to create school: {str(e)}'
            )


@router.get('/health')
async def admin_health(x_admin_token: str = Header(...)):
    """
    Admin health check endpoint

    Requires X-Admin-Token header
    """
    verify_admin_token(x_admin_token)

    return {
        'status': 'healthy',
        'admin_access': 'authorized',
        'database_mode': 'sqlite' if USE_SQLITE else 'oracle'
    }
