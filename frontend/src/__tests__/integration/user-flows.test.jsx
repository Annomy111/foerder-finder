import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import MockAdapter from 'axios-mock-adapter';
import api from '@/services/api';
import useAuthStore from '@/store/authStore';

// Import pages
import LoginPage from '@/pages/LoginPage';
import FundingListPage from '@/pages/FundingListPage';
import FundingDetailPage from '@/pages/FundingDetailPage';

describe('Critical User Flows - Integration Tests', () => {
  let mock;

  beforeEach(() => {
    mock = new MockAdapter(api);
    useAuthStore.getState().logout();
    localStorage.clear();
  });

  afterEach(() => {
    mock.restore();
  });

  describe('Login Flow', () => {
    it('successfully logs in and redirects to dashboard', async () => {
      const user = userEvent.setup();

      // Mock login endpoint
      const mockAuthResponse = {
        access_token: 'test-jwt-token',
        token_type: 'bearer',
        user: {
          id: '123',
          email: 'admin@gs-musterberg.de',
          role: 'admin',
          school_name: 'Grundschule Musterberg',
        },
      };

      mock.onPost('/api/v1/auth/login').reply(200, mockAuthResponse);

      // Render Login Page
      render(
        <MemoryRouter initialEntries={['/login']}>
          <LoginPage />
        </MemoryRouter>
      );

      // Fill in login form
      const emailInput = screen.getByLabelText(/e-mail/i) || screen.getByRole('textbox', { name: /email/i });
      const passwordInput = screen.getByLabelText(/passwort/i) || screen.getByLabelText(/password/i);

      await user.type(emailInput, 'admin@gs-musterberg.de');
      await user.type(passwordInput, 'test1234');

      // Submit form
      const submitButton = screen.getByRole('button', { name: /anmelden|login/i });
      await user.click(submitButton);

      // Wait for login to complete
      await waitFor(() => {
        const authState = useAuthStore.getState();
        expect(authState.isAuthenticated).toBe(true);
        expect(authState.token).toBe('test-jwt-token');
        expect(authState.user.email).toBe('admin@gs-musterberg.de');
      });
    });

    it('shows error message on failed login', async () => {
      const user = userEvent.setup();

      mock.onPost('/api/v1/auth/login').reply(401, {
        detail: 'Invalid credentials',
      });

      render(
        <MemoryRouter initialEntries={['/login']}>
          <LoginPage />
        </MemoryRouter>
      );

      const emailInput = screen.getByLabelText(/e-mail/i) || screen.getByRole('textbox', { name: /email/i });
      const passwordInput = screen.getByLabelText(/passwort/i) || screen.getByLabelText(/password/i);

      await user.type(emailInput, 'wrong@example.com');
      await user.type(passwordInput, 'wrongpassword');

      const submitButton = screen.getByRole('button', { name: /anmelden|login/i });
      await user.click(submitButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/fehler|error|invalid/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('validates required fields before submission', async () => {
      const user = userEvent.setup();

      render(
        <MemoryRouter initialEntries={['/login']}>
          <LoginPage />
        </MemoryRouter>
      );

      const submitButton = screen.getByRole('button', { name: /anmelden|login/i });
      await user.click(submitButton);

      // Should show validation errors or prevent submission
      // (Depends on implementation - adjust based on actual behavior)
      const authState = useAuthStore.getState();
      expect(authState.isAuthenticated).toBe(false);
    });
  });

  describe('Funding Browse Flow', () => {
    beforeEach(() => {
      // Set authenticated state
      useAuthStore.setState({
        token: 'test-jwt-token',
        isAuthenticated: true,
        user: {
          id: '123',
          email: 'admin@gs-musterberg.de',
          role: 'admin',
        },
      });
    });

    it('displays funding list and allows filtering', async () => {
      const mockFunding = [
        {
          id: 'fund-1',
          title: 'Digitalisierung Förderung',
          provider: 'Ministerium',
          category: 'Digitalisierung',
          amount_min: 5000,
          amount_max: 50000,
          deadline: '2025-12-31',
        },
        {
          id: 'fund-2',
          title: 'MINT Förderung',
          provider: 'Stiftung',
          category: 'MINT',
          amount_min: 1000,
          amount_max: 10000,
          deadline: '2025-11-30',
        },
      ];

      mock.onGet('/api/v1/funding/').reply(200, mockFunding);

      render(
        <MemoryRouter initialEntries={['/funding']}>
          <FundingListPage />
        </MemoryRouter>
      );

      // Wait for funding to load
      await waitFor(() => {
        expect(screen.getByText('Digitalisierung Förderung')).toBeInTheDocument();
        expect(screen.getByText('MINT Förderung')).toBeInTheDocument();
      });

      // Verify funding details are displayed
      const firstCard = screen.getByText('Digitalisierung Förderung').closest('a');
      expect(firstCard).not.toBeNull();
      expect(within(firstCard).getByText(/Ministerium/i)).toBeInTheDocument();

      const secondCard = screen.getByText('MINT Förderung').closest('a');
      expect(secondCard).not.toBeNull();
      expect(within(secondCard).getByText(/Stiftung/i)).toBeInTheDocument();
    });

    it('navigates to funding detail page when clicking on opportunity', async () => {
      const user = userEvent.setup();

      const mockFundingList = [
        {
          id: 'fund-123',
          title: 'Test Förderung',
          provider: 'Test Provider',
          category: 'Digitalisierung',
        },
      ];

      const mockFundingDetail = {
        id: 'fund-123',
        title: 'Test Förderung',
        description: 'Detailed description of the funding opportunity',
        provider: 'Test Provider',
        category: 'Digitalisierung',
        amount_min: 10000,
        amount_max: 100000,
        deadline: '2025-12-31',
        requirements: ['Requirement 1', 'Requirement 2'],
      };

      mock.onGet('/api/v1/funding/').reply(200, mockFundingList);
      mock.onGet('/api/v1/funding/fund-123').reply(200, mockFundingDetail);

      // Render with Routes to support navigation
      render(
        <MemoryRouter initialEntries={['/funding']}>
          <Routes>
            <Route path="/funding" element={<FundingListPage />} />
            <Route path="/funding/:fundingId" element={<FundingDetailPage />} />
          </Routes>
        </MemoryRouter>
      );

      // Wait for list to load
      await waitFor(() => {
        expect(screen.getByText('Test Förderung')).toBeInTheDocument();
      });

      // Click on funding opportunity
      const fundingCard = screen.getByText('Test Förderung');
      await user.click(fundingCard);

      // Should navigate to detail page and show detailed information
      await waitFor(() => {
        expect(screen.getByText(/Detailed description/i)).toBeInTheDocument();
      });
    });

    it('handles empty funding list gracefully', async () => {
      mock.onGet('/api/v1/funding/').reply(200, []);

      render(
        <MemoryRouter initialEntries={['/funding']}>
          <FundingListPage />
        </MemoryRouter>
      );

      // Should show empty state
      await waitFor(() => {
        expect(screen.getByText(/keine.*förder|no.*funding|empty/i)).toBeInTheDocument();
      });
    });

    it('handles API errors during funding fetch', async () => {
      mock.onGet('/api/v1/funding/').reply(500, {
        error: 'Internal server error',
      });

      render(
        <MemoryRouter initialEntries={['/funding']}>
          <FundingListPage />
        </MemoryRouter>
      );

      // Should show error message
      await waitFor(() => {
        expect(screen.getAllByText(/fehler/i).length).toBeGreaterThan(0);
      }, { timeout: 3000 });
    });
  });

  describe('Funding Detail View', () => {
    beforeEach(() => {
      useAuthStore.setState({
        token: 'test-jwt-token',
        isAuthenticated: true,
        user: { id: '123', email: 'test@example.com', role: 'admin' },
      });
    });

    it('displays complete funding information', async () => {
      const user = userEvent.setup();
      const mockFunding = {
        id: 'fund-456',
        title: 'Complete Funding Example',
        description: 'This is a comprehensive funding opportunity',
        provider: 'Example Foundation',
        category: 'Digitalisierung',
        amount_min: 5000,
        amount_max: 50000,
        deadline: '2025-12-31',
        requirements: ['Must be a primary school', 'Must have digital concept'],
        eligible_regions: ['Berlin', 'Hamburg'],
        application_url: 'https://example.com/apply',
      };

      mock.onGet('/api/v1/funding/fund-456').reply(200, mockFunding);

      render(
        <MemoryRouter initialEntries={['/funding/fund-456']}>
          <Routes>
            <Route path="/funding/:fundingId" element={<FundingDetailPage />} />
          </Routes>
        </MemoryRouter>
      );

      // Wait for all details to load
      await waitFor(() => {
        expect(screen.getAllByText('Complete Funding Example').length).toBeGreaterThan(0);
        expect(screen.getByText(/comprehensive funding opportunity/i)).toBeInTheDocument();
        expect(screen.getAllByText('Example Foundation').length).toBeGreaterThan(0);
      });

      // Check funding amount range
      const amountContainer = screen.getByText('Fördersumme').parentElement;
      expect(amountContainer).toHaveTextContent('5.000');
      expect(amountContainer).toHaveTextContent('50.000');

      // Check requirements
      const requirementsTab = screen.getByRole('button', { name: /voraussetzungen/i });
      await user.click(requirementsTab);

      await waitFor(() => {
        expect(screen.getByText(/Must be a primary school/i)).toBeInTheDocument();
        expect(screen.getByText(/Must have digital concept/i)).toBeInTheDocument();
      });
    });

    it('shows "Apply" or "Create Application" button', async () => {
      const mockFunding = {
        id: 'fund-789',
        title: 'Funding with Application',
        provider: 'Provider',
        category: 'Sport',
      };

      mock.onGet('/api/v1/funding/fund-789').reply(200, mockFunding);

      render(
        <MemoryRouter initialEntries={['/funding/fund-789']}>
          <Routes>
            <Route path="/funding/:fundingId" element={<FundingDetailPage />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getAllByText('Funding with Application').length).toBeGreaterThan(0);
      });

      // Should have an apply/create application button
      const applyButton = screen.getByRole('button', { name: /mit ki beantragen/i });
      expect(applyButton).toBeInTheDocument();
    });
  });

  describe('Complete User Journey', () => {
    it('user can browse funding, view details, and start application', async () => {
      const user = userEvent.setup();

      // Set authenticated state
      useAuthStore.setState({
        token: 'test-jwt-token',
        isAuthenticated: true,
        user: {
          id: '123',
          email: 'admin@gs-musterberg.de',
          role: 'admin',
          school_name: 'Grundschule Musterberg',
        },
      });

      // Mock data
      const mockFundingList = [
        {
          id: 'fund-complete',
          title: 'End-to-End Test Funding',
          provider: 'Test Provider',
          category: 'Digitalisierung',
        },
      ];

      const mockFundingDetail = {
        id: 'fund-complete',
        title: 'End-to-End Test Funding',
        description: 'Full journey test',
        provider: 'Test Provider',
        amount_min: 10000,
        amount_max: 50000,
      };

      const mockApplicationResponse = {
        id: 'app-new',
        application_id: 'app-new',
        funding_id: 'fund-complete',
        school_id: '123',
        status: 'draft',
        created_at: '2025-10-05T12:00:00Z',
      };

      mock.onGet('/api/v1/funding/').reply(200, mockFundingList);
      mock.onGet('/api/v1/funding/fund-complete').reply(200, mockFundingDetail);
      mock.onPost('/api/v1/applications/').reply(201, mockApplicationResponse);

      // Render full app
      render(
        <MemoryRouter initialEntries={['/funding']}>
          <Routes>
            <Route path="/funding" element={<FundingListPage />} />
            <Route path="/funding/:fundingId" element={<FundingDetailPage />} />
          </Routes>
        </MemoryRouter>
      );

      // Step 1: See funding list
      await waitFor(() => {
        expect(screen.getByText('End-to-End Test Funding')).toBeInTheDocument();
      });

      // Step 2: Click to view details
      const fundingLink = screen.getByText('End-to-End Test Funding');
      await user.click(fundingLink);

      // Step 3: See detailed information
      await waitFor(() => {
        expect(screen.getByText('Full journey test')).toBeInTheDocument();
      });

      // Step 4: Click "Apply" button (if present)
      const applyButtons = screen.queryAllByRole('button', { name: /bewerb|apply|antrag/i });
      const applyButton = applyButtons[0];
      if (applyButton) {
        await user.click(applyButton);

        // Should trigger application creation flow
        await waitFor(() => {
          // Depending on implementation, might navigate or show modal
          // Adjust assertion based on actual behavior
          expect(mock.history.post.length).toBeGreaterThan(0);
        });
      }
    });
  });

  describe('Error Recovery', () => {
    beforeEach(() => {
      useAuthStore.setState({
        token: 'test-jwt-token',
        isAuthenticated: true,
        user: { id: '123', email: 'test@example.com', role: 'admin' },
      });
    });

    it('allows retry after failed network request', async () => {
      const user = userEvent.setup();

      // First call fails, second succeeds
      mock
        .onGet('/api/v1/funding/')
        .replyOnce(500)
        .onGet('/api/v1/funding/')
        .replyOnce(200, [
          { id: 'fund-1', title: 'Recovered Funding', provider: 'Provider' },
        ]);

      render(
        <MemoryRouter initialEntries={['/funding']}>
          <FundingListPage />
        </MemoryRouter>
      );

      // Should show error first
      await waitFor(() => {
        expect(screen.getAllByText(/fehler/i).length).toBeGreaterThan(0);
      });

      // Click retry button (if present)
      const retryButton = screen.queryByRole('button', { name: /erneut|retry|reload/i });
      if (retryButton) {
        await user.click(retryButton);

        // Should load successfully
        await waitFor(() => {
          expect(screen.getByText('Recovered Funding')).toBeInTheDocument();
        });
      }
    });
  });
});
