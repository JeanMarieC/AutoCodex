/**
 * Phase 0 placeholder. The real three-phase UI (Hero → Agent Progress → Chat)
 * is built in Phase 1 by recreating design-reference/Manual Assistant.dc.html.
 * This screen just confirms the Tailwind design tokens and fonts are wired up.
 */
export default function App() {
  return (
    <div
      className="min-h-screen px-5 pb-32"
      style={{
        background:
          'radial-gradient(1100px 520px at 50% -120px, rgba(111,177,255,0.10), transparent 60%), #08090b',
      }}
    >
      <header className="mx-auto flex max-w-[880px] items-center gap-3 pt-7">
        <div className="flex h-[30px] w-[30px] items-center justify-center rounded-lg border border-white/10 bg-gradient-to-br from-[#2a2f37] to-[#0f1115] shadow-[0_0_18px_rgba(111,177,255,0.18)]">
          <div className="h-[13px] w-[13px] rotate-[35deg] rounded-full border-2 border-accent border-t-transparent" />
        </div>
        <span className="font-display text-[13px] font-semibold uppercase tracking-[0.14em]">
          Manual<span className="text-accent">.ai</span>
        </span>
      </header>

      <main className="mx-auto mt-24 max-w-[880px] text-center animate-fadeup">
        <h1 className="font-display text-5xl font-semibold tracking-tight">
          Scaffold ready.
        </h1>
        <p className="mx-auto mt-4 max-w-[480px] text-muted">
          Phase 0 complete — Vite + React + TS + Tailwind v4 with the automotive
          dark theme. The full UI lands in Phase 1.
        </p>
      </main>
    </div>
  );
}
