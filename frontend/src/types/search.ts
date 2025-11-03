/**
 * RAG Search Types
 */

export interface SearchParams {
  query: string;
  top_k?: number;
  region?: string;
  funding_id?: string;
  expand_queries?: boolean;
  rerank_results?: boolean;
}

export interface SearchResult {
  id: string;
  title: string;
  provider: string;
  score: number;
  excerpt?: string;
  category?: string;
  amount_min?: number;
  amount_max?: number;
  deadline?: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query_time_ms: number;
  expanded_queries?: string[];
  reranked?: boolean;
}

export interface QuickSearchParams {
  q: string;
  limit?: number;
}

export interface RAGHealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  vector_db_status: 'connected' | 'disconnected';
  index_size: number;
  last_indexed?: string;
  embeddings_model?: string;
}
