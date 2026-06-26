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
    messages,
    draft,
    setDraft,
    typing,
    ask,
    send,
  };
}

export type AssistantApi = ReturnType<typeof useAssistant>;
