/** API types matching backend Pydantic schemas */

export type Pace = 'relaxed' | 'moderate' | 'fast';

export interface Coordinates {
  longitude: number;
  latitude: number;
}

export interface POIResponse {
  id: string;
  name: string;
  category: string;
  estimated_duration_minutes: number;
  coordinates: Coordinates;
}

export interface DayStops {
  day_number: number;
  daily_route_id: string;
  stops: POIResponse[];
}

export interface ItineraryResponse {
  id: string;
  location_id: string;
  days: number;
  pace: string;
  days_with_stops: DayStops[];
}

export interface RouteGeometryResponse {
  type: 'LineString';
  coordinates: [number, number][]; // [lon, lat]
}
