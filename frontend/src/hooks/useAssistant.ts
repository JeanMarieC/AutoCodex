/**
 * The app's state machine: input → progress → chat. Drives the pipeline and
 * chat entirely through the API client layer (src/api/endpoints), so it works
 * identically against mocks now and the real SSE backend in Phase 2.
 *
 * Mirrors the behaviour of the original Claude Design prototype component.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  getInitialSteps,
  sendChat,
  streamIngestion,
  type ExampleCar,
} from '@/api/endpoints';
import { uploadManual as uploadManualApi } from '@/api/manuals';
import { analyzeDashboard as analyzeDashboardApi } from '@/api/vision';
import type { Car, ChatMessage, ManualRef, PipelineStep, StreamHandle } from '@/types';

export type Phase = 'input' | 'progress' | 'chat';

const VALIDATE_INDEX = 2; // retry resumes at the validation stage

export function useAssistant() {
  const [phase, setPhase] = useState<Phase>('input');
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [year, setYear] = useState('');
  const [car, setCar] = useState<Car | null>(null);

  const [steps, setSteps] = useState<PipelineStep[]>(getInitialSteps);
  const [manuals, setManuals] = useState<ManualRef[]>([]);
  const [failed, setFailed] = useState(false);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState('');
  const [typing, setTyping] = useState(false);

  const streamRef = useRef<StreamHandle | null>(null);

  // Cancel any in-flight stream on unmount.
  useEffect(() => () => streamRef.current?.cancel(), []);

  const onYear = useCallback(
    (v: string) => setYear(v.replace(/[^0-9]/g, '').slice(0, 4)),
    [],
  );

  const handleEvent = useCallback((e: import('@/types').IngestionEvent) => {
    switch (e.type) {
      case 'step':
        setSteps((prev) =>
          prev.map((s) =>
            s.id === e.step ? { ...s, status: e.status, detail: e.detail } : s,
          ),
        );
        if (e.status === 'failed') setFailed(true);
        break;
      case 'manuals':
        setManuals(e.manuals);
        break;
      case 'complete':
        setPhase('chat');
        setMessages([{ role: 'assistant', text: e.greeting, citations: null }]);
        break;
      case 'error':
        setFailed(true);
        break;
    }
  }, []);

  const findManual = useCallback(() => {
    const target: Car = {
      make: make.trim() || 'Mercedes-Benz',
      model: model.trim() || 'C200',
      year: year.trim() || '1998',
    };
    setMake(target.make);
    setModel(target.model);
    setYear(target.year);
    setCar(target);
    setFailed(false);
    setManuals([]);
    setMessages([]);
    setSteps(getInitialSteps());
    setPhase('progress');

    streamRef.current?.cancel();
    streamRef.current = streamIngestion(target, { onEvent: handleEvent });
  }, [make, model, year, handleEvent]);

  const retry = useCallback(() => {
    if (!car) return;
    setFailed(false);
    // Mark earlier stages done, re-run from validation — and force success.
    setSteps((prev) =>
      prev.map((s, i) => {
        if (i < VALIDATE_INDEX) return { ...s, status: 'done' };
        return { ...s, status: i === VALIDATE_INDEX ? 'active' : 'pending' };
      }),
    );
    streamRef.current?.cancel();
    streamRef.current = streamIngestion(
      car,
      { onEvent: handleEvent },
      { fromStep: VALIDATE_INDEX, forceSuccess: true },
    );
  }, [car, handleEvent]);

  const resetCar = useCallback(() => {
    streamRef.current?.cancel();
    streamRef.current = null;
    setPhase('input');
    setCar(null);
    setSteps(getInitialSteps());
    setManuals([]);
    setFailed(false);
    setMessages([]);
    setDraft('');
    setTyping(false);
  }, []);

  const fillExample = useCallback((ex: ExampleCar) => {
    setMake(ex.make);
    setModel(ex.model);
    setYear(ex.year);
  }, []);

  // Upload a user-supplied PDF. Used on the hero (always available) and when
  // the agent couldn't fetch a manual. Indexes it, then drops into chat.
  const uploadManual = useCallback(
    async (file: File) => {
      const target: Car = car ?? {
        make: make.trim() || 'Mercedes-Benz',
        model: model.trim() || 'C200',
        year: year.trim() || '1998',
      };
      setMake(target.make);
      setModel(target.model);
      setYear(target.year);
      setCar(target);
      streamRef.current?.cancel();

      const res = await uploadManualApi(target, file);
      setManuals((prev) => [...prev, { name: res.name, meta: res.meta }]);
      setMessages([{ role: 'assistant', text: res.greeting, citations: null }]);
      setFailed(false);
      setPhase('chat');
    },
    [car, make, model, year],
  );

  const ask = useCallback(
    (text: string) => {
      const t = text.trim();
      if (!t || typing || !car) return;
      setMessages((prev) => [...prev, { role: 'user', text: t, citations: null }]);
      setDraft('');
      setTyping(true);
      sendChat(car, t).then((reply) => {
        setTyping(false);
        setMessages((prev) => [...prev, reply]);
      });
    },
    [typing, car],
  );

  const send = useCallback(() => ask(draft), [ask, draft]);

  // Snap a dashboard photo → VLM identifies the light → grounded answer.
  const analyzeDashboard = useCallback(
    async (file: File) => {
      if (!car || typing) return;
      setMessages((prev) => [...prev, { role: 'user', text: '📷 Dashboard photo', citations: null }]);
      setTyping(true);
      try {
        const res = await analyzeDashboardApi(car, file);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            text: `Detected: ${res.identification}\n\n${res.text}`,
            citations: res.citations ?? null,
          },
        ]);
      } catch {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            text: "I couldn't read that photo. Make sure the vision model is running, then try a clear, well-lit shot of the dashboard.",
            citations: null,
          },
        ]);
      } finally {
        setTyping(false);
      }
    },
    [car, typing],
  );

  return {
    phase,
    make,
    model,
    year,
    car,
    setMake,
    setModel,
    onYear,
    steps,
    manuals,
    failed,
    findManual,
    retry,
    resetCar,
    fillExample,
    uploadManual,
    messages,
    draft,
    setDraft,
    typing,
    ask,
    send,
    analyzeDashboard,
  };
}

export type AssistantApi = ReturnType<typeof useAssistant>;
