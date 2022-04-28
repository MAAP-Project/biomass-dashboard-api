"""dashboard_api api."""

from dashboard_api.api.api_v1.endpoints import datasets  # isort:skip
from fastapi import APIRouter

from dashboard_api.api.api_v1.endpoints import (
    country_pilots,
    metadata,
    ogc,
    products,
    tiles,
    timelapse,
)

api_router = APIRouter()
api_router.include_router(tiles.router, tags=["tiles"])
api_router.include_router(metadata.router, tags=["metadata"])
api_router.include_router(ogc.router, tags=["OGC"])
api_router.include_router(timelapse.router, tags=["timelapse"])
api_router.include_router(datasets.router, tags=["datasets"])
api_router.include_router(products.router, tags=["products"])
api_router.include_router(country_pilots.router, tags=["country_pilots"])
