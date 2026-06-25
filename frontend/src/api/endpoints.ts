/**
 * Typed API calls used by the UI. Phase 1 wires these to the real backend
 * (cars, agent SSE stream, chat). For now they are placeholders so the
 * structure and imports are in place.
 *
 * The UI swaps between these and ./mocks via VITE_USE_MOCKS.
 */
export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS !== 'false';

// Implemented in Phase 1.
export {};
