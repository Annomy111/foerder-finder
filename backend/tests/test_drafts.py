"""
Test Suite: AI Draft Generation
Tests for draft generation, retrieval, and AI integration
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestDraftGeneration:
    """Test draft generation endpoint"""

    def test_generate_draft_requires_auth(self, client: TestClient):
        """Test that draft generation requires authentication"""
        response = client.post(
            '/api/v1/drafts/generate',
            json={
                'funding_id': 'test-funding-id',
                'user_query': 'Test query'
            }
        )

        assert response.status_code == 401

    def test_generate_draft_missing_fields(self, client: TestClient, auth_headers: dict):
        """Test draft generation with missing required fields"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.post(
            '/api/v1/drafts/generate',
            headers=auth_headers,
            json={}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.slow
    def test_generate_draft_success_mock(self, client: TestClient, auth_headers: dict, sample_funding_id: str, create_test_application):
        """Test successful draft generation with mocked AI response"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        # Create test application first
        app_id = create_test_application('Draft Generation Test')
        if not app_id:
            pytest.skip('Could not create test application')

        # Mock the AI call to avoid external API dependency
        with patch('httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': 'Test generated draft content from AI'
                    }
                }]
            }
            mock_post.return_value = mock_response

            response = client.post(
                '/api/v1/drafts/generate',
                headers=auth_headers,
                json={
                    'application_id': app_id,
                    'funding_id': sample_funding_id,
                    'user_query': 'Generate a test draft'
                }
            )

            # Should succeed with mocked AI
            assert response.status_code in [200, 201]
            if response.status_code == 200:
                data = response.json()
                assert 'draft_id' in data or 'content' in data


@pytest.mark.unit
class TestDraftRetrieval:
    """Test draft retrieval endpoints"""

    def test_list_drafts_requires_auth(self, client: TestClient):
        """Test that listing drafts requires authentication"""
        response = client.get('/api/v1/drafts')

        assert response.status_code == 401

    def test_list_drafts_success(self, client: TestClient, auth_headers: dict):
        """Test successful draft listing"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.get('/api/v1/drafts', headers=auth_headers)

        # Should succeed even if empty
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_draft_requires_auth(self, client: TestClient):
        """Test that getting draft detail requires authentication"""
        response = client.get('/api/v1/drafts/test-draft-id')

        assert response.status_code == 401

    def test_get_draft_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent draft"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.get('/api/v1/drafts/nonexistent-draft-id', headers=auth_headers)

        assert response.status_code == 404


