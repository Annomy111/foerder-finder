/**
 * API Service - Axios Client mit automatischer JWT-Authentifizierung
 */

import axios from 'axios'
import useAuthStore from '@/store/authStore'

// Base URL (aus ENV oder default)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Axios Instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request Interceptor - fügt JWT Token hinzu
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response Interceptor - behandelt 401 Errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - logout
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ============================================================================
// Auth Endpoints
// ============================================================================

export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/api/v1/auth/login', { email, password })
    return response.data
  },

  register: async (userData) => {
    const response = await api.post('/api/v1/auth/register', userData)
    return response.data
  },
}

// ============================================================================
// Funding Endpoints
// ============================================================================

export const fundingAPI = {
  list: async (filters = {}) => {
    const response = await api.get('/api/v1/funding/', { params: filters })
    return response.data
  },

  getById: async (fundingId) => {
    const response = await api.get(`/api/v1/funding/${fundingId}`)
    return response.data
  },

  getFilterOptions: async () => {
    const response = await api.get('/api/v1/funding/filters/options')
    return response.data
  },
}

// ============================================================================
// Applications Endpoints
// ============================================================================

export const applicationsAPI = {
  list: async () => {
    const response = await api.get('/api/v1/applications/')
    return response.data
  },

  getById: async (applicationId) => {
    const response = await api.get(`/api/v1/applications/${applicationId}`)
    return response.data
  },

  create: async (data) => {
    const response = await api.post('/api/v1/applications/', data)
    return response.data
  },

  update: async (applicationId, data) => {
    const response = await api.patch(`/api/v1/applications/${applicationId}`, data)
    return response.data
  },

  delete: async (applicationId) => {
    await api.delete(`/api/v1/applications/${applicationId}`)
  },
}

// ============================================================================
// AI Drafts Endpoints
// ============================================================================

export const draftsAPI = {
  generate: async (data) => {
    const response = await api.post('/api/v1/drafts/generate', data)
    return response.data
  },

  getForApplication: async (applicationId) => {
    const response = await api.get(`/api/v1/drafts/application/${applicationId}`)
    return response.data
  },

  submitFeedback: async (draftId, feedback) => {
    const response = await api.post('/api/v1/drafts/feedback', {
      draft_id: draftId,
      feedback: feedback,
    })
    return response.data
  },
}

// ============================================================================
// RAG Search Endpoints (NEW!)
// ============================================================================

export const searchAPI = {
  /**
   * Advanced semantic search with RAG pipeline
   * @param {Object} params - Search parameters
   * @param {string} params.query - Search query
   * @param {number} params.top_k - Number of results (default: 10)
   * @param {string} params.region - Filter by region
   * @param {string} params.funding_id - Filter by funding ID
   * @param {boolean} params.expand_queries - Enable query expansion (default: true)
   * @param {boolean} params.rerank_results - Enable reranking (default: true)
   */
  search: async (params) => {
    const response = await api.post('/api/v1/search/', params)
    return response.data
  },

  /**
   * Quick search (optimized for speed, no expansion/reranking)
   * @param {string} query - Search query
   * @param {number} limit - Number of results (default: 5)
   */
  quickSearch: async (query, limit = 5) => {
    const response = await api.get('/api/v1/search/quick', {
      params: { q: query, limit }
    })
    return response.data
  },

  /**
   * RAG system health check
   */
  health: async () => {
    const response = await api.get('/api/v1/search/health')
    return response.data
  }
}

// ============================================================================
// Health Check
// ============================================================================

export const healthCheck = async () => {
  const response = await api.get('/api/v1/health')
  return response.data
}

export default api
