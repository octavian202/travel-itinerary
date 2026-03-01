/**
 * API client for City Break Planner backend.
 * Set EXPO_PUBLIC_API_URL or use default (localhost; use your machine IP for device).
 */
import axios from 'axios';
import type { ItineraryResponse, RouteGeometryResponse } from '../types/api';

const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // generation can take 5–15s
  headers: { 'Content-Type': 'application/json' },
});

export interface GeneratePayload {
  city_name: string;
  days: number;
  pace: 'relaxed' | 'moderate' | 'fast';
}

export async function generateItinerary(payload: GeneratePayload): Promise<ItineraryResponse> {
  const { data } = await client.post<ItineraryResponse>('/api/v1/itineraries/generate', payload);
  return data;
}

export async function getItinerary(id: string): Promise<ItineraryResponse> {
  const { data } = await client.get<ItineraryResponse>(`/api/v1/itineraries/${id}`);
  return data;
}

export async function getRouteGeometry(dailyRouteId: string): Promise<RouteGeometryResponse> {
  const { data } = await client.get<RouteGeometryResponse>(`/api/v1/routes/${dailyRouteId}/geometry`);
  return data;
}
