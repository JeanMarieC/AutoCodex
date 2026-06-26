/**
 * Shared API types — the contract between the React frontend and the
 * FastAPI backend. Mirrors the Pydantic schemas in backend/app/api/schemas.
 *
 * The ingestion events below are exactly what the Phase 2 SSE endpoint
 * (`GET /api/agent/stream`) will emit as the LangGraph pipeline advances, so
 * the mock and the real backend are interchangeable behind the client layer.
 */

export interface Car {
  make: string;
  model: string;
  year: string;
}

/** The 5 LangGraph pipeline nodes, surfaced to the UI as progress steps. */
export type PipelineStepId =
  | 'parse'
  | 'search'
  | 'validate'
  | 'fetch'
  | 'ingest';

export type StepStatus = 'pending' | 'active' | 'done' | 'failed';

export interface PipelineStep {
  id: PipelineStepId;
  label: string;
  status: StepStatus;
  /** Human-readable status line shown under the label. */
  detail: string;
}

export interface ManualRef {
  name: string;
  meta: string;
}

export interface Citation {
  tag: string;
  ref: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
  citations?: Citation[] | null;
}

/**
 * Streamed over SSE while the agent works. A discriminated union so the UI
 * can advance steps, reveal indexed manuals and drop into chat from one feed.
 */
export type IngestionEvent =
  | { type: 'step'; step: PipelineStepId; status: StepStatus; detail: string }
  | { type: 'manuals'; manuals: ManualRef[] }
  | { type: 'complete'; greeting: string }
  | { type: 'error'; step: PipelineStepId; message: string };

export interface StreamHandlers {
  onEvent: (event: IngestionEvent) => void;
  onError?: (err: unknown) => void;
}

/** Returned by streamIngestion so callers can cancel an in-flight run. */
export interface StreamHandle {
  cancel: () => void;
}
