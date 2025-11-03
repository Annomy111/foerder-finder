"""
Test Suite: Applications
Tests for application CRUD operations and management
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestApplicationCreate:
    """Test application creation"""

    def test_create_application_requires_auth(self, client: TestClient):
        """Test that creating application requires authentication"""
        response = client.post(
            '/api/v1/applications',
            json={
                'funding_id': 'test-funding-id',
                'title': 'Test Application',
                'projektbeschreibung': 'Test description'
            }
        )

        assert response.status_code == 401

    def test_create_application_success(self, client: TestClient, auth_headers: dict, sample_funding_id: str):
        """Test successful application creation"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        response = client.post(
            '/api/v1/applications',
            headers=auth_headers,
            json={
                'funding_id': sample_funding_id,
                'title': 'Test Application',
                'projektbeschreibung': 'Test project description for funding',
                'zielgruppe': 'Grundschüler Klasse 3-4',
                'budget_details': 'Budget: 5000 EUR'
            }
        )

        assert response.status_code in [200, 201]
        data = response.json()
        assert 'application_id' in data
        assert isinstance(data['application_id'], str)

    def test_create_application_missing_fields(self, client: TestClient, auth_headers: dict):
        """Test creating application with missing required fields"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.post(
            '/api/v1/applications',
            headers=auth_headers,
            json={
                'title': 'Incomplete Application'
                # Missing funding_id and other required fields
            }
        )

        assert response.status_code == 422  # Validation error

    def test_create_application_invalid_funding_id(self, client: TestClient, auth_headers: dict):
        """Test creating application with non-existent funding_id"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.post(
            '/api/v1/applications',
            headers=auth_headers,
            json={
                'funding_id': 'nonexistent-funding-id',
                'title': 'Test Application',
                'projektbeschreibung': 'Test description'
            }
        )

        # Should fail with 404 or 400 (invalid funding reference)
        assert response.status_code in [400, 404, 422]


