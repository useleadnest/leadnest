// src/api.ts
const baseURL = process.env.REACT_APP_API_BASE_URL!;
export const apiFetch = (path: string, init?: RequestInit) =>
  fetch(`${baseURL}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) }});
