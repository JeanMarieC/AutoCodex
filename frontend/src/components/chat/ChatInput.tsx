import { SendIcon } from '@/components/icons';

interface ChatInputProps {
  draft: string;
  onDraft: (v: string) => void;
  onSend: () => void;
}

export default function ChatInput({ draft, onDraft, onSend }: ChatInputProps) {
  return (
    <div className="flex items-end gap-[10px]">
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
