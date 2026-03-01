"""
SQLAlchemy 2.0 models for City Break Planner.

Maps exactly to TDD Section 2: locations, pois, itineraries, daily_routes, route_stops.
Uses GeoAlchemy2 for PostGIS geometry columns (Point, SRID 4326 = WGS84).
"""

import uuid
import enum
from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.database import Base


class PaceEnum(str, enum.Enum):
    """Travel pace for an itinerary; controls POIs per day (TDD Step 3.2)."""
    relaxed = "relaxed"
    moderate = "moderate"
    fast = "fast"


class Location(Base):
    """
    Target city. Geometry is the city center or representative point (WGS84).
    """
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    geom = Column(Geometry("POINT", srid=4326))

    # Relationships: one city has many POIs and many itineraries
    pois = relationship("POI", back_populates="location")
    itineraries = relationship("Itinerary", back_populates="location")


class POI(Base):
    """
    Point of Interest (attraction, museum, park, etc.) in a location.
    geom is WGS84 (SRID 4326) as required by PostGIS and mapping clients.
    """
    __tablename__ = "pois"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False)
    geom = Column(Geometry("POINT", srid=4326))

    location = relationship("Location", back_populates="pois")
    route_stops = relationship("RouteStop", back_populates="poi")


class Itinerary(Base):
    """
    User-generated plan: N days in a location at a given pace.
    """
    __tablename__ = "itineraries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    days = Column(Integer, nullable=False)
    pace = Column(Enum(PaceEnum), nullable=False)

    location = relationship("Location", back_populates="itineraries")
    daily_routes = relationship("DailyRoute", back_populates="itinerary")


class DailyRoute(Base):
    """
    One day of an itinerary; groups POIs to visit that day.
    """
    __tablename__ = "daily_routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id"), nullable=False)
    day_number = Column(Integer, nullable=False)

    itinerary = relationship("Itinerary", back_populates="daily_routes")
    route_stops = relationship("RouteStop", back_populates="daily_route")


class RouteStop(Base):
    """
    A single POI visit within a day; stop_order gives the visit sequence (TSP order).
    """
    __tablename__ = "route_stops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    daily_route_id = Column(UUID(as_uuid=True), ForeignKey("daily_routes.id"), nullable=False)
    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id"), nullable=False)
    stop_order = Column(Integer, nullable=False)

    daily_route = relationship("DailyRoute", back_populates="route_stops")
    poi = relationship("POI", back_populates="route_stops")
