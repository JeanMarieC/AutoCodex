import { useRef } from 'react';
import { CameraIcon, SendIcon } from '@/components/icons';

interface ChatInputProps {
  draft: string;
  onDraft: (v: string) => void;
  onSend: () => void;
  onPhoto: (file: File) => void;
}

export default function ChatInput({ draft, onDraft, onSend, onPhoto }: ChatInputProps) {
  const fileRef = useRef<HTMLInputElement>(null);

  return (
    <div className="flex items-end gap-[10px]">
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        hidden
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onPhoto(f);
          e.target.value = '';
        }}
      />
      <button
        onClick={() => fileRef.current?.click()}
        title="Snap a dashboard warning light"
        className="ma-chip flex h-[46px] w-[46px] flex-none cursor-pointer items-center justify-center rounded-[12px] border border-white/10 bg-white/[0.03] text-[#aeb5bd]"
      >
        <CameraIcon />
      </button>
      <input
        value={draft}
        onChange={(e) => onDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') onSend();
        }}
        placeholder="Ask about maintenance, fluids, warning lights…"
        className="ma-field flex-1 rounded-[12px] bg-black/[0.35] px-[15px] py-[13px] text-[14.5px]"
      />
      <button
        onClick={onSend}
        className="ma-send flex h-[46px] w-[46px] flex-none cursor-pointer items-center justify-center rounded-[12px] border-none text-[#06121f]"
      >
        <SendIcon />
      </button>
    </div>
  );
}
