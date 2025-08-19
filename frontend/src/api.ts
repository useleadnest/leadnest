const baseURL = process.env.REACT_APP_API_BASE_URL!;
export async function apiFetch(path: string, init?: RequestInit) {
  const res = await fetch(`${baseURL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    credentials: 'include',
  });
  return res;
}
