"""
OCI Vault Secrets Manager
Zugriff auf Secrets aus dem Oracle Cloud Infrastructure Vault
"""

import base64
import os
from functools import lru_cache
from typing import Optional

import oci
from oci.config import from_file
from oci.secrets import SecretsClient


class OCISecretsManager:
    """Manager für OCI Vault Secrets"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialisiert den OCI Secrets Manager

        Args:
            config_path: Pfad zur OCI Config-Datei (default: ~/.oci/config)
        """
        self.config_path = config_path or os.path.expanduser('~/.oci/config')
        self.config = from_file(self.config_path)
        self.secrets_client = SecretsClient(self.config)

    @lru_cache(maxsize=32)
    def get_secret(self, secret_id: str) -> str:
        """
        Holt ein Secret aus dem OCI Vault (mit Caching)

        Args:
            secret_id: OCID des Secrets

        Returns:
            Dekodierter Secret-Wert als String

        Raises:
            Exception: Bei Fehlern beim Abrufen des Secrets
        """
        try:
            response = self.secrets_client.get_secret_bundle(secret_id)
            secret_content = response.data.secret_bundle_content.content
            decoded_secret = base64.b64decode(secret_content).decode('utf-8')
            return decoded_secret
        except Exception as e:
            raise Exception(f'Fehler beim Abrufen des Secrets {secret_id}: {str(e)}')

    def get_deepseek_api_key(self) -> str:
        """Holt den DeepSeek API Key"""
        secret_id = os.getenv('SECRET_DEEPSEEK_API_KEY')
        if not secret_id:
            raise ValueError('SECRET_DEEPSEEK_API_KEY nicht in .env definiert')
        return self.get_secret(secret_id)

    def get_brightdata_proxy(self) -> str:
        """Holt die Bright Data Proxy Connection String"""
        secret_id = os.getenv('SECRET_BRIGHTDATA_PROXY')
        if not secret_id:
            raise ValueError('SECRET_BRIGHTDATA_PROXY nicht in .env definiert')
        return self.get_secret(secret_id)

    def get_jwt_secret(self) -> str:
        """Holt den JWT Secret Key"""
        secret_id = os.getenv('SECRET_JWT_SECRET')
        if not secret_id:
            raise ValueError('SECRET_JWT_SECRET nicht in .env definiert')
        return self.get_secret(secret_id)


# Singleton-Instanz
_secrets_manager: Optional[OCISecretsManager] = None


def get_secrets_manager() -> OCISecretsManager:
    """
    Gibt die Singleton-Instanz des Secrets Managers zurück

    Returns:
        OCISecretsManager Instanz
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = OCISecretsManager()
    return _secrets_manager


# Convenience-Funktionen
def get_deepseek_api_key() -> str:
    """Holt den DeepSeek API Key aus dem OCI Vault"""
    return get_secrets_manager().get_deepseek_api_key()


def get_brightdata_proxy() -> str:
    """Holt die Bright Data Proxy URL aus dem OCI Vault"""
    return get_secrets_manager().get_brightdata_proxy()


def get_jwt_secret() -> str:
    """Holt den JWT Secret Key aus dem OCI Vault"""
    return get_secrets_manager().get_jwt_secret()
