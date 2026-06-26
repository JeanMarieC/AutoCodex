import type { CSSProperties } from 'react';
import type { PipelineStep as Step } from '@/types';

interface PipelineStepProps {
  step: Step;
  number: number;
  isLast: boolean;
  onRetry: () => void;
  onResetCar: () => void;
}

export default function PipelineStep({
  step,
  number,
  isLast,
  onRetry,
  onResetCar,
}: PipelineStepProps) {
  const { status, label, detail } = step;
  const isActive = status === 'active';
  const isDone = status === 'done';
  const isFailed = status === 'failed';

  const dotStyle: CSSProperties = {
    flex: 'none',
    width: 24,
    height: 24,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 12,
    fontWeight: 700,
    transition: 'all 0.3s',
    ...(isDone
      ? {
          background: 'rgba(111,220,155,0.14)',
          border: '1px solid rgba(111,220,155,0.5)',
          color: '#6fdc9b',
        }
      : isActive
        ? {
            background: 'rgba(111,177,255,0.16)',
            border: '1px solid #6fb1ff',
            color: '#6fb1ff',
            boxShadow: '0 0 0 4px rgba(111,177,255,0.12)',
          }
        : isFailed
          ? {
              background: 'rgba(239,138,107,0.14)',
              border: '1px solid rgba(239,138,107,0.55)',
              color: '#ef8a6b',
            }
          : {
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.12)',
              color: '#4d545c',
            }),
  };

  // done → ✓, failed → !, active → spinner glow (empty), pending → number
  const dotIcon = isDone ? '✓' : isFailed ? '!' : isActive ? '' : number;

  const labelStyle: CSSProperties = {
    fontFamily: "'Sora', sans-serif",
    fontSize: 14.5,
    fontWeight: isActive || isFailed ? 600 : 500,
    color: isDone ? '#dfe4ea' : isActive ? '#ffffff' : isFailed ? '#f0b8a6' : '#6c747d',
    transition: 'color 0.3s',
  };

  const detailStyle: CSSProperties = {
    margin: '5px 0 0',
    fontSize: 13,
    lineHeight: 1.5,
    color: isFailed ? '#d99478' : isActive ? '#aeb5bd' : '#5d646d',
  };

  const lineStyle: CSSProperties = {
    width: 2,
    flex: 1,
    minHeight: 18,
    margin: '5px 0',
    borderRadius: 2,
    background: isDone ? 'rgba(111,220,155,0.4)' : 'rgba(255,255,255,0.08)',
    transition: 'background 0.3s',
  };

  return (
    <div className="flex gap-4">
      <div className="flex w-6 flex-none flex-col items-center">
        <div style={dotStyle}>{dotIcon}</div>
        {!isLast && <div style={lineStyle} />}
      </div>
      <div className="min-w-0 flex-1 pb-[18px]">
        <div className="flex flex-wrap items-center gap-[10px]">
          <span style={labelStyle}>{label}</span>
          {isActive && (
            <span className="rounded-full border border-accent/25 bg-accent/10 px-2 py-[2px] text-[9.5px] font-bold uppercase tracking-[0.14em] text-accent">
              Working
            </span>
          )}
          {isFailed && (
            <span className="rounded-full border border-danger/30 bg-danger/10 px-2 py-[2px] text-[9.5px] font-bold uppercase tracking-[0.14em] text-danger">
              Failed
            </span>
          )}
        </div>
        <p style={detailStyle}>{detail}</p>

        {isActive && (
          <div className="mt-[11px] h-[3px] max-w-[280px] overflow-hidden rounded-[3px] bg-white/[0.06]">
            <div
              className="h-full w-[45%] rounded-[3px] animate-shimmer"
              style={{
                background:
                  'linear-gradient(90deg,rgba(111,177,255,0),#6fb1ff,rgba(111,177,255,0))',
                backgroundSize: '200% 100%',
              }}
            />
          </div>
        )}

        {isFailed && (
          <div className="mt-3 flex flex-wrap items-center gap-[9px]">
            <button
              onClick={onRetry}
              className="inline-flex cursor-pointer items-center gap-[7px] rounded-[10px] border-none bg-gradient-to-b from-[#cfe2ff] to-[#9cc4ff] px-[15px] py-2 text-[13px] font-semibold text-[#0a0b0e]"
            >
              ↻ Retry search
            </button>
            <button
              onClick={onResetCar}
              className="cursor-pointer rounded-[10px] border border-white/10 bg-white/[0.04] px-[15px] py-2 text-[13px] font-semibold text-[#aeb4bc]"
            >
              Try another vehicle
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
