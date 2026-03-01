"""
Route geometry API: GeoJSON LineString for a day's route (TDD Section 4).
route_id = daily_route UUID.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import RouteGeometryResponse
from app.services.mapbox import get_route_geometry

router = APIRouter()


@router.get("/{route_id}/geometry", response_model=RouteGeometryResponse)
def get_route_geometry_endpoint(
    route_id: UUID,
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/routes/{route_id}/geometry (TDD Section 4).
    Calls Mapbox Directions API with the day's ordered POI coordinates
    and returns GeoJSON LineString for drawing on the frontend map.
    """
    coords = get_route_geometry(db, route_id)
    if coords is None:
        raise HTTPException(status_code=404, detail="Route not found.")
    return RouteGeometryResponse(type="LineString", coordinates=coords)
