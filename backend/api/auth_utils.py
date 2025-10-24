"""
Authentication Utilities - JWT & Password Hashing
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from utils.oci_secrets import get_jwt_secret

load_dotenv()

# Password Hashing
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# JWT Configuration
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# Security Scheme
security = HTTPBearer()


# ============================================================================
# Password Functions
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hasht ein Passwort mit bcrypt

    Args:
        password: Plaintext-Passwort

    Returns:
        Gehashtes Passwort
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifiziert ein Passwort gegen einen Hash

    Args:
        plain_password: Plaintext-Passwort
        hashed_password: Gehashtes Passwort

    Returns:
        True wenn korrekt, sonst False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT Functions
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Erstellt ein JWT Access Token

    Args:
        data: Payload-Daten (user_id, school_id, role)
        expires_delta: Optional - Ablaufzeit

    Returns:
        JWT Token String
    """
    to_encode = data.copy()

    # Expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

    to_encode.update({'exp': expire})

    # Hole JWT Secret aus OCI Vault
    secret_key = get_jwt_secret()

    # Encode Token
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Dekodiert ein JWT Token

    Args:
        token: JWT Token String

    Returns:
        Dekodierte Payload

    Raises:
        HTTPException: Bei ungültigem Token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        secret_key = get_jwt_secret()
        payload = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


# ============================================================================
# Dependency: Get Current User
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    FastAPI Dependency - Extrahiert aktuellen User aus JWT Token

    Args:
        credentials: HTTP Authorization Header

    Returns:
        User-Dict mit user_id, school_id, role

    Raises:
        HTTPException: Bei ungültigem Token
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    # Extrahiere User-Infos
    user_id = payload.get('user_id')
    school_id = payload.get('school_id')
    role = payload.get('role')

    if not user_id or not school_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token payload'
        )

    return {
        'user_id': user_id,
        'school_id': school_id,
        'role': role,
        'email': payload.get('email')
    }


# ============================================================================
# Dependency: Verify School Access
# ============================================================================

def verify_school_access(required_school_id: str):
    """
    Dependency Factory - Verifiziert dass User auf Schule zugreifen darf

    Args:
        required_school_id: Schul-ID die benötigt wird

    Returns:
        Dependency Function
    """

    async def _verify(current_user: dict = Depends(get_current_user)):
        if current_user['school_id'] != required_school_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Access to this school denied'
            )
        return current_user

    return _verify


# ============================================================================
# Dependency: Require Role
# ============================================================================

def require_role(required_role: str):
    """
    Dependency Factory - Verifiziert User-Rolle

    Args:
        required_role: Benötigte Rolle (z.B. 'admin')

    Returns:
        Dependency Function
    """

    async def _verify(current_user: dict = Depends(get_current_user)):
        if current_user['role'] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Role {required_role} required'
            )
        return current_user

    return _verify
