import { useRef, useState } from 'react';

interface UploadDropzoneProps {
  onUpload: (file: File) => Promise<void>;
  /** Compact = a single link/button (e.g. in the hero); full = a drop area. */
  compact?: boolean;
}

export default function UploadDropzone({ onUpload, compact }: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  const handle = async (file: File | undefined) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      setError('Please choose a PDF file.');
      return;
    }
    setError(null);
    setBusy(true);
    try {
      await onUpload(file);
    } catch {
      setError('Upload failed. Please try again.');
    } finally {
      setBusy(false);
    }
  };

  const pick = () => inputRef.current?.click();

  const input = (
    <input
      ref={inputRef}
      type="file"
      accept="application/pdf,.pdf"
      hidden
      onChange={(e) => handle(e.target.files?.[0])}
    />
  );

  if (compact) {
    return (
      <>
        {input}
        <button
          onClick={pick}
          disabled={busy}
          className="ma-chip cursor-pointer rounded-full border border-white/[0.09] bg-white/[0.025] px-[13px] py-[7px] text-[13px] text-[#aeb5bd] disabled:opacity-60"
        >
          {busy ? 'Indexing your PDF…' : 'Have the manual? Upload a PDF'}
        </button>
        {error && <span className="text-[12px] text-danger">{error}</span>}
      </>
    );
  }

  return (
    <div className="mt-1">
      {input}
      <div
        onClick={pick}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handle(e.dataTransfer.files?.[0]);
        }}
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-[14px] border border-dashed px-5 py-7 text-center transition ${
          dragging ? 'border-accent bg-accent/[0.06]' : 'border-white/15 bg-white/[0.02]'
        }`}
      >
        {busy ? (
          <span className="inline-block h-5 w-5 animate-spin-slow rounded-full border-2 border-accent/25 border-t-accent" />
        ) : (
          <span className="text-[26px] leading-none text-accent">↑</span>
        )}
        <span className="text-[13.5px] font-semibold text-ink-soft">
          {busy ? 'Reading & indexing your manual…' : 'Upload your manual (PDF)'}
        </span>
        <span className="text-[12px] text-muted-2">
          Drop a file here or click to browse · max 30 MB
        </span>
      </div>
      {error && <p className="m-0 mt-2 text-center text-[12.5px] text-danger">{error}</p>}
    </div>
  );
}
