import type { ChatMessage } from '@/types';

export default function MessageBubble({ message }: { message: ChatMessage }) {
  const isAssistant = message.role === 'assistant';
  const hasCitations = !!(message.citations && message.citations.length);

  return (
    <div className={`flex ${isAssistant ? 'justify-start' : 'justify-end'}`}>
      <div
        className={
          isAssistant
            ? 'max-w-[82%] rounded-[16px_16px_16px_4px] border border-white/[0.09] bg-white/[0.045] px-[17px] py-[15px]'
            : 'max-w-[78%] rounded-[16px_16px_4px_16px] border border-accent/40 bg-gradient-to-b from-[#5a93e0] to-[#3f6fae] px-4 py-3 shadow-[0_8px_24px_-12px_rgba(63,111,174,0.7)]'
        }
      >
        {isAssistant && (
          <div className="mb-[9px] flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded-[6px] bg-gradient-to-br from-accent to-[#3f6fae] font-display text-[11px] font-extrabold text-[#06121f]">
              M
            </span>
            <span className="text-[10.5px] font-bold uppercase tracking-[0.1em] text-[#6c747d]">
              Manual.ai
            </span>
          </div>
        )}

        <p
          className="m-0 whitespace-pre-wrap text-[14.5px] leading-[1.62]"
          style={{ color: isAssistant ? '#dde3ea' : '#f4f8ff' }}
        >
          {message.text}
        </p>

        {hasCitations && (
          <div className="mt-[13px] flex flex-wrap gap-2 border-t border-dashed border-white/10 pt-3">
            {message.citations!.map((c, i) => (
              <span
                key={`${c.tag}-${c.ref}-${i}`}
                className="ma-chip inline-flex cursor-default items-center gap-[7px] rounded-[8px] border border-white/10 bg-white/[0.04] py-[5px] pr-[10px] pl-[7px] text-[11.5px] text-[#c4ccd4]"
              >
                <span className="rounded-[5px] bg-accent/[0.12] px-[6px] py-[2px] text-[9px] font-bold uppercase tracking-[0.08em] text-accent">
                  {c.tag}
                </span>
                <span className="font-semibold text-[#e6ebf1]">{c.ref}</span>
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
