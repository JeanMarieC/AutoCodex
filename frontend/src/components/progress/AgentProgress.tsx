import type { ManualRef, PipelineStep as Step } from '@/types';
import UploadDropzone from '@/components/UploadDropzone';
import PipelineStep from './PipelineStep';
import ManualsIndexed from './ManualsIndexed';

interface AgentProgressProps {
  steps: Step[];
  manuals: ManualRef[];
  onRetry: () => void;
  onResetCar: () => void;
  onUpload: (file: File) => Promise<void>;
}

export default function AgentProgress({
  steps,
  manuals,
  onRetry,
  onResetCar,
  onUpload,
}: AgentProgressProps) {
  const doneCount = steps.filter((s) => s.status === 'done').length;
  const failed = steps.some((s) => s.status === 'failed');
  const allDone = doneCount === steps.length;
  const running = !failed && !allDone;

  const title = failed ? 'Manual not found' : allDone ? 'Vehicle indexed' : 'Agent at work';
  const count = failed ? 'Stopped' : `${doneCount} / ${steps.length} complete`;

  return (
    <div className="mt-[18px] rounded-[18px] border border-white/[0.08] bg-gradient-to-b from-white/[0.035] to-white/[0.012] px-6 pt-6 pb-5 shadow-[0_30px_70px_-34px_rgba(0,0,0,0.85)] animate-fadeup">
      <div className="mb-[22px] flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          {running && (
            <span className="inline-block h-[15px] w-[15px] animate-spin-slow rounded-full border-2 border-accent/25 border-t-accent" />
          )}
          <h2 className="m-0 font-display text-[17px] font-semibold tracking-[-0.01em]">
            {title}
          </h2>
        </div>
        <span className="text-[12px] tabular-nums tracking-[0.04em] text-[#6c747d]">
          {count}
        </span>
      </div>

      {steps.map((s, i) => (
        <PipelineStep
          key={s.id}
          step={s}
          number={i + 1}
          isLast={i === steps.length - 1}
          onRetry={onRetry}
          onResetCar={onResetCar}
        />
      ))}

      {allDone && manuals.length > 0 && <ManualsIndexed manuals={manuals} />}

      {failed && (
        <div className="mt-1 border-t border-white/[0.07] pt-4">
          <p className="mb-1 text-[12.5px] text-muted">
            Couldn't find a manual automatically — upload your own PDF to continue:
          </p>
          <UploadDropzone onUpload={onUpload} />
        </div>
      )}
    </div>
  );
}
