/**
 * Thin fetch wrapper. All calls go through `/api`, which Vite proxies to the
 * FastAPI backend in dev (see vite.config.ts) and the reverse proxy serves in
 * prod. Override with VITE_API_BASE_URL when calling a remote backend.
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export { BASE_URL };
