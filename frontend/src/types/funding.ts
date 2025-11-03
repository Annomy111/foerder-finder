/**
 * Funding Opportunity Types
 */

export interface FundingOpportunity {
  id: string;
  title: string;
  description?: string;
  provider: string;
  category?: string;
  amount_min?: number;
  amount_max?: number;
  deadline?: string;
  application_url?: string;
  requirements?: string[];
  eligible_regions?: string[];
  target_group?: string;
  funding_type?: string;
  contact_email?: string;
  contact_phone?: string;
  created_at?: string;
  updated_at?: string;
  scraped_at?: string;
  source_url?: string;
}

export interface FundingFilters {
  category?: string;
  region?: string;
  amount_min?: number;
  amount_max?: number;
  deadline_before?: string;
  deadline_after?: string;
  provider?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

export interface FundingFilterOptions {
  categories: string[];
  regions: string[];
  providers: string[];
  funding_types: string[];
}

export interface FundingListResponse {
  items: FundingOpportunity[];
  total: number;
  limit: number;
  offset: number;
}
