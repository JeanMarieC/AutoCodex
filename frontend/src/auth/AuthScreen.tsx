import { useState } from 'react';
import { ArrowIcon } from '@/components/icons';
import { useAuth } from './AuthContext';

const FIELD =
  'ma-field rounded-[11px] bg-black/[0.32] px-[13px] py-3 text-[15px] w-full';

export default function AuthScreen() {
  const { login, signup, continueAsGuest } = useAuth();
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setError(null);
    setBusy(true);
    try {
      if (mode === 'login') await login(email.trim(), password);
      else await signup(email.trim(), password);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      className="flex min-h-screen items-center justify-center px-5"
      style={{
        background:
          'radial-gradient(1100px 520px at 50% -120px, rgba(111,177,255,0.10), transparent 60%), #08090b',
      }}
    >
      <div className="w-full max-w-[400px] animate-fadeup">
        <div className="mb-7 flex items-center justify-center gap-3">
          <div className="flex h-[30px] w-[30px] items-center justify-center rounded-lg border border-white/10 bg-gradient-to-br from-[#2a2f37] to-[#0f1115] shadow-[0_0_18px_rgba(111,177,255,0.18)]">
            <div className="h-[13px] w-[13px] rotate-[35deg] rounded-full border-2 border-accent border-t-transparent" />
          </div>
          <span className="font-display text-[15px] font-semibold uppercase tracking-[0.14em]">
            Manual<span className="text-accent">.ai</span>
          </span>
        </div>

        <div className="rounded-[18px] border border-white/10 bg-gradient-to-b from-white/[0.045] to-white/[0.015] p-6 shadow-[0_30px_70px_-30px_rgba(0,0,0,0.85)]">
          <h1 className="m-0 mb-1 text-center font-display text-[22px] font-semibold">
            {mode === 'login' ? 'Welcome back' : 'Create your account'}
          </h1>
          <p className="mb-5 text-center text-[13.5px] text-muted">
            {mode === 'login'
              ? 'Sign in to access your garage and saved chats.'
              : 'Save your cars and chat history across sessions.'}
          </p>

          <div className="flex flex-col gap-3">
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              type="email"
              autoComplete="email"
              className={FIELD}
            />
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && submit()}
              placeholder="Password (min 6 chars)"
              type="password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              className={FIELD}
            />

            {error && (
              <p className="m-0 text-[13px] text-danger">{error}</p>
            )}

            <button
              onClick={submit}
              disabled={busy}
              className="ma-cta mt-1 flex w-full cursor-pointer items-center justify-center gap-[9px] rounded-[12px] border-none p-[13px] font-display text-[15px] font-semibold text-[#06121f] disabled:opacity-60"
            >
              <span>{busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Sign up'}</span>
              {!busy && <ArrowIcon size={16} />}
            </button>
          </div>

          <div className="mt-4 text-center text-[13px] text-muted">
            {mode === 'login' ? "Don't have an account? " : 'Already have one? '}
            <button
              onClick={() => {
                setMode(mode === 'login' ? 'signup' : 'login');
                setError(null);
              }}
              className="cursor-pointer border-none bg-transparent font-semibold text-accent"
            >
              {mode === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </div>
        </div>

        <button
          onClick={continueAsGuest}
          className="ma-chip mx-auto mt-4 block cursor-pointer rounded-full border border-white/[0.09] bg-white/[0.025] px-[14px] py-[8px] text-[13px] text-[#aeb5bd]"
        >
          Continue as guest
        </button>
      </div>
    </div>
  );
}