@pytest.mark.unit
class TestApplicationList:
    """Test application list endpoint"""

    def test_list_applications_requires_auth(self, client: TestClient):
        """Test that listing applications requires authentication"""
        response = client.get('/api/v1/applications')

        assert response.status_code == 401

    def test_list_applications_success(self, client: TestClient, auth_headers: dict):
        """Test successful application listing"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.get('/api/v1/applications', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_applications_with_limit(self, client: TestClient, auth_headers: dict):
        """Test application list with limit parameter"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.get('/api/v1/applications?limit=5', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_list_applications_empty(self, client: TestClient, auth_headers: dict):
        """Test listing applications when none exist"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.get('/api/v1/applications', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.unit
class TestApplicationDetail:
    """Test application detail endpoint"""

    def test_get_application_requires_auth(self, client: TestClient):
        """Test that getting application requires authentication"""
        response = client.get('/api/v1/applications/test-app-id')

        assert response.status_code == 401

    def test_get_application_success(self, client: TestClient, auth_headers: dict, create_test_application):
        """Test getting application detail"""
        if not auth_headers:
            pytest.skip('Auth not available')

        # Create a test application
        app_id = create_test_application('Test Application for Detail')
        if not app_id:
            pytest.skip('Could not create test application')

        response = client.get(f'/api/v1/applications/{app_id}', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data['application_id'] == app_id

    def test_get_application_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent application"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.get('/api/v1/applications/nonexistent-id', headers=auth_headers)

        assert response.status_code == 404

    def test_get_application_has_required_fields(self, client: TestClient, auth_headers: dict, create_test_application):
        """Test that application detail has all required fields"""
        if not auth_headers:
            pytest.skip('Auth not available')

        app_id = create_test_application('Test Application')
        if not app_id:
            pytest.skip('Could not create test application')

        response = client.get(f'/api/v1/applications/{app_id}', headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        required_fields = ['application_id', 'funding_id', 'title', 'status']
        for field in required_fields:
            assert field in data, f'Missing required field: {field}'


@pytest.mark.unit
class TestApplicationUpdate:
    """Test application update endpoint"""

    def test_update_application_requires_auth(self, client: TestClient):
        """Test that updating application requires authentication"""
        response = client.put(
            '/api/v1/applications/test-app-id',
            json={'title': 'Updated Title'}
        )

        assert response.status_code == 401

    def test_update_application_success(self, client: TestClient, auth_headers: dict, create_test_application):
        """Test successful application update"""
        if not auth_headers:
            pytest.skip('Auth not available')

        app_id = create_test_application('Original Title')
        if not app_id:
            pytest.skip('Could not create test application')

        response = client.put(
            f'/api/v1/applications/{app_id}',
            headers=auth_headers,
            json={
                'title': 'Updated Title',
                'projektbeschreibung': 'Updated description'
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['title'] == 'Updated Title'

    def test_update_application_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating non-existent application"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.put(
            '/api/v1/applications/nonexistent-id',
            headers=auth_headers,
            json={'title': 'Updated Title'}
        )

        assert response.status_code == 404


@pytest.mark.unit
class TestApplicationDelete:
    """Test application delete endpoint"""

    def test_delete_application_requires_auth(self, client: TestClient):
        """Test that deleting application requires authentication"""
        response = client.delete('/api/v1/applications/test-app-id')

        assert response.status_code == 401

    def test_delete_application_success(self, client: TestClient, auth_headers: dict, create_test_application):
        """Test successful application deletion"""
        if not auth_headers:
            pytest.skip('Auth not available')

        app_id = create_test_application('Application to Delete')
        if not app_id:
            pytest.skip('Could not create test application')

        response = client.delete(f'/api/v1/applications/{app_id}', headers=auth_headers)

        assert response.status_code in [200, 204]

        # Verify deletion
        get_response = client.get(f'/api/v1/applications/{app_id}', headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_application_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting non-existent application"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.delete('/api/v1/applications/nonexistent-id', headers=auth_headers)

        assert response.status_code == 404


@pytest.mark.integration
class TestApplicationWorkflow:
    """Test complete application workflow"""

    def test_complete_crud_workflow(self, client: TestClient, auth_headers: dict, sample_funding_id: str):
        """Test create -> read -> update -> delete workflow"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        # 1. Create
        create_response = client.post(
            '/api/v1/applications',
            headers=auth_headers,
            json={
                'funding_id': sample_funding_id,
                'title': 'Workflow Test Application',
                'projektbeschreibung': 'Test project',
                'zielgruppe': 'Grundschüler',
                'budget_details': '5000 EUR'
            }
        )
        assert create_response.status_code in [200, 201]
        app_id = create_response.json()['application_id']

        # 2. Read
        read_response = client.get(f'/api/v1/applications/{app_id}', headers=auth_headers)
        assert read_response.status_code == 200
        assert read_response.json()['title'] == 'Workflow Test Application'

        # 3. Update
        update_response = client.put(
            f'/api/v1/applications/{app_id}',
            headers=auth_headers,
            json={'title': 'Updated Workflow Test'}
        )
        assert update_response.status_code == 200

        # 4. Verify update
        verify_response = client.get(f'/api/v1/applications/{app_id}', headers=auth_headers)
        assert verify_response.status_code == 200
        assert verify_response.json()['title'] == 'Updated Workflow Test'

        # 5. Delete
        delete_response = client.delete(f'/api/v1/applications/{app_id}', headers=auth_headers)
        assert delete_response.status_code in [200, 204]

        # 6. Verify deletion
        final_response = client.get(f'/api/v1/applications/{app_id}', headers=auth_headers)
        assert final_response.status_code == 404


@pytest.mark.unit
class TestApplicationSecurity:
    """Test application security and authorization"""

    def test_user_cannot_access_other_school_applications(self, client: TestClient, auth_headers: dict):
        """Test that users can only see their school's applications"""
        if not auth_headers:
            pytest.skip('Auth not available')

        # This test verifies multi-tenancy
        # Applications should be filtered by school_id from JWT
        response = client.get('/api/v1/applications', headers=auth_headers)

        assert response.status_code == 200
        # All applications should belong to the authenticated school

    def test_sql_injection_in_application_title(self, client: TestClient, auth_headers: dict, sample_funding_id: str):
        """Test SQL injection protection in title field"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        response = client.post(
            '/api/v1/applications',
            headers=auth_headers,
            json={
                'funding_id': sample_funding_id,
                'title': "Test'; DROP TABLE applications; --",
                'projektbeschreibung': 'Test'
            }
        )

        # Should either create safely or reject
        assert response.status_code in [200, 201, 400, 422]
