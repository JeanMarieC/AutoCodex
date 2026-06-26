import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import * as authApi from '@/api/auth';
import { clearAuth, getStoredEmail, isGuestStored, setAuth, setGuest } from './token';

interface AuthValue {
  email: string | null;
  isAuthed: boolean;
  isGuest: boolean;
  /** True once the user may use the app (signed in or guest). */
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  continueAsGuest: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(getStoredEmail());
  const [guest, setGuestState] = useState<boolean>(isGuestStored());

  const login = useCallback(async (e: string, p: string) => {
    const res = await authApi.login(e, p);
    setAuth(res.access_token, res.email);
    setEmail(res.email);
    setGuestState(false);
  }, []);

  const signup = useCallback(async (e: string, p: string) => {
    const res = await authApi.signup(e, p);
    setAuth(res.access_token, res.email);
    setEmail(res.email);
    setGuestState(false);
  }, []);

  const continueAsGuest = useCallback(() => {
    setGuest();
    setGuestState(true);
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setEmail(null);
    setGuestState(false);
  }, []);

  const value = useMemo<AuthValue>(
    () => ({
      email,
      isAuthed: !!email,
      isGuest: guest,
      ready: !!email || guest,
      login,
      signup,
      continueAsGuest,
      logout,
    }),
    [email, guest, login, signup, continueAsGuest, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