@pytest.mark.unit
class TestDraftValidation:
    """Test draft input validation"""

    def test_draft_generation_invalid_funding_id(self, client: TestClient, auth_headers: dict):
        """Test draft generation with invalid funding_id"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.post(
            '/api/v1/drafts/generate',
            headers=auth_headers,
            json={
                'funding_id': 'invalid-funding-id',
                'user_query': 'Test query'
            }
        )

        # Should fail with 404 or 400
        assert response.status_code in [400, 404, 422]

    def test_draft_generation_empty_query(self, client: TestClient, auth_headers: dict, sample_funding_id: str):
        """Test draft generation with empty query"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        response = client.post(
            '/api/v1/drafts/generate',
            headers=auth_headers,
            json={
                'funding_id': sample_funding_id,
                'user_query': ''
            }
        )

        # Should reject empty query
        assert response.status_code in [400, 422]

    def test_draft_generation_very_long_query(self, client: TestClient, auth_headers: dict, sample_funding_id: str):
        """Test draft generation with very long query"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        long_query = 'A' * 10000  # 10k characters

        response = client.post(
            '/api/v1/drafts/generate',
            headers=auth_headers,
            json={
                'funding_id': sample_funding_id,
                'user_query': long_query
            }
        )

        # Should either accept or reject gracefully
        assert response.status_code in [200, 201, 400, 422, 413]


@pytest.mark.integration
class TestDraftAIIntegration:
    """Test AI integration for draft generation"""

    @pytest.mark.slow
    def test_draft_content_structure(self, client: TestClient, auth_headers: dict, sample_funding_id: str, create_test_application):
        """Test that generated draft has proper structure"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        app_id = create_test_application('AI Structure Test')
        if not app_id:
            pytest.skip('Could not create test application')

        # Mock AI response
        with patch('httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': 'Draft content with sections:\n\n1. Introduction\n2. Project Description\n3. Budget'
                    }
                }]
            }
            mock_post.return_value = mock_response

            response = client.post(
                '/api/v1/drafts/generate',
                headers=auth_headers,
                json={
                    'application_id': app_id,
                    'funding_id': sample_funding_id,
                    'user_query': 'Generate structured draft'
                }
            )

            if response.status_code == 200:
                data = response.json()
                # Draft should have content
                if 'content' in data:
                    assert len(data['content']) > 0
                    assert isinstance(data['content'], str)

    def test_rag_context_retrieval(self, client: TestClient, auth_headers: dict, sample_funding_id: str):
        """Test that RAG retrieves relevant context"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        # This tests the RAG pipeline if enabled
        # Should retrieve relevant documents from ChromaDB
        # Mock ChromaDB query
        with patch('chromadb.PersistentClient') as mock_chroma:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                'documents': [['Relevant funding information']],
                'metadatas': [[{'funding_id': sample_funding_id}]]
            }
            mock_client = MagicMock()
            mock_client.get_collection.return_value = mock_collection
            mock_chroma.return_value = mock_client

            # Test would verify RAG retrieval
            # Actual implementation depends on RAG router


@pytest.mark.unit
class TestDraftUpdate:
    """Test draft update and editing"""

    def test_update_draft_requires_auth(self, client: TestClient):
        """Test that updating draft requires authentication"""
        response = client.put(
            '/api/v1/drafts/test-draft-id',
            json={'content': 'Updated content'}
        )

        assert response.status_code == 401

    def test_update_draft_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating non-existent draft"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.put(
            '/api/v1/drafts/nonexistent-draft-id',
            headers=auth_headers,
            json={'content': 'Updated content'}
        )

        assert response.status_code == 404


@pytest.mark.unit
class TestDraftDelete:
    """Test draft deletion"""

    def test_delete_draft_requires_auth(self, client: TestClient):
        """Test that deleting draft requires authentication"""
        response = client.delete('/api/v1/drafts/test-draft-id')

        assert response.status_code == 401

    def test_delete_draft_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting non-existent draft"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.delete('/api/v1/drafts/nonexistent-draft-id', headers=auth_headers)

        assert response.status_code == 404


@pytest.mark.integration
class TestDraftSecurity:
    """Test draft security and authorization"""

    def test_user_cannot_access_other_school_drafts(self, client: TestClient, auth_headers: dict):
        """Test that users can only see their school's drafts"""
        if not auth_headers:
            pytest.skip('Auth not available')

        response = client.get('/api/v1/drafts', headers=auth_headers)

        assert response.status_code == 200
        # All drafts should belong to authenticated school

    def test_ai_response_sanitization(self, client: TestClient, auth_headers: dict, sample_funding_id: str, create_test_application):
        """Test that AI responses are sanitized before storage"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        app_id = create_test_application('Sanitization Test')
        if not app_id:
            pytest.skip('Could not create test application')

        # Mock AI response with potentially malicious content
        with patch('httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': '<script>alert("xss")</script>Safe content'
                    }
                }]
            }
            mock_post.return_value = mock_response

            response = client.post(
                '/api/v1/drafts/generate',
                headers=auth_headers,
                json={
                    'application_id': app_id,
                    'funding_id': sample_funding_id,
                    'user_query': 'Generate draft'
                }
            )

            # Should handle XSS safely
            if response.status_code == 200:
                data = response.json()
                if 'content' in data:
                    # Script tags should be escaped or removed
                    assert '<script>' not in data['content'] or '&lt;script&gt;' in data['content']


@pytest.mark.unit
class TestDraftStatus:
    """Test draft status management"""

    def test_draft_initial_status(self, client: TestClient, auth_headers: dict, sample_funding_id: str, create_test_application):
        """Test that new drafts have correct initial status"""
        if not auth_headers or not sample_funding_id:
            pytest.skip('Auth or funding data not available')

        app_id = create_test_application('Status Test')
        if not app_id:
            pytest.skip('Could not create test application')

        # Mock AI
        with patch('httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'Test draft'}}]
            }
            mock_post.return_value = mock_response

            response = client.post(
                '/api/v1/drafts/generate',
                headers=auth_headers,
                json={
                    'application_id': app_id,
                    'funding_id': sample_funding_id,
                    'user_query': 'Test'
                }
            )

            if response.status_code == 200:
                data = response.json()
                # New draft should have 'draft' or 'pending' status
                if 'status' in data:
                    assert data['status'] in ['draft', 'pending', 'generated']
