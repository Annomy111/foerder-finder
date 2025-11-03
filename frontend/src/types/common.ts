/**
 * Common Types
 */

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success?: boolean;
}

export interface ApiError {
  error: string;
  detail?: string;
  status?: number;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface HealthResponse {
  status: 'ok' | 'error';
  version?: string;
  timestamp?: string;
}
