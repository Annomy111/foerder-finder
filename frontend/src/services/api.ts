/**
 * API Service - Axios Client mit automatischer JWT-Authentifizierung
 * Fully typed with TypeScript
 */

import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios';
import useAuthStore from '@/store/authStore';
import type {
  LoginResponse,
  RegisterData,
  RegisterResponse,
  FundingOpportunity,
  FundingFilters,
  FundingFilterOptions,
  Application,
  CreateApplicationData,
  UpdateApplicationData,
  ApplicationDraft,
  GenerateDraftData,
  DraftFeedbackResponse,
  SearchParams,
  SearchResponse,
  RAGHealthResponse,
  HealthResponse,
} from '@/types';

// Base URL (aus ENV oder default)
const API_BASE_URL = import.meta.env['VITE_API_URL'] || 'http://localhost:8000';

// Axios Instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor - fügt JWT Token hinzu
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response Interceptor - behandelt 401 Errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - logout
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Auth Endpoints
// ============================================================================

export const authAPI = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/api/v1/auth/login', { email, password });
    return response.data;
  },

  register: async (userData: RegisterData): Promise<RegisterResponse> => {
    const response = await api.post<RegisterResponse>('/api/v1/auth/register', userData);
    return response.data;
  },
};

// ============================================================================
// Funding Endpoints
// ============================================================================

export const fundingAPI = {
  list: async (filters: FundingFilters = {}): Promise<FundingOpportunity[]> => {
    const response = await api.get<FundingOpportunity[]>('/api/v1/funding/', { params: filters });
    return response.data;
  },

  getById: async (fundingId: string): Promise<FundingOpportunity> => {
    const response = await api.get<FundingOpportunity>(`/api/v1/funding/${fundingId}`);
    return response.data;
  },

  getFilterOptions: async (): Promise<FundingFilterOptions> => {
    const response = await api.get<FundingFilterOptions>('/api/v1/funding/filters/options');
    return response.data;
  },
};

// ============================================================================
// Applications Endpoints
// ============================================================================

export const applicationsAPI = {
  list: async (): Promise<Application[]> => {
    const response = await api.get<Application[]>('/api/v1/applications/');
    return response.data;
  },

  getById: async (applicationId: string): Promise<Application> => {
    const response = await api.get<Application>(`/api/v1/applications/${applicationId}`);
    return response.data;
  },

  create: async (data: CreateApplicationData): Promise<Application> => {
    const response = await api.post<Application>('/api/v1/applications/', data);
    return response.data;
  },

  update: async (applicationId: string, data: UpdateApplicationData): Promise<Application> => {
    const response = await api.patch<Application>(`/api/v1/applications/${applicationId}`, data);
    return response.data;
  },

  delete: async (applicationId: string): Promise<void> => {
    await api.delete(`/api/v1/applications/${applicationId}`);
  },
};

// ============================================================================
// AI Drafts Endpoints
// ============================================================================

export const draftsAPI = {
  generate: async (data: GenerateDraftData): Promise<ApplicationDraft> => {
    const response = await api.post<ApplicationDraft>('/api/v1/drafts/generate', data);
    return response.data;
  },

  getForApplication: async (applicationId: string): Promise<ApplicationDraft[]> => {
    const response = await api.get<ApplicationDraft[]>(`/api/v1/drafts/application/${applicationId}`);
    return response.data;
  },

  submitFeedback: async (draftId: string, feedback: string): Promise<DraftFeedbackResponse> => {
    const response = await api.post<DraftFeedbackResponse>('/api/v1/drafts/feedback', {
      draft_id: draftId,
      feedback: feedback,
    });
    return response.data;
  },
};

// ============================================================================
// RAG Search Endpoints
// ============================================================================

export const searchAPI = {
  /**
   * Advanced semantic search with RAG pipeline
   * @param params - Search parameters
   */
  search: async (params: SearchParams): Promise<SearchResponse> => {
    const response = await api.post<SearchResponse>('/api/v1/search/', params);
    return response.data;
  },

  /**
   * Quick search (optimized for speed, no expansion/reranking)
   * @param query - Search query
   * @param limit - Number of results (default: 5)
   */
  quickSearch: async (query: string, limit: number = 5): Promise<SearchResponse> => {
    const response = await api.get<SearchResponse>('/api/v1/search/quick', {
      params: { q: query, limit },
    });
    return response.data;
  },

  /**
   * RAG system health check
   */
  health: async (): Promise<RAGHealthResponse> => {
    const response = await api.get<RAGHealthResponse>('/api/v1/search/health');
    return response.data;
  },
};

// ============================================================================
// Health Check
// ============================================================================

export const healthCheck = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>('/api/v1/health');
  return response.data;
};

export default api;
