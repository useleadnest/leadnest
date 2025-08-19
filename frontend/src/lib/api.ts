// API Client for LeadNest
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'https://api.useleadnest.com/api';

interface Lead {
  id?: number;
  first_name: string;
  last_name: string;
  phone?: string;
  email?: string;
  status?: string;
  notes?: string;
}

interface UserData {
  email: string;
  plan?: string;
  subscription_status?: string;
}

// Core API function
export const api = async <T>(path: string, options: RequestInit = {}): Promise<T> => {
  const token = localStorage.getItem('ln_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText}`);
  }

  return response.json();
};

// Auth API
export const Auth = {
  login: async (email: string, password: string): Promise<{ token: string }> => {
    return api<{ token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  register: async (email: string, password: string): Promise<{ token: string }> => {
    return api<{ token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },
};

// Leads API
export const Leads = {
  list: async (): Promise<Lead[]> => {
    return api<Lead[]>('/leads');
  },

  bulkUpload: async (file: File): Promise<{ created: number; duplicates: number }> => {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('ln_token');
    const response = await fetch(`${API_BASE_URL}/leads/bulk`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Upload failed: ${errorText}`);
    }

    return response.json();
  },
};

// Billing API (Stripe)
export const Billing = {
  createCheckoutSession: async (plan: 'starter' | 'pro' | 'enterprise'): Promise<{ url: string }> => {
    return api<{ url: string }>('/stripe/checkout', {
      method: 'POST',
      body: JSON.stringify({ plan }),
    });
  },

  createPortalSession: async (): Promise<{ url: string }> => {
    return api<{ url: string }>('/stripe/portal', {
      method: 'POST',
    });
  },
};

// User API
export const User = {
  me: async (): Promise<UserData> => {
    return api<UserData>('/users/me');
  },
};

// Health check
export const Health = {
  check: async () => {
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/healthz`);
    return response.json();
  },
  
  ping: async () => {
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/healthz`);
    if (!response.ok) throw new Error('Ping failed');
    return response.json();
  }
};

export type { Lead, UserData };
