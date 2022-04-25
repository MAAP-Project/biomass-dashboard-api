"""Tilelapse models."""

from typing import Dict

from geojson_pydantic.features import Feature
from geojson_pydantic.geometries import Polygon
from pydantic import BaseModel

PolygonFeature = Feature[Polygon, Dict]


class TimelapseValue(BaseModel):
    """ "Timelapse values model."""

    mean: float
    median: float


class TimelapseRequest(BaseModel):
    """ "Timelapse request model."""

    month: str
    geojson: PolygonFeature  # type: ignore
    type: str
