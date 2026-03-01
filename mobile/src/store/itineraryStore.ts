/**
 * Zustand store for itinerary flow: input -> loading -> ready/error.
 */
import { create } from 'zustand';
import type { ItineraryResponse } from '../types/api';
import { generateItinerary } from '../api/client';

type Status = 'idle' | 'loading' | 'ready' | 'error';

interface ItineraryState {
  status: Status;
  itinerary: ItineraryResponse | null;
  error: string | null;
  generate: (cityName: string, days: number, pace: 'relaxed' | 'moderate' | 'fast') => Promise<void>;
  reset: () => void;
  setItinerary: (itinerary: ItineraryResponse | null) => void;
}

export const useItineraryStore = create<ItineraryState>((set) => ({
  status: 'idle',
  itinerary: null,
  error: null,
  generate: async (cityName, days, pace) => {
    set({ status: 'loading', error: null });
    try {
      const itinerary = await generateItinerary({ city_name: cityName, days, pace });
      set({ status: 'ready', itinerary, error: null });
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Failed to generate itinerary';
      set({ status: 'error', error: message, itinerary: null });
    }
  },
  reset: () => set({ status: 'idle', itinerary: null, error: null }),
  setItinerary: (itinerary) => set({ itinerary }),
}));
