/**
 * Shared API types — the contract between the React frontend and the
 * FastAPI backend. Mirrors the Pydantic schemas in backend/app/api/schemas.
 * Filled out fully in Phase 1; kept minimal here for scaffolding.
 */

export interface Car {
  id: string;
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
  detail?: string;
}

/** Streamed over SSE as the agent graph advances. */
export interface AgentProgressEvent {
  carId: string;
  step: PipelineStepId;
  status: StepStatus;
  detail?: string;
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
