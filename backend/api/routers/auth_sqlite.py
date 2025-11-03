"""
Authentication Router (SQLite-compatible)
Login, Registration, JWT Tokens
"""

import sys
import os
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from api.models import UserLogin, Token, UserCreate, User
from api.auth_utils import hash_password, verify_password, create_access_token
from utils.db_adapter import get_db_cursor, USE_SQLITE

router = APIRouter()


def generate_hex_id():
    """Generate a hex ID compatible with both Oracle RAW and SQLite TEXT"""
    return str(uuid.uuid4()).replace('-', '').upper()


@router.post('/login', response_model=Token)
async def login(credentials: UserLogin):
    """
    Login Endpoint - Gibt JWT Token zurück

    Args:
        credentials: Email & Password

    Returns:
        JWT Access Token

    Raises:
        401: Bei falschen Credentials
    """
    # Hole User aus DB (SQLite-compatible query)
    if USE_SQLITE:
        query = """
        SELECT
            user_id,
            school_id,
            email,
            password_hash,
            role,
            is_active
        FROM USERS
        WHERE email = ?
        """
    else:
        query = """
        SELECT
            RAWTOHEX(user_id) as user_id,
            RAWTOHEX(school_id) as school_id,
            email,
            password_hash,
            role,
            is_active
        FROM USERS
        WHERE email = :email
        """

    with get_db_cursor() as cursor:
        if USE_SQLITE:
            cursor.execute(query, (credentials.email,))
            row = cursor.fetchone()
        else:
            cursor.execute(query, {'email': credentials.email})
            row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )

    # Parse Result
    if USE_SQLITE:
        # SQLite returns Row objects
        user = {
            'user_id': row['user_id'],
            'school_id': row['school_id'],
            'email': row['email'],
            'password_hash': row['password_hash'],
            'role': row['role'],
            'is_active': bool(row['is_active'])
        }
    else:
        columns = ['user_id', 'school_id', 'email', 'password_hash', 'role', 'is_active']
        user = dict(zip(columns, row))

    # Check Active
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User account is inactive'
        )

    # Verify Password
    if not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )

    # Update Last Login
    if USE_SQLITE:
        update_query = """
        UPDATE USERS
        SET last_login = CURRENT_TIMESTAMP
        WHERE email = ?
        """
        with get_db_cursor() as cursor:
            cursor.execute(update_query, (credentials.email,))
    else:
        update_query = """
        UPDATE USERS
        SET last_login = SYSTIMESTAMP
        WHERE email = :email
        """
        with get_db_cursor() as cursor:
            cursor.execute(update_query, {'email': credentials.email})

    # Create JWT Token
    token_data = {
        'user_id': user['user_id'],
        'school_id': user['school_id'],
        'email': user['email'],
        'role': user['role']
    }
    access_token = create_access_token(token_data)

    return Token(
        access_token=access_token,
        user_id=user['user_id'],
        school_id=user['school_id'],
        role=user['role']
    )


@router.post('/register', response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    User Registration

    Args:
        user_data: User-Daten

    Returns:
        Erstellter User

    Raises:
        400: User existiert bereits
        404: Schule nicht gefunden
    """
    # Check if school exists
    if USE_SQLITE:
        school_check_query = """
        SELECT school_id FROM SCHOOLS
        WHERE school_id = ? AND is_active = 1
        """
    else:
        school_check_query = """
        SELECT school_id FROM SCHOOLS
        WHERE RAWTOHEX(school_id) = :school_id AND is_active = 1
        """

    with get_db_cursor() as cursor:
        if USE_SQLITE:
            cursor.execute(school_check_query, (user_data.school_id,))
        else:
            cursor.execute(school_check_query, {'school_id': user_data.school_id})

        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='School not found'
            )

    # Check if user already exists
    if USE_SQLITE:
        email_check_query = """
        SELECT email FROM USERS WHERE email = ?
        """
    else:
        email_check_query = """
        SELECT email FROM USERS WHERE email = :email
        """

    with get_db_cursor() as cursor:
        if USE_SQLITE:
            cursor.execute(email_check_query, (user_data.email,))
        else:
            cursor.execute(email_check_query, {'email': user_data.email})

        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email already registered'
            )

    # Hash Password
    password_hash = hash_password(user_data.password)

    # Generate new user_id
    user_id = generate_hex_id()

    # Insert User
    if USE_SQLITE:
        insert_query = """
        INSERT INTO USERS (
            user_id, school_id, email, password_hash, first_name, last_name, role
        ) VALUES (?, ?, ?, ?, ?, ?, 'lehrkraft')
        """
        with get_db_cursor() as cursor:
            cursor.execute(insert_query, (
                user_id,
                user_data.school_id,
                user_data.email,
                password_hash,
                user_data.first_name,
                user_data.last_name
            ))
    else:
        insert_query = """
        INSERT INTO USERS (
            school_id, email, password_hash, first_name, last_name, role
        ) VALUES (
            HEXTORAW(:school_id), :email, :password_hash, :first_name, :last_name, 'lehrkraft'
        ) RETURNING RAWTOHEX(user_id) INTO :user_id
        """
        user_id_var = cursor.var(str)
        with get_db_cursor() as cursor:
            cursor.execute(insert_query, {
                'school_id': user_data.school_id,
                'email': user_data.email,
                'password_hash': password_hash,
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'user_id': user_id_var
            })
            user_id = user_id_var.getvalue()[0]

    # Return created user (ohne password_hash!)
    return User(
        user_id=user_id,
        school_id=user_data.school_id,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role='lehrkraft',
        is_active=True,
        created_at=datetime.now()
    )
