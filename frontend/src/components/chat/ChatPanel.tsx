import { useEffect, useRef } from 'react';
import type { ChatMessage } from '@/types';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import Suggestions from './Suggestions';
import ChatInput from './ChatInput';

interface ChatPanelProps {
  messages: ChatMessage[];
  typing: boolean;
  draft: string;
  onDraft: (v: string) => void;
  onSend: () => void;
  onAsk: (q: string) => void;
}

export default function ChatPanel({
  messages,
  typing,
  draft,
  onDraft,
  onSend,
  onAsk,
}: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Keep the transcript pinned to the latest message / typing indicator.
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages.length, typing]);

  return (
    <div className="mt-[22px] animate-fadeup">
      <div className="overflow-hidden rounded-[18px] border border-white/[0.08] bg-gradient-to-b from-white/[0.03] to-white/[0.01] shadow-[0_30px_70px_-34px_rgba(0,0,0,0.85)]">
        <div
          ref={scrollRef}
          className="flex max-h-[560px] flex-col gap-[18px] overflow-y-auto px-[22px] pt-[22px] pb-[6px]"
        >
          {messages.map((m, i) => (
            <MessageBubble key={i} message={m} />
          ))}
          {typing && <TypingIndicator />}
        </div>

        <div className="border-t border-white/[0.07] bg-black/20 px-4 py-[14px]">
          {!typing && <Suggestions onAsk={onAsk} />}
          <ChatInput draft={draft} onDraft={onDraft} onSend={onSend} />
        </div>
      </div>
      <p className="mx-0 mt-[14px] text-center text-[11.5px] text-[#4d545c]">
        Answers are generated from indexed manuals. Verify safety-critical
        procedures against the printed manual.
      </p>
    </div>
  );
}
