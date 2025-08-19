// API Client for LeadNest
const RAW_BASE = process.env.REACT_APP_API_BASE_URL; // must be: https://api.useleadnest.com/api
if (!RAW_BASE) {
  console.error("REACT_APP_API_BASE_URL is missing");
}
const BASE_URL = RAW_BASE?.replace(/\/+$/, "") ?? ""; // trim trailing slash

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

export async function apiFetch(path: string, init: RequestInit = {}) {
  const url = `${BASE_URL}/${path.replace(/^\/+/, "")}`;
  try {
    const res = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers || {}),
      },
      // credentials not required unless we set cookies. Keep 'same-origin' default.
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${res.statusText}: ${text.slice(0, 400)}`);
    }
    return res.headers.get("content-type")?.includes("application/json")
      ? res.json()
      : res.text();
  } catch (e: any) {
    console.error("apiFetch error:", { url, error: e?.message });
    throw e;
  }
}

// Core API function (legacy wrapper)
export const api = async <T>(path: string, options: RequestInit = {}): Promise<T> => {
  const token = localStorage.getItem('ln_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  return apiFetch(path, {
    ...options,
    headers,
  });
};

// Auth API
export const Auth = {
  login: async (email: string, password: string): Promise<{ token: string }> => {
    return apiFetch('auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  register: async (email: string, password: string): Promise<{ token: string }> => {
    return apiFetch('auth/register', {
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
    const response = await fetch(`${BASE_URL}/leads/bulk`, {
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
    const response = await fetch(`${BASE_URL.replace('/api', '')}/healthz`);
    return response.json();
  },
  
  ping: async () => {
    const response = await fetch(`${BASE_URL.replace('/api', '')}/healthz`);
    if (!response.ok) throw new Error('Ping failed');
    return response.json();
  }
};

export type { Lead, UserData };
