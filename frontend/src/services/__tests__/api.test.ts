import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import MockAdapter from 'axios-mock-adapter';
import api, {
  authAPI,
  fundingAPI,
  applicationsAPI,
  draftsAPI,
  searchAPI,
  healthCheck,
} from '../api';
import useAuthStore from '@/store/authStore';
import type { ApplicationStatus } from '@/types';

describe('API Service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    // Create new mock adapter for each test
    mock = new MockAdapter(api);

    // Clear auth store
    useAuthStore.getState().logout();
  });

  afterEach(() => {
    mock.restore();
  });

  describe('Auth API', () => {
    it('login - successful authentication', async () => {
      const mockResponse = {
        access_token: 'test-jwt-token',
        token_type: 'bearer',
        user: {
          id: '123',
          email: 'test@example.com',
          role: 'admin',
        },
      };

      mock.onPost('/api/v1/auth/login').reply(200, mockResponse);

      const result = await authAPI.login('test@example.com', 'password123');

      expect(result).toEqual(mockResponse);
      expect(mock.history.post.length).toBe(1);
      expect(mock.history.post[0].data).toBe(
        JSON.stringify({ email: 'test@example.com', password: 'password123' })
      );
    });

    it('login - handles authentication failure', async () => {
      mock.onPost('/api/v1/auth/login').reply(401, {
        detail: 'Invalid credentials',
      });

      await expect(authAPI.login('wrong@example.com', 'wrongpass')).rejects.toThrow();
    });

    it('register - successful user registration', async () => {
      const userData = {
        email: 'new@example.com',
        password: 'securepass',
        school_name: 'Test School',
      };

      const mockResponse = {
        id: '456',
        email: 'new@example.com',
      };

      mock.onPost('/api/v1/auth/register').reply(201, mockResponse);

      const result = await authAPI.register(userData);

      expect(result).toEqual(mockResponse);
      expect(mock.history.post[0].data).toBe(JSON.stringify(userData));
    });
  });

  describe('Funding API', () => {
    it('list - fetches all funding opportunities', async () => {
      const mockFunding = [
        {
          id: 'fund-1',
          title: 'Digitalisierung Förderung',
          provider: 'Ministerium',
          amount_min: 5000,
          amount_max: 50000,
        },
        {
          id: 'fund-2',
          title: 'MINT Förderung',
          provider: 'Stiftung',
          amount_min: 1000,
          amount_max: 10000,
        },
      ];

      mock.onGet('/api/v1/funding/').reply(200, mockFunding);

      const result = await fundingAPI.list();

      expect(result).toEqual(mockFunding);
      expect(result.length).toBe(2);
    });

    it('list - applies filters correctly', async () => {
      const filters = { region: 'Berlin', category: 'Digitalisierung' };

      mock.onGet('/api/v1/funding/', { params: filters }).reply(200, []);

      await fundingAPI.list(filters);

      const request = mock.history.get[0];
      expect(request.params).toEqual(filters);
    });

    it('getById - fetches single funding opportunity', async () => {
      const mockFunding = {
        id: 'fund-123',
        title: 'Test Förderung',
        description: 'Detailed description',
        provider: 'Provider Name',
      };

      mock.onGet('/api/v1/funding/fund-123').reply(200, mockFunding);

      const result = await fundingAPI.getById('fund-123');

      expect(result).toEqual(mockFunding);
      expect(result.id).toBe('fund-123');
    });

    it('getById - handles 404 not found', async () => {
      mock.onGet('/api/v1/funding/nonexistent').reply(404);

      await expect(fundingAPI.getById('nonexistent')).rejects.toThrow();
    });

    it('getFilterOptions - fetches available filter options', async () => {
      const mockOptions = {
        regions: ['Berlin', 'Hamburg', 'Bayern'],
        categories: ['Digitalisierung', 'MINT', 'Sport'],
      };

      mock.onGet('/api/v1/funding/filters/options').reply(200, mockOptions);

      const result = await fundingAPI.getFilterOptions();

      expect(result).toEqual(mockOptions);
    });
  });

  describe('Applications API', () => {
    beforeEach(() => {
      // Set auth token for protected endpoints
      useAuthStore.setState({
        token: 'test-jwt-token',
        isAuthenticated: true,
      });
    });

    it('list - fetches all applications', async () => {
      const mockApplications = [
        {
          id: 'app-1',
          funding_id: 'fund-1',
          status: 'draft',
          school_context: 'Context 1',
        },
        {
          id: 'app-2',
          funding_id: 'fund-2',
          status: 'submitted',
          school_context: 'Context 2',
        },
      ];

      mock.onGet('/api/v1/applications/').reply(200, mockApplications);

      const result = await applicationsAPI.list();

      expect(result).toEqual(mockApplications);
      expect(result.length).toBe(2);
    });

    it('list - includes authorization header', async () => {
      mock.onGet('/api/v1/applications/').reply(200, []);

      await applicationsAPI.list();

      const request = mock.history.get[0];
      expect(request.headers.Authorization).toBe('Bearer test-jwt-token');
    });

    it('getById - fetches single application', async () => {
      const mockApplication = {
        id: 'app-123',
        funding_id: 'fund-456',
        status: 'draft',
      };

      mock.onGet('/api/v1/applications/app-123').reply(200, mockApplication);

      const result = await applicationsAPI.getById('app-123');

      expect(result).toEqual(mockApplication);
    });

    it('create - creates new application', async () => {
      const newApplication = {
        funding_id: 'fund-789',
        school_context: 'We need this funding for...',
      };

      const mockResponse = {
        id: 'app-new',
        ...newApplication,
        status: 'draft',
        created_at: '2025-10-05T12:00:00Z',
      };

      mock.onPost('/api/v1/applications/').reply(201, mockResponse);

      const result = await applicationsAPI.create(newApplication);

      expect(result).toEqual(mockResponse);
      expect(result.id).toBe('app-new');
    });

    it('update - updates existing application', async () => {
      const updateData = {
        school_context: 'Updated context',
        status: 'submitted' as ApplicationStatus,
      };

      const mockResponse = {
        id: 'app-123',
        ...updateData,
        updated_at: '2025-10-05T12:30:00Z',
      };

      mock.onPatch('/api/v1/applications/app-123').reply(200, mockResponse);

      const result = await applicationsAPI.update('app-123', updateData);

      expect(result).toEqual(mockResponse);
    });

    it('delete - deletes application', async () => {
      mock.onDelete('/api/v1/applications/app-123').reply(204);

      await expect(applicationsAPI.delete('app-123')).resolves.not.toThrow();
    });
  });

  describe('Drafts API', () => {
    beforeEach(() => {
      useAuthStore.setState({ token: 'test-jwt-token', isAuthenticated: true });
    });

    it('generate - creates AI-generated draft', async () => {
      const generateData = {
        application_id: 'app-123',
        funding_id: 'fund-456',
        user_query: 'Generate a draft for digital equipment',
      };

      const mockDraft = {
        id: 'draft-789',
        application_id: 'app-123',
        generated_text: 'AI-generated draft content...',
        confidence_score: 0.92,
      };

      mock.onPost('/api/v1/drafts/generate').reply(200, mockDraft);

      const result = await draftsAPI.generate(generateData);

      expect(result).toEqual(mockDraft);
      expect(result.confidence_score).toBeGreaterThan(0.9);
    });

    it('getForApplication - fetches drafts for application', async () => {
      const mockDrafts = [
        { id: 'draft-1', version: 1 },
        { id: 'draft-2', version: 2 },
      ];

      mock.onGet('/api/v1/drafts/application/app-123').reply(200, mockDrafts);

      const result = await draftsAPI.getForApplication('app-123');

      expect(result).toEqual(mockDrafts);
      expect(result.length).toBe(2);
    });

    it('submitFeedback - sends user feedback on draft', async () => {
      const mockResponse = { success: true, message: 'Feedback recorded' };

      mock.onPost('/api/v1/drafts/feedback').reply(200, mockResponse);

      const result = await draftsAPI.submitFeedback('draft-123', 'Great draft!');

      expect(result).toEqual(mockResponse);

      const request = mock.history.post[0];
      const data = JSON.parse(request.data);
      expect(data.draft_id).toBe('draft-123');
      expect(data.feedback).toBe('Great draft!');
    });
  });

  describe('Search API', () => {
    beforeEach(() => {
      useAuthStore.setState({ token: 'test-jwt-token', isAuthenticated: true });
    });

    it('search - performs advanced semantic search', async () => {
      const searchParams = {
        query: 'Digitalisierung Grundschule',
        top_k: 10,
        expand_queries: true,
        rerank_results: true,
      };

      const mockResults = {
        results: [
          { id: 'fund-1', score: 0.95, title: 'Digital Funding' },
          { id: 'fund-2', score: 0.88, title: 'IT Equipment' },
        ],
        total: 2,
        query_time_ms: 125,
      };

      mock.onPost('/api/v1/search/').reply(200, mockResults);

      const result = await searchAPI.search(searchParams);

      expect(result).toEqual(mockResults);
      expect(result.results.length).toBe(2);
      expect(result.results[0]!.score).toBeGreaterThan(0.9);
    });

    it('quickSearch - performs fast search without advanced features', async () => {
      const mockResults = {
        results: [{ id: 'fund-1', title: 'Quick Result' }],
      };

      mock.onGet('/api/v1/search/quick').reply(200, mockResults);

      const result = await searchAPI.quickSearch('Digitalisierung', 5);

      expect(result).toEqual(mockResults);

      const request = mock.history.get[0];
      expect(request.params.q).toBe('Digitalisierung');
      expect(request.params.limit).toBe(5);
    });

    it('health - checks RAG system status', async () => {
      const mockHealth = {
        status: 'healthy',
        vector_db_status: 'connected',
        index_size: 124,
      };

      mock.onGet('/api/v1/search/health').reply(200, mockHealth);

      const result = await searchAPI.health();

      expect(result).toEqual(mockHealth);
      expect(result.status).toBe('healthy');
    });
  });

  describe('General API', () => {
    it('healthCheck - verifies API is running', async () => {
      const mockHealth = {
        status: 'ok',
        version: '1.0.0',
      };

      mock.onGet('/api/v1/health').reply(200, mockHealth);

      const result = await healthCheck();

      expect(result).toEqual(mockHealth);
      expect(result.status).toBe('ok');
    });
  });

  describe('Request Interceptors', () => {
    it('adds JWT token to requests when authenticated', async () => {
      useAuthStore.setState({ token: 'my-jwt-token', isAuthenticated: true });

      mock.onGet('/api/v1/funding/').reply(200, []);

      await fundingAPI.list();

      const request = mock.history.get[0];
      expect(request.headers.Authorization).toBe('Bearer my-jwt-token');
    });

    it('does not add Authorization header when not authenticated', async () => {
      useAuthStore.setState({ token: null, isAuthenticated: false });

      mock.onGet('/api/v1/funding/').reply(200, []);

      await fundingAPI.list();

      const request = mock.history.get[0];
      expect(request.headers.Authorization).toBeUndefined();
    });
  });

  describe('Response Interceptors', () => {
    it('logs out user on 401 Unauthorized response', async () => {
      useAuthStore.setState({ token: 'expired-token', isAuthenticated: true });

      // Mock window.location.href in a TypeScript-safe way
      const originalLocation = window.location;
      // @ts-expect-error - Mocking window.location for testing
      delete window.location;
      window.location = { ...originalLocation, href: '' };

      mock.onGet('/api/v1/applications/').reply(401);

      await expect(applicationsAPI.list()).rejects.toThrow();

      // Check that logout was called
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
      expect(useAuthStore.getState().token).toBeNull();

      // Restore window.location
      window.location = originalLocation;
    });
  });

  describe('Error Handling', () => {
    it('handles network errors gracefully', async () => {
      mock.onGet('/api/v1/funding/').networkError();

      await expect(fundingAPI.list()).rejects.toThrow();
    });

    it('handles timeout errors', async () => {
      mock.onGet('/api/v1/funding/').timeout();

      await expect(fundingAPI.list()).rejects.toThrow();
    });

    it('handles 500 server errors', async () => {
      mock.onGet('/api/v1/funding/').reply(500, {
        error: 'Internal server error',
      });

      await expect(fundingAPI.list()).rejects.toThrow();
    });

    it('handles 404 not found errors', async () => {
      mock.onGet('/api/v1/funding/nonexistent').reply(404);

      await expect(fundingAPI.getById('nonexistent')).rejects.toThrow();
    });
  });
});
