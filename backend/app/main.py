"""
FastAPI application entrypoint for City Break Planner.

Mount API v1 under /api/v1.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import itineraries, routes as route_geometry

logger = logging.getLogger(__name__)

app = FastAPI(
    title="City Break Planner API",
    description="Generate optimized daily travel itineraries",
    version="0.1.0",
)

# CORS headers added to every response (including 500) so browser can read error body
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return 500 with CORS headers so the client can see the error instead of 'CORS missing'."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
        headers=CORS_HEADERS,
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(itineraries.router, prefix="/api/v1/itineraries", tags=["itineraries"])
app.include_router(route_geometry.router, prefix="/api/v1/routes", tags=["routes"])
