/**
 * In-memory fake backend. Replays the Claude Design prototype's behaviour —
 * staged pipeline with realistic timings, a deliberately-failing vehicle
 * (Toyota Hilux), and canned, classified Q&A answers — so the UI runs
 * end-to-end with no server. Phase 2 swaps this for the real FastAPI/SSE
 * backend behind the identical client interface in ./endpoints.
 *
 * Ported from design-reference logic in Manual Assistant.dc.html.
 */
import type {
  Car,
  ChatMessage,
  Citation,
  IngestionEvent,
  ManualRef,
  StreamHandle,
  StreamHandlers,
} from '@/types';

interface StepDef {
  id: import('@/types').PipelineStepId;
  label: string;
  pending: string;
  active: string;
  done: (carLabel: string) => string;
  fail?: string;
}

export const STEP_DEFS: StepDef[] = [
  {
    id: 'parse',
    label: 'Parsing vehicle',
    pending: 'Awaiting vehicle details',
    active: 'Normalizing make, model and production year…',
    done: (c) => `Identified ${c} · chassis W202 generation`,
  },
  {
    id: 'search',
    label: 'Searching sources',
    pending: 'ManualsLib · Archive.org · OEM portals',
    active: 'Querying ManualsLib and Archive.org for matching manuals…',
    done: () => '7 candidate documents found across 3 sources',
  },
  {
    id: 'validate',
    label: 'Validating & ranking results',
    pending: 'Cross-checking model & year coverage',
    active: 'Scoring candidates by edition, language and completeness…',
    done: () => 'Ranked by relevance — 2 official manuals selected',
    fail: 'No candidate scored above the reliability threshold for this exact model year.',
  },
  {
    id: 'fetch',
    label: 'Fetching manual PDF',
    pending: 'Download & verify integrity',
    active: 'Downloading 2 PDFs (48.2 MB) and verifying checksums…',
    done: () => '2 PDFs retrieved · 612 pages total',
  },
  {
    id: 'ingest',
    label: 'Ingesting & indexing',
    pending: 'Chunk · embed · build vector index',
    active: 'Chunking pages, embedding and building the vector index…',
    done: () => '1,438 chunks embedded · index ready',
  },
];

const STEP_DURATIONS = [900, 1500, 1400, 1600, 1700];

export const MANUALS: ManualRef[] = [
  { name: "Owner's Manual", meta: '1998 · 312 pp' },
  { name: 'Workshop Manual', meta: 'W202 · 300 pp' },
];

export interface ExampleCar extends Car {
  label: string;
  fail?: boolean;
}

export const EXAMPLES: ExampleCar[] = [
  { label: 'Mercedes-Benz C200 · 1998', make: 'Mercedes-Benz', model: 'C200', year: '1998' },
  { label: 'BMW 320i · 2012', make: 'BMW', model: '320i', year: '2012' },
  { label: 'Toyota Hilux · 2009 (no manual)', make: 'Toyota', model: 'Hilux', year: '2009', fail: true },
];

export const SUGGESTIONS: string[] = [
  'What oil type and capacity does it take?',
  'How often should I change the transmission fluid?',
  'What does the yellow ABS warning light mean?',
];

interface Answer {
  text: string;
  citations: Citation[];
}

