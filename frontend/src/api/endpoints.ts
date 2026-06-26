/**
 * The API the UI talks to. One interface, two implementations:
 *   - mocks (default in Phase 1)        VITE_USE_MOCKS !== 'false'
 *   - real FastAPI/SSE backend (Phase 2)
 *
 * Components and hooks import only from here, so flipping VITE_USE_MOCKS
 * swaps the whole data layer with zero UI changes.
 */
import type {
  Car,
  ChatMessage,
  IngestionEvent,
  PipelineStep,
  StreamHandle,
  StreamHandlers,
} from '@/types';
import { BASE_URL, apiPost } from './client';
import {
  EXAMPLES,
  STEP_DEFS,
  SUGGESTIONS,
  mockSendChat,
  mockStreamIngestion,
} from './mocks';

export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS !== 'false';

export { EXAMPLES, SUGGESTIONS };
export type { ExampleCar } from './mocks';

/** The 5-step pipeline skeleton in its initial (pending) state. */
export function getInitialSteps(): PipelineStep[] {
  return STEP_DEFS.map((d) => ({
    id: d.id,
    label: d.label,
    status: 'pending',
    detail: d.pending,
  }));
}

export interface IngestionOptions {
  fromStep?: number;
  forceSuccess?: boolean;
}

/** Stream agent progress. Mock replays timings; real opens an SSE channel. */
export function streamIngestion(
  car: Car,
  handlers: StreamHandlers,
  opts: IngestionOptions = {},
): StreamHandle {
  if (USE_MOCKS) return mockStreamIngestion(car, handlers, opts);

  const params = new URLSearchParams({
    make: car.make,
    model: car.model,
    year: car.year,
  });
  if (opts.fromStep != null) params.set('from_step', String(opts.fromStep));
  const source = new EventSource(`${BASE_URL}/agent/stream?${params.toString()}`);

  source.onmessage = (e) => {
    try {
      handlers.onEvent(JSON.parse(e.data) as IngestionEvent);
    } catch (err) {
      handlers.onError?.(err);
    }
  };
  source.addEventListener('complete', () => source.close());
  source.onerror = (err) => handlers.onError?.(err);

  return { cancel: () => source.close() };
}

/** Ask a question against the indexed manuals for a car. */
export function sendChat(car: Car, text: string): Promise<ChatMessage> {
  if (USE_MOCKS) return mockSendChat(car, text);
  return apiPost<ChatMessage>('/chat', { car, message: text });
}
