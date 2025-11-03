/**
 * Application Types
 */

export type ApplicationStatus = 'draft' | 'submitted' | 'approved' | 'rejected' | 'in_review';

export interface Application {
  id: string;
  funding_id: string;
  school_id: string;
  user_id: string;
  status: ApplicationStatus;
  school_context?: string;
  created_at: string;
  updated_at: string;
  submitted_at?: string;

  // Relations (populated in detail views)
  funding?: {
    id: string;
    title: string;
    provider: string;
    deadline?: string;
  };
}

export interface CreateApplicationData {
  funding_id: string;
  school_context?: string;
}

export interface UpdateApplicationData {
  school_context?: string;
  status?: ApplicationStatus;
}

export interface ApplicationDraft {
  id: string;
  application_id: string;
  funding_id: string;
  generated_text: string;
  user_query?: string;
  confidence_score?: number;
  created_at: string;
  version: number;

  // Metadata
  word_count?: number;
  char_count?: number;
  sections?: string[];
}

export interface GenerateDraftData {
  application_id: string;
  funding_id: string;
  user_query: string;
  school_context?: string;
}

export interface DraftFeedbackData {
  draft_id: string;
  feedback: string;
  rating?: number;
}

export interface DraftFeedbackResponse {
  success: boolean;
  message: string;
}