const ANSWERS: Record<string, Answer> = {
  oil: {
    text: "For the 1998 C200 (M111 engine), use SAE 5W-40 fully synthetic oil meeting MB 229.1.\n\nTotal capacity including the filter is 5.5 litres. Mercedes specifies an oil and filter change every 10,000 km or 12 months, whichever comes first.",
    citations: [
      { tag: "Owner's Manual", ref: 'p.124' },
      { tag: 'Workshop Manual', ref: 'Engine · Lubrication' },
    ],
  },
  trans: {
    text: "The 5-speed automatic (722.6) uses ATF Dexron III. Under normal driving Mercedes lists the fluid as a lifetime fill, but for vehicles of this age a service is recommended every 60,000 km.\n\nThe procedure requires dropping the pan, replacing the filter and refilling ~5.5 L, then checking level at operating temperature.",
    citations: [
      { tag: 'Workshop Manual', ref: 'Transmission · 722.6' },
      { tag: "Owner's Manual", ref: 'p.201' },
    ],
  },
  abs: {
    text: "A steady yellow ABS lamp means the Anti-lock Braking System has detected a fault and disabled itself — your normal brakes still work, but ABS assistance is off.\n\nMost common causes on the W202 are a dirty or failing wheel-speed sensor or low brake fluid. Have the fault codes read before driving hard.",
    citations: [
      { tag: "Owner's Manual", ref: 'p.88 · Warning Lamps' },
      { tag: 'Workshop Manual', ref: 'Brakes · ABS' },
    ],
  },
  default: {
    text: "Based on the indexed manuals for your vehicle, here's what I found. The relevant procedure and torque specifications are covered in the workshop manual section cited below. Always use the values for your exact engine variant.",
    citations: [{ tag: 'Workshop Manual', ref: 'General · Specs' }],
  },
};

function classify(q: string): keyof typeof ANSWERS {
  const s = q.toLowerCase();
  if (/oil|lubric/.test(s)) return 'oil';
  if (/transmission|gearbox|atf|fluid/.test(s)) return 'trans';
  if (/abs|warning|light|lamp|brake/.test(s)) return 'abs';
  return 'default';
}

const carLabelOf = (c: Car) => `${c.make} ${c.model} · ${c.year}`;

/**
 * Drive the fake pipeline. Emits `step` events as each stage moves through
 * active → done, then `manuals` + `complete`, or `error` on the failing car.
 * `fromStep` lets the retry path resume at the validation stage.
 */
export function mockStreamIngestion(
  car: Car,
  handlers: StreamHandlers,
  opts: { fromStep?: number; forceSuccess?: boolean } = {},
): StreamHandle {
  const timers: ReturnType<typeof setTimeout>[] = [];
  let cancelled = false;
  const carLabel = carLabelOf(car);
  const shouldFail = !opts.forceSuccess && /hilux/i.test(car.model);
  const start = opts.fromStep ?? 0;

  const at = (fn: () => void, ms: number) => {
    timers.push(setTimeout(fn, ms));
  };

  const emit = (e: IngestionEvent) => {
    if (!cancelled) handlers.onEvent(e);
  };

  const runStep = (i: number) => {
    if (cancelled) return;
    const def = STEP_DEFS[i];
    emit({ type: 'step', step: def.id, status: 'active', detail: def.active });

    at(() => {
      if (shouldFail && def.id === 'validate') {
        emit({ type: 'step', step: def.id, status: 'failed', detail: def.fail! });
        emit({ type: 'error', step: def.id, message: def.fail! });
        return;
      }
      emit({ type: 'step', step: def.id, status: 'done', detail: def.done(carLabel) });

      if (i + 1 < STEP_DEFS.length) {
        runStep(i + 1);
      } else {
        emit({ type: 'manuals', manuals: MANUALS });
        at(() => {
          emit({
            type: 'complete',
            greeting: `Your ${car.make} ${car.model} (${car.year}) is indexed and ready. I've read the Owner's and Workshop manuals — ask me anything about maintenance, fluids, warning lights or repair procedures.`,
          });
        }, 850);
      }
    }, STEP_DURATIONS[i]);
  };

  runStep(start);

  return {
    cancel: () => {
      cancelled = true;
      timers.forEach(clearTimeout);
    },
  };
}

/** Fake RAG answer with ~1.4s of "thinking". */
export function mockSendChat(_car: Car, text: string): Promise<ChatMessage> {
  const ans = ANSWERS[classify(text)];
  return new Promise((resolve) => {
    setTimeout(
      () => resolve({ role: 'assistant', text: ans.text, citations: ans.citations }),
      1400,
    );
  });
}
