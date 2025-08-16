export interface User {
  id: number;
  email: string;
  business_id?: number;
  role?: string;
  is_active?: boolean;
  is_admin?: boolean;
  created_at?: string;
  trial_ends_at?: string;
  subscription_status?: string;
}

export interface Lead {
  id: number;
  search_id: number;
  business_name: string;
  phone?: string;
  email?: string;
  website?: string;
  address?: string;
  category?: string;
  rating?: number;
  review_count?: number;
  ai_email_message?: string;
  ai_sms_message?: string;
  quality_score?: number;
  created_at: string;
}

export interface Search {
  id: number;
  user_id: number;
  location: string;
  trade: string;
  results_count: number;
  created_at: string;
  leads?: Lead[];
}

export interface Export {
  id: number;
  user_id: number;
  search_id: number;
  export_type: string;
  leads_count: number;
  created_at: string;
}

export interface DashboardStats {
  total_searches: number;
  total_leads: number;
  total_exports: number;
  trial_days_left?: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface SearchRequest {
  location: string;
  trade: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
