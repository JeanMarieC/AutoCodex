import { EXAMPLES, type ExampleCar } from '@/api/endpoints';

interface ExampleChipsProps {
  onPick: (ex: ExampleCar) => void;
}

export default function ExampleChips({ onPick }: ExampleChipsProps) {
  return (
    <div className="mt-5 flex flex-wrap items-center justify-center gap-[10px]">
      <span className="text-[13px] text-[#5d646d]">Try</span>
      {EXAMPLES.map((ex) => (
        <button
          key={ex.label}
          onClick={() => onPick(ex)}
          className="ma-chip cursor-pointer rounded-full border border-white/[0.09] bg-white/[0.025] px-[13px] py-[7px] text-[13px] text-[#aeb5bd]"
        >
          {ex.label}
        </button>
      ))}
    </div>
  );
}
