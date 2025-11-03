"""
SQLite Database Manager (Dev Only)
Development fallback when Oracle DB is not available
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional
from dotenv import load_dotenv

load_dotenv()


class SQLiteDatabaseManager:
    """Manager für SQLite DB Verbindungen (Development)"""

    def __init__(self, db_path: str = 'dev_database.db'):
        """Initialisiert den Database Manager"""
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """
        Erstellt eine neue DB-Verbindung

        Returns:
            SQLite Connection Objekt
        """
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row  # Ermöglicht dict-like access
        return connection

    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Context Manager für DB-Cursor (auto-commit bei Erfolg)

        Yields:
            SQLite Cursor Objekt
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
    def get_connection_context(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context Manager für DB-Connection (manuelles Commit)

        Yields:
            SQLite Connection Objekt
        """
        connection = self.get_connection()
        try:
            yield connection
        finally:
            connection.close()


# Singleton-Instanz
_db_manager: Optional[SQLiteDatabaseManager] = None


def get_db_manager() -> SQLiteDatabaseManager:
    """
    Gibt die Singleton-Instanz des Database Managers zurück

    Returns:
        SQLiteDatabaseManager Instanz
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = SQLiteDatabaseManager()
    return _db_manager


# Convenience-Funktionen
def get_db_connection() -> sqlite3.Connection:
    """Erstellt eine neue DB-Verbindung"""
    return get_db_manager().get_connection()


@contextmanager
def get_db_cursor() -> Generator[sqlite3.Cursor, None, None]:
    """Context Manager für DB-Cursor"""
    with get_db_manager().get_cursor() as cursor:
        yield cursor


def execute_query(query: str, params: Optional[dict] = None) -> list:
    """
    Führt eine SELECT-Query aus und gibt alle Ergebnisse zurück

    Args:
        query: SQL Query (SQLite-kompatibel!)
        params: Query-Parameter (dict oder tuple)

    Returns:
        Liste von Rows
    """
    with get_db_cursor() as cursor:
        if params:
            # SQLite uses ? placeholders, not :name
            cursor.execute(query, params if isinstance(params, tuple) else tuple(params.values()))
        else:
            cursor.execute(query)
        return cursor.fetchall()


def execute_insert(query: str, params: dict) -> None:
    """
    Führt eine INSERT-Query aus

    Args:
        query: SQL Query
        params: Query-Parameter (dict)
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, tuple(params.values()))


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
        cursor.execute(query, tuple(params.values()))
        return cursor.rowcount


def init_sqlite_schema():
    """
    Initialisiert SQLite Schema für Entwicklung
    """
    with get_db_cursor() as cursor:
        # SCHOOLS Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SCHOOLS (
                school_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT,
                postal_code TEXT,
                city TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # USERS Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS USERS (
                user_id TEXT PRIMARY KEY,
                school_id TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                role TEXT DEFAULT 'lehrkraft',
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES SCHOOLS(school_id)
            )
        ''')

        # FUNDING_OPPORTUNITIES Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS FUNDING_OPPORTUNITIES (
                funding_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                provider TEXT,
                description TEXT,
                eligibility TEXT,
                application_deadline DATE,
                deadline DATE,
                funding_amount_min REAL,
                min_funding_amount REAL,
                funding_amount_max REAL,
                max_funding_amount REAL,
                categories TEXT,
                target_groups TEXT,
                region TEXT,
                funding_area TEXT,
                url TEXT,
                source_url TEXT,
                cleaned_text TEXT,
                metadata_json TEXT,
                last_scraped TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # APPLICATIONS Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS APPLICATIONS (
                application_id TEXT PRIMARY KEY,
                school_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                funding_id TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                draft_text TEXT,
                final_text TEXT,
                submitted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES SCHOOLS(school_id),
                FOREIGN KEY (user_id) REFERENCES USERS(user_id),
                FOREIGN KEY (funding_id) REFERENCES FUNDING_OPPORTUNITIES(funding_id)
            )
        ''')

        # APPLICATION_DRAFTS Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS APPLICATION_DRAFTS (
                draft_id TEXT PRIMARY KEY,
                application_id TEXT NOT NULL,
                draft_text TEXT NOT NULL,
                ai_model TEXT,
                prompt_used TEXT,
                user_feedback TEXT,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES APPLICATIONS(application_id)
            )
        ''')

    print("✅ SQLite Schema initialized")


def seed_demo_data():
    """
    Fügt Demo-Daten für Entwicklung ein
    """
    import uuid
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def generate_id():
        return str(uuid.uuid4()).replace('-', '').upper()

    # Password: test1234
    password_hash = pwd_context.hash('test1234')

    with get_db_cursor() as cursor:
        # Demo School
        school_id = generate_id()
        cursor.execute('''
            INSERT OR IGNORE INTO SCHOOLS (
                school_id, name, address, postal_code, city,
                contact_email, contact_phone, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            school_id,
            'Grundschule Musterberg',
            'Musterstraße 123',
            '10115',
            'Berlin',
            'info@gs-musterberg.de',
            '+49 30 12345678',
            1
        ))

        # Demo User (Admin)
        user_id = generate_id()
        cursor.execute('''
            INSERT OR IGNORE INTO USERS (
                user_id, school_id, email, password_hash,
                first_name, last_name, role, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            school_id,
            'admin@gs-musterberg.de',
            password_hash,
            'Max',
            'Mustermann',
            'admin',
            1
        ))

        # Demo Funding
        funding_id = generate_id()
        cursor.execute('''
            INSERT OR IGNORE INTO FUNDING_OPPORTUNITIES (
                funding_id, title, provider, description,
                application_deadline, funding_amount_min, funding_amount_max,
                categories, target_groups, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            funding_id,
            'Digitale Bildung 2025',
            'Bundesministerium für Bildung',
            'Förderung für digitale Lernmittel und Infrastruktur',
            '2025-12-31',
            5000.0,
            50000.0,
            'Digitalisierung,Bildung',
            'Grundschulen',
            'https://example.com/foerderung'
        ))

    print(f"✅ Demo data seeded")
    print(f"   School ID: {school_id}")
    print(f"   User ID: {user_id}")
    print(f"   Login: admin@gs-musterberg.de / test1234")
