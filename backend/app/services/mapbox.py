"""
Mapbox Directions API: get route geometry (LineString) for ordered waypoints.
Used by GET /api/v1/routes/{route_id}/geometry (TDD Section 4).
"""

import os
from uuid import UUID

import httpx

from app.services.routing import get_poi_coords
from app.models import DailyRoute, RouteStop
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_route_geometry(db: Session, daily_route_id: UUID | str) -> list[list[float]] | None:
    """
    Fetch ordered (lon, lat) for the daily route's stops, call Mapbox Directions
    walking profile, return GeoJSON LineString coordinates [[lon, lat], ...].
    """
    rid = daily_route_id if isinstance(daily_route_id, UUID) else UUID(str(daily_route_id))
    route = db.execute(select(DailyRoute).where(DailyRoute.id == rid)).scalar_one_or_none()
    if not route:
        return None
    stops = (
        db.execute(
            select(RouteStop)
            .where(RouteStop.daily_route_id == route.id)
            .order_by(RouteStop.stop_order)
        )
        .scalars().all()
    )
    if not stops:
        return None
    # stops from .scalars().all() is list of RouteStop
    poi_ids = [s.poi_id for s in stops]
    coords = get_poi_coords(db, poi_ids)
    # Mapbox expects lon,lat
    coords_lonlat = [[lon, lat] for (lat, lon) in coords]
    if len(coords_lonlat) < 2:
        return coords_lonlat
    token = os.getenv("MAPBOX_ACCESS_TOKEN")
    if not token:
        # Fallback: return straight line between points (no API call)
        return coords_lonlat
    url = "https://api.mapbox.com/directions/v5/mapbox/walking/" + ";".join(f"{lon},{lat}" for lon, lat in coords_lonlat)
    params = {"access_token": token, "geometries": "geojson"}
    with httpx.Client(timeout=15.0) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    if not data.get("routes"):
        return coords_lonlat
    return data["routes"][0]["geometry"]["coordinates"]
