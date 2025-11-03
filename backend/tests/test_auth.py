"""
Test Suite: Authentication
Tests for login, JWT tokens, and user management
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestAuthLogin:
    """Test authentication login endpoint"""

    def test_login_success(self, client: TestClient):
        """Test successful login with valid credentials"""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': 'admin@gs-musterberg.de',
                'password': 'test1234'
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'
        assert isinstance(data['access_token'], str)
        assert len(data['access_token']) > 0

    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email"""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': 'nonexistent@example.com',
                'password': 'test1234'
            }
        )

        assert response.status_code == 401
        assert 'detail' in response.json()

    def test_login_invalid_password(self, client: TestClient):
        """Test login with wrong password"""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': 'admin@gs-musterberg.de',
                'password': 'wrongpassword'
            }
        )

        assert response.status_code == 401
        assert 'detail' in response.json()

    def test_login_missing_email(self, client: TestClient):
        """Test login with missing email field"""
        response = client.post(
            '/api/v1/auth/login',
            json={'password': 'test1234'}
        )

        assert response.status_code == 422  # Validation error

    def test_login_missing_password(self, client: TestClient):
        """Test login with missing password field"""
        response = client.post(
            '/api/v1/auth/login',
            json={'email': 'admin@gs-musterberg.de'}
        )

        assert response.status_code == 422  # Validation error

    def test_login_empty_credentials(self, client: TestClient):
        """Test login with empty credentials"""
        response = client.post(
            '/api/v1/auth/login',
            json={'email': '', 'password': ''}
        )

        assert response.status_code in [401, 422]

    def test_login_invalid_json(self, client: TestClient):
        """Test login with malformed JSON"""
        response = client.post(
            '/api/v1/auth/login',
            data='invalid json',
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 422


@pytest.mark.unit
class TestAuthToken:
    """Test JWT token functionality"""

    def test_token_is_jwt_format(self, client: TestClient):
        """Test that returned token is valid JWT format"""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': 'admin@gs-musterberg.de',
                'password': 'test1234'
            }
        )

        token = response.json()['access_token']
        # JWT has 3 parts separated by dots
        parts = token.split('.')
        assert len(parts) == 3

    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token"""
        response = client.get('/api/v1/applications')

        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            '/api/v1/applications',
            headers={'Authorization': 'Bearer invalid-token-123'}
        )

        assert response.status_code == 401

    def test_protected_endpoint_with_valid_token(self, client: TestClient, auth_headers: dict):
        """Test accessing protected endpoint with valid token"""
        if not auth_headers:
            pytest.skip('No auth token available')

        response = client.get('/api/v1/applications', headers=auth_headers)

        # Should return 200 (success) or 404 (not found) but not 401 (unauthorized)
        assert response.status_code in [200, 404]

    def test_token_with_bearer_prefix(self, client: TestClient):
        """Test that Authorization header requires Bearer prefix"""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': 'admin@gs-musterberg.de',
                'password': 'test1234'
            }
        )

        token = response.json()['access_token']

        # Test without Bearer prefix
        response = client.get(
            '/api/v1/applications',
            headers={'Authorization': token}
        )
        assert response.status_code == 401


@pytest.mark.unit
class TestAuthValidation:
    """Test input validation for authentication"""

    def test_email_format_validation(self, client: TestClient):
        """Test that email format is validated"""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': 'not-an-email',
                'password': 'test1234'
            }
        )

        # Should be 422 (validation error) or 401 (invalid credentials)
        assert response.status_code in [401, 422]

    def test_sql_injection_attempt(self, client: TestClient):
        """Test that SQL injection attempts are handled safely"""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': "admin@example.com' OR '1'='1",
                'password': "password' OR '1'='1"
            }
        )

        # Should not succeed - should be 401 or 422
        assert response.status_code in [401, 422]

    def test_xss_attempt_in_email(self, client: TestClient):
        """Test that XSS attempts are handled safely"""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': '<script>alert("xss")</script>@example.com',
                'password': 'test1234'
            }
        )

        assert response.status_code in [401, 422]
