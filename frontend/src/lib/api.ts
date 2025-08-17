export const api = async <T>(path: string, options: RequestInit = {}): Promise<T> => {
  const base = import.meta.env.VITE_API_BASE_URL;
  const token = localStorage.getItem('ln_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  } as Record<string, string>;

  const res = await fetch(`${base}${path}`, { ...options, headers });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
};
