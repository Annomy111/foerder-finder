"""
Oracle Database Connection Manager
Verwaltet Verbindungen zur Oracle Autonomous Database
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional

import cx_Oracle
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """Manager für Oracle DB Verbindungen"""

    def __init__(self):
        """Initialisiert den Database Manager"""
        self.user = os.getenv('ORACLE_USER')
        self.password = os.getenv('ORACLE_PASSWORD')
        self.dsn = os.getenv('ORACLE_DSN')
        self.wallet_path = os.getenv('ORACLE_WALLET_PATH')

        if not all([self.user, self.password, self.dsn]):
            raise ValueError('Oracle DB Credentials nicht vollständig in .env')

        # Konfiguriere Oracle Wallet für mTLS
        if self.wallet_path and os.path.exists(self.wallet_path):
            cx_Oracle.init_oracle_client(config_dir=self.wallet_path)

    def get_connection_string(self) -> str:
        """
        Erstellt Connection String für cx_Oracle

        Returns:
            Connection String
        """
        return f'{self.user}/{self.password}@{self.dsn}'

    def get_connection(self) -> cx_Oracle.Connection:
        """
        Erstellt eine neue DB-Verbindung

        Returns:
            Oracle Connection Objekt

        Raises:
            cx_Oracle.Error: Bei Verbindungsfehlern
        """
        try:
            connection = cx_Oracle.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn,
                encoding='UTF-8'
            )
            return connection
        except cx_Oracle.Error as e:
            raise Exception(f'Fehler beim Verbinden mit Oracle DB: {str(e)}')

    @contextmanager
    def get_cursor(self) -> Generator[cx_Oracle.Cursor, None, None]:
        """
        Context Manager für DB-Cursor (auto-commit bei Erfolg)

        Yields:
            Oracle Cursor Objekt

        Example:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT * FROM schools")
                results = cursor.fetchall()
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            connection.close()

    @contextmanager
    def get_connection_context(self) -> Generator[cx_Oracle.Connection, None, None]:
        """
        Context Manager für DB-Connection (manuelles Commit)

        Yields:
            Oracle Connection Objekt

        Example:
            with db_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT ...")
                conn.commit()
        """
        connection = self.get_connection()
        try:
            yield connection
        finally:
            connection.close()


# Singleton-Instanz
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    Gibt die Singleton-Instanz des Database Managers zurück

    Returns:
        DatabaseManager Instanz
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


# Convenience-Funktionen
def get_db_connection() -> cx_Oracle.Connection:
    """Erstellt eine neue DB-Verbindung"""
    return get_db_manager().get_connection()


@contextmanager
def get_db_cursor() -> Generator[cx_Oracle.Cursor, None, None]:
    """Context Manager für DB-Cursor"""
    with get_db_manager().get_cursor() as cursor:
        yield cursor


def execute_query(query: str, params: Optional[dict] = None) -> list:
    """
    Führt eine SELECT-Query aus und gibt alle Ergebnisse zurück

    Args:
        query: SQL Query
        params: Query-Parameter (dict)

    Returns:
        Liste von Tupeln mit Ergebnissen
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or {})
        return cursor.fetchall()


def execute_insert(query: str, params: dict) -> None:
    """
    Führt eine INSERT-Query aus

    Args:
        query: SQL Query
        params: Query-Parameter (dict)
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params)


def execute_update(query: str, params: dict) -> int:
    """
    Führt eine UPDATE-Query aus

    Args:
        query: SQL Query
        params: Query-Parameter (dict)

    Returns:
        Anzahl betroffener Zeilen
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.rowcount
