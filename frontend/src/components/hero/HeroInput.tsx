import { ArrowIcon } from '@/components/icons';
import type { ExampleCar } from '@/api/endpoints';
import UploadDropzone from '@/components/UploadDropzone';
import ExampleChips from './ExampleChips';

interface HeroInputProps {
  make: string;
  model: string;
  year: string;
  onMake: (v: string) => void;
  onModel: (v: string) => void;
  onYear: (v: string) => void;
  onSubmit: () => void;
  onPickExample: (ex: ExampleCar) => void;
  onUpload: (file: File) => Promise<void>;
}

const FIELD_CLASS =
  'ma-field rounded-[11px] bg-black/[0.32] px-[13px] py-3 text-[15px]';
const FIELD_LABEL =
  'pl-[3px] text-[10.5px] font-bold uppercase tracking-[0.12em] text-[#6f7780]';

/** Radar graphic behind the headline — inline styles match the design 1:1. */
function Radar() {
  return (
    <div
      style={{
        position: 'absolute',
        top: 8,
        left: '50%',
        transform: 'translateX(-50%)',
        width: 300,
        height: 300,
        pointerEvents: 'none',
        opacity: 0.85,
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(111,177,255,0.14), transparent 62%)',
          animation: 'ma-glow 5s ease-in-out infinite',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          width: 210,
          height: 210,
          margin: '-105px 0 0 -105px',
          borderRadius: '50%',
          border: '1px solid rgba(255,255,255,0.06)',
          borderTopColor: 'rgba(111,177,255,0.22)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          width: 1.5,
          height: 88,
          background: 'linear-gradient(#6fb1ff,rgba(111,177,255,0))',
          transformOrigin: 'bottom center',
          transform: 'translate(-50%,-100%)',
          animation: 'ma-sweep 6s ease-in-out infinite',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          width: 9,
          height: 9,
          margin: '-4.5px 0 0 -4.5px',
          borderRadius: '50%',
          background: '#6fb1ff',
          boxShadow: '0 0 12px rgba(111,177,255,0.8)',
        }}
      />
    </div>
  );
}

export default function HeroInput({
  make,
  model,
  year,
  onMake,
  onModel,
  onYear,
  onSubmit,
  onPickExample,
  onUpload,
}: HeroInputProps) {
  const submitOnEnter = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') onSubmit();
  };

  return (
    <div className="animate-fadeup">
      {/* Headline */}
      <div className="relative px-0 pt-[52px] pb-[18px] text-center">
        <Radar />
        <div className="relative">
          <div className="mb-[26px] inline-flex items-center gap-2 whitespace-nowrap rounded-full border border-white/10 bg-white/[0.03] px-[13px] py-[6px] text-[11.5px] font-semibold uppercase tracking-[0.16em] text-[#9aa3ad]">
            <span className="h-[6px] w-[6px] rounded-full bg-accent animate-glow" />
            Agentic manual retrieval
          </div>
          <h1 className="m-0 mb-[18px] font-display text-[clamp(34px,6vw,58px)] font-semibold leading-[1.04] tracking-[-0.02em]">
            Ask your car
            <br />
            <span className="bg-gradient-to-b from-white to-[#9aa3ad] bg-clip-text text-transparent">
              anything.
            </span>
          </h1>
          <p className="mx-auto max-w-[480px] text-[clamp(15px,2vw,17px)] leading-[1.55] text-[#8b939d]">
            Enter your vehicle and the agent autonomously finds, fetches and
            indexes its official manuals — then answers from the source.
          </p>
        </div>
      </div>

      {/* Input card */}
      <div className="mx-auto mt-[30px] max-w-[660px] rounded-[18px] border border-white/10 bg-gradient-to-b from-white/[0.045] to-white/[0.015] p-[14px] shadow-[0_1px_0_rgba(255,255,255,0.05)_inset,0_30px_70px_-30px_rgba(0,0,0,0.85)]">
        <div
          className="grid gap-2"
          style={{ gridTemplateColumns: '1.2fr 1fr 0.7fr' }}
        >
          <label className="flex flex-col gap-[6px] text-left">
            <span className={FIELD_LABEL}>Make</span>
            <input
              value={make}
              onChange={(e) => onMake(e.target.value)}
              onKeyDown={submitOnEnter}
              placeholder="Mercedes-Benz"
              className={FIELD_CLASS}
            />
          </label>
          <label className="flex flex-col gap-[6px] text-left">
            <span className={FIELD_LABEL}>Model</span>
            <input
              value={model}
              onChange={(e) => onModel(e.target.value)}
              onKeyDown={submitOnEnter}
              placeholder="C200"
              className={FIELD_CLASS}
            />
          </label>
          <label className="flex flex-col gap-[6px] text-left">
            <span className={FIELD_LABEL}>Year</span>
            <input
              value={year}
              onChange={(e) => onYear(e.target.value)}
              onKeyDown={submitOnEnter}
              placeholder="1998"
              inputMode="numeric"
              maxLength={4}
              className={FIELD_CLASS}
            />
          </label>
        </div>
        <button
          onClick={onSubmit}
          className="ma-cta mt-2 flex w-full cursor-pointer items-center justify-center gap-[9px] rounded-[12px] border-none p-[14px] font-display text-[15px] font-semibold text-[#06121f]"
        >
          <span>Find My Manual</span>
          <ArrowIcon />
        </button>
      </div>

      <ExampleChips onPick={onPickExample} />

      <div className="mt-3 flex flex-wrap items-center justify-center gap-[10px]">
        <UploadDropzone onUpload={onUpload} compact />
      </div>
    </div>
  );
}
