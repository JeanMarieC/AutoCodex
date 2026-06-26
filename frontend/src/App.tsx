import Header from '@/components/Header';
import HeroInput from '@/components/hero/HeroInput';
import AgentProgress from '@/components/progress/AgentProgress';
import ChatPanel from '@/components/chat/ChatPanel';
import AuthScreen from '@/auth/AuthScreen';
import { useAuth } from '@/auth/AuthContext';
import { useAssistant } from '@/hooks/useAssistant';

export default function App() {
  const auth = useAuth();
  const a = useAssistant();
  const carLabel = `${a.make} ${a.model} · ${a.year}`;

  // Guests and signed-in users can use the app; otherwise show the auth screen.
  if (!auth.ready) return <AuthScreen />;

  return (
    <div
      className="min-h-screen px-5 pb-[120px]"
      style={{
        background:
          'radial-gradient(1100px 520px at 50% -120px, rgba(111,177,255,0.10), transparent 60%), #08090b',
      }}
    >
      <Header
        showCarBadge={a.phase !== 'input'}
        carLabel={carLabel}
        onResetCar={a.resetCar}
        email={auth.email}
        onLogout={auth.logout}
        onSignIn={auth.logout}
      />

      <div className="mx-auto max-w-[880px]">
        {a.phase === 'input' && (
          <HeroInput
            make={a.make}
            model={a.model}
            year={a.year}
            onMake={a.setMake}
            onModel={a.setModel}
            onYear={a.onYear}
            onSubmit={a.findManual}
            onPickExample={a.fillExample}
            onUpload={a.uploadManual}
          />
        )}

        {a.phase === 'progress' && (
          <AgentProgress
            steps={a.steps}
            manuals={a.manuals}
            onRetry={a.retry}
            onResetCar={a.resetCar}
            onUpload={a.uploadManual}
          />
        )}

        {a.phase === 'chat' && (
          <ChatPanel
            messages={a.messages}
            typing={a.typing}
            draft={a.draft}
            onDraft={a.setDraft}
            onSend={a.send}
            onAsk={a.ask}
          />
        )}
      </div>
    </div>
  );
}
