// Legacy API wrapper - use lib/api.ts for new code
const RAW_BASE = process.env.REACT_APP_API_BASE_URL;
if (!RAW_BASE) {
  console.error("REACT_APP_API_BASE_URL is missing");
}
const baseURL = RAW_BASE?.replace(/\/+$/, "") ?? "";

export async function apiFetch(path: string, init?: RequestInit) {
  const url = `${baseURL}/${path.replace(/^\/+/, "")}`;
  try {
    const res = await fetch(url, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers || {}),
      },
      credentials: 'include',
    });
    
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${res.statusText}: ${text.slice(0, 400)}`);
    }
    
    return res;
  } catch (e: any) {
    console.error("apiFetch error:", { url, error: e?.message });
    throw e;
  }
}
