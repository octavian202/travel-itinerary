"""
Pydantic schemas for API request/response validation.
"""

from uuid import UUID
from pydantic import BaseModel, Field


# --- Request ---


class GenerateItineraryRequest(BaseModel):
    """Payload for POST /api/v1/itineraries/generate (TDD Section 4)."""
    city_name: str = Field(..., min_length=1, examples=["Cluj-Napoca"])
    days: int = Field(..., ge=1, le=14, description="Number of days for the trip")
    pace: str = Field(..., pattern="^(relaxed|moderate|fast)$")


# --- Response: POI with coordinates for map ---


class Coordinates(BaseModel):
    """WGS84 lon/lat for a POI (GeoJSON order)."""
    longitude: float
    latitude: float


class POIResponse(BaseModel):
    """POI as returned in itinerary (id, name, category, duration, coordinates)."""
    id: UUID
    name: str
    category: str
    estimated_duration_minutes: int
    coordinates: Coordinates

    class Config:
        from_attributes = True


class DayStops(BaseModel):
    """One day's ordered list of POIs (TSP order). Includes daily_route_id for GET /routes/{id}/geometry."""
    day_number: int
    daily_route_id: UUID
    stops: list[POIResponse]


class ItineraryResponse(BaseModel):
    """Full itinerary: id, days, and ordered POIs per day (TDD Section 4)."""
    id: UUID
    location_id: UUID
    days: int
    pace: str
    days_with_stops: list[DayStops]


# --- Route geometry (Mapbox) ---


class RouteGeometryResponse(BaseModel):
    """GeoJSON-like response for drawing the route on the map."""
    type: str = "LineString"
    coordinates: list[list[float]]  # [[lon, lat], ...]
