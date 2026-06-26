import type { ManualRef } from '@/types';

export default function ManualsIndexed({ manuals }: { manuals: ManualRef[] }) {
  return (
    <div className="mt-1 flex flex-wrap items-center gap-[9px] border-t border-white/[0.07] pt-4 animate-fadeup">
      <span className="mr-[2px] text-[10px] font-bold uppercase tracking-[0.16em] text-[#6c747d]">
        Manuals indexed
      </span>
      {manuals.map((m) => (
        <span
          key={m.name}
          className="inline-flex items-center gap-2 rounded-full border border-accent/[0.22] bg-accent/[0.07] px-[13px] py-[7px] text-[12.5px] font-semibold text-[#cfe2ff]"
        >
          <span className="text-success">✓</span>
          {m.name}
          <span className="font-medium text-[#6c747d]">· {m.meta}</span>
        </span>
      ))}
    </div>
  );
}
