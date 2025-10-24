"""
Authentication Router
Login, Registration, JWT Tokens
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from api.models import UserLogin, Token, UserCreate, User
from api.auth_utils import hash_password, verify_password, create_access_token
from utils.database import get_db_cursor

router = APIRouter()


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
    # Hole User aus DB
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
        cursor.execute(query, {'email': credentials.email})
        row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )

    # Parse Result
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
    school_check_query = """
    SELECT school_id FROM SCHOOLS
    WHERE RAWTOHEX(school_id) = :school_id AND is_active = 1
    """

    with get_db_cursor() as cursor:
        cursor.execute(school_check_query, {'school_id': user_data.school_id})
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='School not found'
            )

    # Check if user already exists
    email_check_query = """
    SELECT email FROM USERS WHERE email = :email
    """

    with get_db_cursor() as cursor:
        cursor.execute(email_check_query, {'email': user_data.email})
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email already registered'
            )

    # Hash Password
    password_hash = hash_password(user_data.password)

    # Insert User
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

    # Return created user (ohne password_hash!)
    return User(
        user_id=user_id_var.getvalue()[0],
        school_id=user_data.school_id,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role='lehrkraft',
        is_active=True,
        created_at=datetime.now()
    )
