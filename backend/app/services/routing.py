"""
Itinerary generation: geocode city, AI-generated day plan, geocode each stop,
then persist Location, POIs, Itinerary, DailyRoutes, RouteStops.
"""

import logging
from uuid import UUID

import httpx
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement
from geoalchemy2.functions import ST_X, ST_Y

from app.models import Location, POI, Itinerary, DailyRoute, RouteStop
from app.models import PaceEnum
from app.services.ai_itinerary import generate_ai_itinerary

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {"User-Agent": "CityBreakPlanner/1.0"}


def get_city_bbox_and_center(city_name: str, country: str | None = None) -> dict | None:
    """
    Geocode city via Nominatim to get bounding box and center.
    Returns dict with center_lat, center_lon, bbox [south, north, west, east], display_name.
    """
    q = city_name if not country else f"{city_name}, {country}"
    params = {"q": q, "format": "json", "limit": 1}
    with httpx.Client(timeout=15.0) as client:
        r = client.get(NOMINATIM_URL, params=params, headers=NOMINATIM_HEADERS)
        r.raise_for_status()
        data = r.json()
    if not data:
        return None
    item = data[0]
    bbox = list(map(float, item["boundingbox"]))
    lat = float(item["lat"])
    lon = float(item["lon"])
    return {
        "center_lat": lat,
        "center_lon": lon,
        "bbox": bbox,
        "display_name": item.get("display_name", city_name),
    }


def geocode_place(place_name: str, city_name: str) -> tuple[float, float] | None:
    """
    Geocode a single place in a city via Nominatim.
    Returns (lat, lon) or None if not found.
    """
    q = f"{place_name}, {city_name}"
    params = {"q": q, "format": "json", "limit": 1}
    with httpx.Client(timeout=10.0) as client:
        r = client.get(NOMINATIM_URL, params=params, headers=NOMINATIM_HEADERS)
        if r.status_code != 200:
            return None
        data = r.json()
    if not data:
        return None
    item = data[0]
    try:
        return float(item["lat"]), float(item["lon"])
    except (KeyError, TypeError, ValueError):
        return None


def get_poi_coords(db: Session, poi_ids: list[UUID]) -> list[tuple[float, float]]:
    """Fetch (lat, lon) for POIs using PostGIS ST_Y(geom), ST_X(geom). Returns list in same order as poi_ids."""
    if not poi_ids:
        return []
    stmt = select(POI.id, ST_Y(POI.geom), ST_X(POI.geom)).where(POI.id.in_(poi_ids))
    rows = db.execute(stmt).all()
    id_to_coord = {row[0]: (float(row[1]), float(row[2])) for row in rows}
    return [id_to_coord[pid] for pid in poi_ids]


def generate_itinerary(
    db: Session,
    city_name: str,
    days: int,
    pace_str: str,
) -> Itinerary | None:
    """
    Generate itinerary via AI: geocode city -> AI day plan -> geocode each stop -> persist.
    Returns the created Itinerary or None if geocoding or AI fails.
    Raises ValueError if OPENAI_API_KEY is not set (caller may map to 503).
    """
    pace = PaceEnum(pace_str)
    geo = get_city_bbox_and_center(city_name)
    if not geo:
        return None
    center_lat = geo["center_lat"]
    center_lon = geo["center_lon"]
    display_name = geo["display_name"]
    parts = display_name.split(",")
    country = parts[-1].strip() if len(parts) > 1 else "Unknown"

    ai_result = generate_ai_itinerary(city_name, days, pace_str)
    if not ai_result or not ai_result.days:
        return None

    loc = db.execute(
        select(Location).where(Location.name.ilike(city_name.strip())).limit(1)
    ).scalar_one_or_none()
    if not loc:
        loc = Location(
            name=city_name.strip(),
            country=country,
            geom=WKTElement(f"POINT({center_lon} {center_lat})", srid=4326),
        )
        db.add(loc)
        db.flush()
    else:
        # Delete in dependency order: route_stops -> daily_routes -> itineraries -> pois
        itinerary_ids = select(Itinerary.id).where(Itinerary.location_id == loc.id)
        daily_route_ids = select(DailyRoute.id).where(DailyRoute.itinerary_id.in_(itinerary_ids))
        db.execute(delete(RouteStop).where(RouteStop.daily_route_id.in_(daily_route_ids)))
        db.execute(delete(DailyRoute).where(DailyRoute.itinerary_id.in_(itinerary_ids)))
        db.execute(delete(Itinerary).where(Itinerary.location_id == loc.id))
        db.execute(delete(POI).where(POI.location_id == loc.id))
        db.flush()

    # (poi, day_number, stop_order) for later RouteStops
    pois_with_placement: list[tuple[POI, int, int]] = []
    for ai_day in ai_result.days:
        for stop_order, stop in enumerate(ai_day.stops):
            coords = geocode_place(stop.name, city_name)
            if coords is None:
                coords = (center_lat, center_lon)
                logger.debug("Geocode failed for %s in %s, using city center", stop.name, city_name)
            lat, lon = coords
            geom = WKTElement(f"POINT({lon} {lat})", srid=4326)
            poi = POI(
                location_id=loc.id,
                name=stop.name[:255],
                category=stop.category[:64],
                estimated_duration_minutes=stop.estimated_duration_minutes,
                geom=geom,
            )
            db.add(poi)
            db.flush()
            pois_with_placement.append((poi, ai_day.day_number, stop_order))

    itinerary = Itinerary(location_id=loc.id, days=days, pace=pace)
    db.add(itinerary)
    db.flush()

    for day_number in range(1, days + 1):
        daily = DailyRoute(itinerary_id=itinerary.id, day_number=day_number)
        db.add(daily)
        db.flush()
        for poi, dnum, stop_order in pois_with_placement:
            if dnum != day_number:
                continue
            db.add(RouteStop(daily_route_id=daily.id, poi_id=poi.id, stop_order=stop_order))

    db.commit()
    db.refresh(itinerary)
    return itinerary
