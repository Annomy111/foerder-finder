/**
 * Type Definitions Index
 * Centralized export for all TypeScript types
 */

// Auth types
export type {
  User,
  LoginCredentials,
  LoginResponse,
  RegisterData,
  RegisterResponse,
  AuthState,
} from './auth';

// Funding types
export type {
  FundingOpportunity,
  FundingFilters,
  FundingFilterOptions,
  FundingListResponse,
} from './funding';

// Application types
export type {
  Application,
  ApplicationStatus,
  CreateApplicationData,
  UpdateApplicationData,
  ApplicationDraft,
  GenerateDraftData,
  DraftFeedbackData,
  DraftFeedbackResponse,
} from './application';

// Search types
export type {
  SearchParams,
  SearchResult,
  SearchResponse,
  QuickSearchParams,
  RAGHealthResponse,
} from './search';

// Common types
export type {
  ApiResponse,
  ApiError,
  PaginationParams,
  PaginatedResponse,
  HealthResponse,
} from './common';
