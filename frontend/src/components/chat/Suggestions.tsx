import { SUGGESTIONS } from '@/api/endpoints';

export default function Suggestions({ onAsk }: { onAsk: (q: string) => void }) {
  return (
    <div className="mb-3 flex flex-wrap gap-2">
      {SUGGESTIONS.map((q) => (
        <button
          key={q}
          onClick={() => onAsk(q)}
          className="ma-chip cursor-pointer rounded-full border border-white/10 bg-white/[0.03] px-3 py-[7px] text-[12.5px] text-[#b6bdc5]"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
