import axios from 'axios';
import {
  User,
  Lead,
  Search,
  Export,
  DashboardStats,
  SearchRequest
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'https://api.useleadnest.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Auth interceptor to add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (email: string, password: string): Promise<{ token: string; user: User }> => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },

  register: async (email: string, password: string, businessName: string): Promise<{ token: string; user: User }> => {
    const response = await api.post('/api/auth/register', { email, password, business_name: businessName });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

// Search API
export const searchAPI = {
  createSearch: async (data: SearchRequest): Promise<Search> => {
    const response = await api.post('/searches', data);
    return response.data;
  },

  getSearches: async (): Promise<Search[]> => {
    const response = await api.get('/searches');
    return response.data;
  },

  getSearchLeads: async (searchId: number): Promise<Lead[]> => {
    const response = await api.get(`/searches/${searchId}/leads`);
    return response.data;
  },
};

// Export API
export const exportAPI = {
  createExport: async (searchId: number, exportType: string): Promise<Export> => {
    const response = await api.post('/exports', {
      search_id: searchId,
      export_type: exportType,
    });
    return response.data;
  },

  downloadCSV: async (searchId: number): Promise<Blob> => {
    const response = await api.get(`/exports/${searchId}/csv`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
};

// Admin API
export const adminAPI = {
  getUsers: async (): Promise<User[]> => {
    const response = await api.get('/admin/users');
    return response.data;
  },

  getStats: async (): Promise<any> => {
    const response = await api.get('/admin/stats');
    return response.data;
  },
};

export default api;
