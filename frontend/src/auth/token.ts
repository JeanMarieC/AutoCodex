/** JWT + identity persistence in localStorage. */
const TOKEN_KEY = 'manualai_token';
const EMAIL_KEY = 'manualai_email';
const GUEST_KEY = 'manualai_guest';

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const getStoredEmail = () => localStorage.getItem(EMAIL_KEY);
export const isGuestStored = () => localStorage.getItem(GUEST_KEY) === '1';

export function setAuth(token: string, email: string) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(EMAIL_KEY, email);
  localStorage.removeItem(GUEST_KEY);
}

export function setGuest() {
  localStorage.setItem(GUEST_KEY, '1');
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(EMAIL_KEY);
  localStorage.removeItem(GUEST_KEY);
}
