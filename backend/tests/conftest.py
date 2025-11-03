"""
pytest Configuration & Fixtures
Core test infrastructure for Förder-Finder Backend
"""

import os
import sys
import sqlite3
import shutil
from typing import Generator
import pytest
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment to test mode BEFORE importing app
os.environ['USE_SQLITE'] = 'true'
os.environ['USE_ADVANCED_RAG'] = 'false'
os.environ['CORS_ORIGINS'] = '["http://localhost:3000"]'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-do-not-use-in-production'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['JWT_ACCESS_TOKEN_EXPIRE_MINUTES'] = '60'

from api.main import app
from utils.database_sqlite import get_db_manager, init_sqlite_schema


@pytest.fixture(scope='session')
def test_db_path() -> str:
    """Returns the path to the test database"""
    return 'test_database.db'


@pytest.fixture(scope='session')
def test_db(test_db_path: str) -> Generator[str, None, None]:
    """
    Create test database for the entire test session
    Copies schema and seed data from dev_database.db
    """
    # Remove old test DB if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # Copy dev database as template
    if os.path.exists('dev_database.db'):
        shutil.copy('dev_database.db', test_db_path)
        print(f'\n[TEST DB] Copied dev_database.db to {test_db_path}')
    else:
        # Create fresh DB with schema
        print(f'\n[TEST DB] Creating fresh test database at {test_db_path}')
        # Temporarily override db path
        old_db_path = get_db_manager().db_path
        get_db_manager().db_path = test_db_path
        init_sqlite_schema()
        get_db_manager().db_path = old_db_path

    yield test_db_path

    # Cleanup after all tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f'\n[TEST DB] Cleaned up {test_db_path}')


@pytest.fixture(scope='function')
def db_cursor(test_db, test_db_path):
    """
    Provides a fresh database cursor for each test
    Automatically rolls back changes after test
    """
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    yield cursor

    conn.rollback()
    cursor.close()
    conn.close()


@pytest.fixture(scope='module')
def client() -> TestClient:
    """
    FastAPI TestClient for making requests
    Shared across all tests in a module
    """
    # Override database path for tests
    from utils import database_sqlite
    database_sqlite._db_manager = database_sqlite.SQLiteDatabaseManager('test_database.db')

    # TestClient expects positional argument in starlette 0.27.0
    test_client = TestClient(app)
    yield test_client
    # Proper cleanup
    try:
        test_client.close()
    except:
        pass


@pytest.fixture(scope='module')
def auth_token(client: TestClient) -> str:
    """
    Get valid JWT token for authenticated requests
    Uses the first admin user from test database
    """
    # Try to login with default admin credentials
    response = client.post(
        '/api/v1/auth/login',
        json={
            'email': 'admin@gs-musterberg.de',
            'password': 'test1234'
        }
    )

    if response.status_code != 200:
        # If default admin doesn't exist, create one
        print('[TEST AUTH] Default admin not found, this is expected for fresh DB')
        return None

    data = response.json()
    return data.get('access_token')


@pytest.fixture(scope='module')
def auth_headers(auth_token: str) -> dict:
    """
    Authorization headers for authenticated requests
    """
    if auth_token is None:
        return {}
    return {'Authorization': f'Bearer {auth_token}'}


@pytest.fixture(scope='function')
def sample_funding_id(db_cursor) -> str:
    """
    Get a sample funding_id from the database for testing
    """
    db_cursor.execute('SELECT funding_id FROM FUNDING_OPPORTUNITIES LIMIT 1')
    row = db_cursor.fetchone()
    if row:
        return row['funding_id']
    return None


@pytest.fixture(scope='function')
def sample_school_id(db_cursor) -> str:
    """
    Get a sample school_id from the database for testing
    """
    db_cursor.execute('SELECT school_id FROM SCHOOLS LIMIT 1')
    row = db_cursor.fetchone()
    if row:
        return row['school_id']
    return None


@pytest.fixture(scope='function')
def create_test_application(client: TestClient, auth_headers: dict, sample_funding_id: str):
    """
    Factory fixture to create test applications
    Returns a function that creates an application and returns its ID
    """
    created_ids = []

    def _create_application(title: str = 'Test Application', **kwargs):
        payload = {
            'funding_id': sample_funding_id or 'test-funding-id',
            'title': title,
            'projektbeschreibung': kwargs.get('projektbeschreibung', 'Test project description'),
            'zielgruppe': kwargs.get('zielgruppe', 'Grundschüler Klasse 3-4'),
            'budget_details': kwargs.get('budget_details', 'Budget: 5000 EUR'),
        }

        response = client.post(
            '/api/v1/applications',
            headers=auth_headers,
            json=payload
        )

        if response.status_code == 200 or response.status_code == 201:
            app_id = response.json().get('application_id')
            created_ids.append(app_id)
            return app_id
        return None

    yield _create_application

    # Cleanup: Delete all created applications
    for app_id in created_ids:
        try:
            client.delete(f'/api/v1/applications/{app_id}', headers=auth_headers)
        except:
            pass


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        'markers', 'slow: marks tests as slow (deselect with \'-m "not slow"\')'
    )
    config.addinivalue_line(
        'markers', 'integration: marks tests as integration tests'
    )
    config.addinivalue_line(
        'markers', 'unit: marks tests as unit tests'
    )
