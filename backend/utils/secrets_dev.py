"""
Development Secrets Manager
Fallback for local development without OCI Vault access
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Development JWT Secret (NEVER use in production!)
DEV_JWT_SECRET = os.getenv('JWT_SECRET_DEV', 'dev_secret_key_change_in_production_123456789')


def get_jwt_secret() -> str:
    """Get JWT secret key for development"""
    return DEV_JWT_SECRET


def get_deepseek_api_key() -> str:
    """Get DeepSeek API key from .env"""
    key = os.getenv('DEEPSEEK_API_KEY')
    if not key:
        raise ValueError('DEEPSEEK_API_KEY not set in .env')
    return key


def get_brightdata_proxy() -> str:
    """Get Bright Data proxy URL from .env"""
    proxy = os.getenv('BRIGHTDATA_PROXY_URL')
    if not proxy:
        raise ValueError('BRIGHTDATA_PROXY_URL not set in .env')
    return proxy
