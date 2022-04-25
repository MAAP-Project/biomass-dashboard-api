"""API metadata."""

import os
import re
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode

import numpy
from fastapi import APIRouter, Query
from rio_tiler.io import COGReader
from starlette.requests import Request
from starlette.responses import Response

from dashboard_api.core import config
from dashboard_api.models.mapbox import TileJSON
from dashboard_api.ressources.enums import ImageType

router = APIRouter()


@router.get(
    "/tilejson.json",
    response_model=TileJSON,
    responses={200: {"description": "Return a tilejson"}},
    response_model_exclude_none=True,
)
def tilejson(
    request: Request,
    response: Response,
    url: str = Query(..., description="Cloud Optimized GeoTIFF URL."),
    tile_format: Optional[ImageType] = Query(
        None, description="Output image type. Default is auto."
    ),
    tile_scale: int = Query(
        1, gt=0, lt=4, description="Tile size scale. 1=256x256, 2=512x512..."
    ),
):
    """Handle /tilejson.json requests."""
    scheme = request.url.scheme
    host = request.headers["host"]
    if config.API_VERSION_STR:
        host += config.API_VERSION_STR

    if tile_format:
        tile_url = f"{scheme}://{host}/{{z}}/{{x}}/{{y}}@{tile_scale}x.{tile_format}"
    else:
        tile_url = f"{scheme}://{host}/{{z}}/{{x}}/{{y}}@{tile_scale}x"

    qs_key_to_remove = [
        "tile_format",
        "tile_scale",
    ]
    qs = [
        (key, value)
        for (key, value) in request.query_params._list
        if key.lower() not in qs_key_to_remove
    ]
    if qs:
        tile_url += f"?{urlencode(qs)}"

    response.headers["Cache-Control"] = "max-age=3600"

    with COGReader(url) as src_dst:
        return {
            "bounds": src_dst.geographic_bounds,
            "minzoom": src_dst.minzoom,
            "maxzoom": src_dst.maxzoom,
            "tiles": [tile_url],
            "name": os.path.basename(url),
        }


@router.get(
    "/bounds", responses={200: {"description": "Return the bounds of the COG."}}
)
def bounds(
    response: Response,
    url: str = Query(..., description="Cloud Optimized GeoTIFF URL."),
):
    """Handle /bounds requests."""
    response.headers["Cache-Control"] = "max-age=3600"
    with COGReader(url) as src_dst:
        return {"address": url, "bounds": src_dst.geographic_bounds}


@router.get("/info", responses={200: {"description": "Return basic info on COG."}})
def info(
    response: Response,
    url: str = Query(..., description="Cloud Optimized GeoTIFF URL."),
):
    """Handle /info requests."""
    response.headers["Cache-Control"] = "max-age=3600"
    with COGReader(url) as src_dst:
        info = src_dst.info()
        return {"address": url, **info}


@router.get(
    "/metadata", responses={200: {"description": "Return the metadata of the COG."}}
)
def metadata(
    request: Request,
    response: Response,
    url: str = Query(..., description="Cloud Optimized GeoTIFF URL."),
    bidx: Optional[str] = Query(None, description="Coma (',') delimited band indexes"),
    nodata: Optional[Union[str, int, float]] = Query(
        None, description="Overwrite internal Nodata value."
    ),
    pmin: float = 2.0,
    pmax: float = 98.0,
    max_size: int = 1024,
    histogram_bins: int = 20,
    histogram_range: Optional[str] = Query(
        None, description="Coma (',') delimited Min,Max bounds"
    ),
):
    """Handle /metadata requests."""
    kwargs = dict(request.query_params)
    kwargs.pop("url", None)
    kwargs.pop("bidx", None)
    kwargs.pop("nodata", None)
    kwargs.pop("pmin", None)
    kwargs.pop("pmax", None)
    kwargs.pop("max_size", None)
    kwargs.pop("histogram_bins", None)
    kwargs.pop("histogram_range", None)

    indexes = tuple(int(s) for s in re.findall(r"\d+", bidx)) if bidx else None

    if nodata is not None:
        nodata = numpy.nan if nodata == "nan" else float(nodata)

    hist_options: Dict[str, Any] = dict()
    if histogram_bins:
        hist_options.update(dict(bins=histogram_bins))
    if histogram_range:
        hist_options.update(dict(range=list(map(float, histogram_range.split(",")))))

    response.headers["Cache-Control"] = "max-age=3600"

    with COGReader(url, nodata=nodata) as cog:
        info = cog.info().dict()
        stats = cog.statistics(
            indexes=indexes,
            percentiles=[pmin, pmax],
            hist_options=hist_options,
            max_size=max_size,
            **kwargs,
        )

        return {"address": url, **info, "statistics": stats}
