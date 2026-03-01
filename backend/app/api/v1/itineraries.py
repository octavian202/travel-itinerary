"""
Itinerary API: generate and retrieve (TDD Section 4).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Itinerary, DailyRoute, RouteStop, POI
from app.schemas import (
    GenerateItineraryRequest,
    ItineraryResponse,
    DayStops,
    POIResponse,
    Coordinates,
)
from app.services.routing import generate_itinerary
from app.services.routing import get_poi_coords

router = APIRouter()


def _itinerary_to_response(db: Session, itinerary: Itinerary) -> ItineraryResponse:
    """Build nested response: days with ordered POIs and coordinates."""
    days_with_stops: list[DayStops] = []
    for daily in sorted(itinerary.daily_routes, key=lambda d: d.day_number):
        stops_sorted = sorted(daily.route_stops, key=lambda s: s.stop_order)
        poi_ids = [s.poi_id for s in stops_sorted]
        if not poi_ids:
            days_with_stops.append(
                DayStops(day_number=daily.day_number, daily_route_id=daily.id, stops=[])
            )
            continue
        coords = get_poi_coords(db, poi_ids)
        pois_response = []
        for i, s in enumerate(stops_sorted):
            poi = s.poi
            lat, lon = coords[i]
            pois_response.append(
                POIResponse(
                    id=poi.id,
                    name=poi.name,
                    category=poi.category,
                    estimated_duration_minutes=poi.estimated_duration_minutes,
                    coordinates=Coordinates(longitude=lon, latitude=lat),
                )
            )
        days_with_stops.append(
            DayStops(day_number=daily.day_number, daily_route_id=daily.id, stops=pois_response)
        )
    return ItineraryResponse(
        id=itinerary.id,
        location_id=itinerary.location_id,
        days=itinerary.days,
        pace=itinerary.pace.value,
        days_with_stops=days_with_stops,
    )


@router.post("/generate", response_model=ItineraryResponse)
def create_itinerary(
    body: GenerateItineraryRequest,
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/itineraries/generate (TDD: triggers generation algorithm).
    Returns itinerary ID, days, and ordered POIs with coordinates.
    """
    try:
        itinerary = generate_itinerary(db, body.city_name, body.days, body.pace)
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e) or "API key" in str(e):
            raise HTTPException(
                status_code=503,
                detail="Service unavailable: OpenAI API key not configured.",
            ) from e
        raise
    if not itinerary:
        raise HTTPException(
            status_code=422,
            detail="Could not generate itinerary (city not found or no POIs).",
        )
    db.refresh(itinerary)
    # Lazy load of daily_routes -> route_stops -> poi when building response
    return _itinerary_to_response(db, itinerary)


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
def get_itinerary(
    itinerary_id: UUID,
    db: Session = Depends(get_db),
):
    """GET /api/v1/itineraries/{itinerary_id} — retrieve a previously generated itinerary."""
    itinerary = (
        db.execute(
            select(Itinerary)
            .where(Itinerary.id == itinerary_id)
            .options(
                selectinload(Itinerary.daily_routes).selectinload(DailyRoute.route_stops).selectinload(RouteStop.poi),
            )
        )
        .scalar_one_or_none()
    )
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found.")
    return _itinerary_to_response(db, itinerary)
