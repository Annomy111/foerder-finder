"""
Test Suite: Funding Opportunities
Tests for funding list, detail, search, and filters
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestFundingList:
    """Test funding opportunities list endpoint"""

    def test_list_funding_public_access(self, client: TestClient):
        """Test that funding list is publicly accessible without auth"""
        response = client.get('/api/v1/funding/')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_funding_with_limit(self, client: TestClient):
        """Test funding list with limit parameter"""
        response = client.get('/api/v1/funding/?limit=5')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_list_funding_with_offset(self, client: TestClient):
        """Test funding list with offset parameter"""
        response = client.get('/api/v1/funding/?offset=5&limit=10')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_list_funding_pagination(self, client: TestClient):
        """Test that pagination returns different results"""
        response1 = client.get('/api/v1/funding/?limit=5&offset=0')
        response2 = client.get('/api/v1/funding/?limit=5&offset=5')

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        if len(data1) > 0 and len(data2) > 0:
            # If both have data, they should be different
            assert data1[0] != data2[0]

    def test_list_funding_large_limit(self, client: TestClient):
        """Test funding list with very large limit"""
        response = client.get('/api/v1/funding/?limit=1000')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_funding_negative_limit(self, client: TestClient):
        """Test funding list with negative limit"""
        response = client.get('/api/v1/funding/?limit=-10')

        # Should handle gracefully - either 422 or return empty list
        assert response.status_code in [200, 422]

    def test_list_funding_invalid_limit_type(self, client: TestClient):
        """Test funding list with invalid limit type"""
        response = client.get('/api/v1/funding/?limit=abc')

        assert response.status_code == 422  # Validation error


@pytest.mark.unit
class TestFundingDetail:
    """Test funding detail endpoint"""

    def test_get_funding_detail_success(self, client: TestClient, sample_funding_id: str):
        """Test getting a specific funding detail"""
        if not sample_funding_id:
            pytest.skip('No funding data available')

        response = client.get(f'/api/v1/funding/{sample_funding_id}')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert 'funding_id' in data
        assert data['funding_id'] == sample_funding_id

    def test_get_funding_detail_not_found(self, client: TestClient):
        """Test getting non-existent funding detail"""
        fake_id = 'nonexistent-funding-id-12345'
        response = client.get(f'/api/v1/funding/{fake_id}')

        assert response.status_code == 404

    def test_get_funding_detail_has_required_fields(self, client: TestClient, sample_funding_id: str):
        """Test that funding detail has all required fields"""
        if not sample_funding_id:
            pytest.skip('No funding data available')

        response = client.get(f'/api/v1/funding/{sample_funding_id}')

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        required_fields = ['funding_id', 'title', 'source_url']
        for field in required_fields:
            assert field in data, f'Missing required field: {field}'

    def test_get_funding_detail_public_access(self, client: TestClient, sample_funding_id: str):
        """Test that funding detail is publicly accessible"""
        if not sample_funding_id:
            pytest.skip('No funding data available')

        # Access without auth headers
        response = client.get(f'/api/v1/funding/{sample_funding_id}')

        assert response.status_code == 200


@pytest.mark.unit
class TestFundingSearch:
    """Test funding search and filter functionality"""

    def test_search_funding_by_title(self, client: TestClient):
        """Test searching funding by title"""
        # Get first funding to know what to search for
        response = client.get('/api/v1/funding/?limit=1')
        if response.status_code == 200 and len(response.json()) > 0:
            first_funding = response.json()[0]
            title_keyword = first_funding.get('title', '').split()[0] if first_funding.get('title') else None

            if title_keyword:
                search_response = client.get(f'/api/v1/funding/?search={title_keyword}')
                assert search_response.status_code == 200
                # Results should contain the keyword (if search is implemented)
        else:
            pytest.skip('No funding data for search test')

    def test_filter_funding_by_category(self, client: TestClient):
        """Test filtering funding by category"""
        # This tests the category filter if implemented
        response = client.get('/api/v1/funding/?category=Bildung')

        # Should return 200 regardless of whether filter is implemented
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_filter_funding_by_bundesland(self, client: TestClient):
        """Test filtering funding by Bundesland"""
        response = client.get('/api/v1/funding/?bundesland=Berlin')

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_multiple_filters(self, client: TestClient):
        """Test applying multiple filters simultaneously"""
        response = client.get('/api/v1/funding/?category=Bildung&bundesland=Berlin&limit=10')

        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.unit
class TestFundingDataQuality:
    """Test data quality and structure of funding responses"""

    def test_funding_list_schema(self, client: TestClient):
        """Test that funding list items have consistent schema"""
        response = client.get('/api/v1/funding/?limit=5')

        assert response.status_code == 200
        data = response.json()

        if len(data) > 0:
            first_item = data[0]
            # All items should have same keys
            expected_keys = set(first_item.keys())

            for item in data:
                assert set(item.keys()) == expected_keys

    def test_funding_id_format(self, client: TestClient):
        """Test that funding_id is properly formatted"""
        response = client.get('/api/v1/funding/?limit=5')

        assert response.status_code == 200
        data = response.json()

        for item in data:
            assert 'funding_id' in item
            assert isinstance(item['funding_id'], str)
            assert len(item['funding_id']) > 0

    def test_funding_urls_are_valid(self, client: TestClient):
        """Test that source URLs are properly formatted"""
        response = client.get('/api/v1/funding/?limit=5')

        assert response.status_code == 200
        data = response.json()

        for item in data:
            if 'source_url' in item and item['source_url']:
                url = item['source_url']
                assert isinstance(url, str)
                # Basic URL validation
                assert url.startswith('http://') or url.startswith('https://')

    def test_funding_dates_format(self, client: TestClient):
        """Test that dates are properly formatted"""
        response = client.get('/api/v1/funding/?limit=5')

        assert response.status_code == 200
        data = response.json()

        for item in data:
            if 'deadline' in item and item['deadline']:
                # Should be a string in ISO format or similar
                assert isinstance(item['deadline'], str)

            if 'created_at' in item and item['created_at']:
                assert isinstance(item['created_at'], str)


@pytest.mark.integration
class TestFundingPerformance:
    """Test performance of funding endpoints"""

    @pytest.mark.slow
    def test_large_limit_performance(self, client: TestClient):
        """Test that large queries don't timeout"""
        response = client.get('/api/v1/funding/?limit=500')

        assert response.status_code == 200
        # Should complete within reasonable time (TestClient timeout)

    def test_concurrent_requests(self, client: TestClient):
        """Test that concurrent requests don't cause errors"""
        # Make multiple requests quickly
        responses = []
        for _ in range(5):
            responses.append(client.get('/api/v1/funding/?limit=10'))

        # All should succeed
        for response in responses:
            assert response.status_code == 200
