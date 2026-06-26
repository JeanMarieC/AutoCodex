/** Auth API calls (signup / login). */
import { BASE_URL } from './client';

export interface AuthResult {
  access_token: string;
  email: string;
}

async function post(path: string, email: string, password: string): Promise<AuthResult> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ?? `Request failed (${res.status})`);
  }
  return res.json() as Promise<AuthResult>;
}

export const signup = (email: string, password: string) =>
  post('/auth/signup', email, password);

export const login = (email: string, password: string) =>
  post('/auth/login', email, password);
