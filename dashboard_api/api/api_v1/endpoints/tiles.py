"""API tiles."""

import re
from typing import Any, Dict, List, Optional, Union

import numpy
from fastapi import APIRouter, Depends, Path, Query
from rio_tiler.io import COGReader
from rio_tiler.utils import _chunks
from starlette.responses import Response

from dashboard_api.api import utils
from dashboard_api.db.memcache import CacheLayer
from dashboard_api.ressources.enums import ImageType
from dashboard_api.ressources.responses import TileResponse

router = APIRouter()
responses = {
    200: {
        "content": {
            "image/png": {},
            "image/jpg": {},
            "image/webp": {},
            "image/tiff": {},
            "application/x-binary": {},
        },
        "description": "Return an image.",
    }
}
tile_routes_params: Dict[str, Any] = dict(
    responses=responses, tags=["tiles"], response_class=TileResponse
)


@router.get(r"/{z}/{x}/{y}", **tile_routes_params)
@router.get(r"/{z}/{x}/{y}.{ext}", **tile_routes_params)
@router.get(r"/{z}/{x}/{y}@{scale}x", **tile_routes_params)
@router.get(r"/{z}/{x}/{y}@{scale}x.{ext}", **tile_routes_params)
def tile(
    z: int = Path(..., ge=0, le=30, description="Mercator tiles's zoom level"),
    x: int = Path(..., description="Mercator tiles's column"),
    y: int = Path(..., description="Mercator tiles's row"),
    scale: int = Query(
        1, gt=0, lt=4, description="Tile size scale. 1=256x256, 2=512x512..."
    ),
    ext: ImageType = Query(None, description="Output image type. Default is auto."),
    url: str = Query(..., description="Cloud Optimized GeoTIFF URL."),
    bidx: Optional[str] = Query(None, description="Coma (',') delimited band indexes"),
    nodata: Optional[Union[str, int, float]] = Query(
        None, description="Overwrite internal Nodata value."
    ),
    rescale: Optional[str] = Query(
        None, description="Coma (',') delimited Min,Max bounds"
    ),
    color_formula: Optional[str] = Query(None, title="rio-color formula"),
    color_map: Optional[utils.ColorMapName] = Query(
        None, title="rio-tiler color map name"
    ),
    cache_client: CacheLayer = Depends(utils.get_cache),
) -> TileResponse:
    """Handle /tiles requests."""
    timings = []
    headers: Dict[str, str] = {}

    tile_hash = utils.get_hash(
        **dict(
            z=z,
            x=x,
            y=y,
            ext=ext,
            scale=scale,
            url=url,
            bidx=bidx,
            nodata=nodata,
            rescale=rescale,
            color_formula=color_formula,
            color_map=color_map.value if color_map else "",
        )
    )
    tilesize = scale * 256

    content = None
    if cache_client:
        try:
            content, ext = cache_client.get_image_from_cache(tile_hash)
            headers["X-Cache"] = "HIT"
        except Exception:
            content = None

    if not content:
        indexes = tuple(int(s) for s in re.findall(r"\d+", bidx)) if bidx else None

        if nodata is not None:
            nodata = numpy.nan if nodata == "nan" else float(nodata)

        with utils.Timer() as t:
            with COGReader(url, nodata=nodata) as cog:
                data = cog.tile(x, y, z, indexes=indexes, tilesize=tilesize)
        timings.append(("Read", t.elapsed))

        if not ext:
            ext = ImageType.jpg if data.mask.all() else ImageType.png

        with utils.Timer() as t:
            rescale_arr: Optional[List[List[float]]] = None
            if rescale:
                rescale_arr = list(map(float, rescale.split(",")))  # type: ignore
                rescale_arr = list(_chunks(rescale_arr, 2))
                if len(rescale_arr) != data.data.shape[0]:
                    rescale_arr = ((rescale_arr[0]),) * data.data.shape[0]

            image = data.post_process(rescale=rescale_arr, color_formula=color_formula)

        timings.append(("Post-process", t.elapsed))

        if color_map:
            color_map = utils.cmap.get(color_map.value)  # type: ignore

        with utils.Timer() as t:
            content = image.render(
                img_format=ext.driver,
                colormap=color_map,
                **ext.profile,
            )

        timings.append(("Format", t.elapsed))

        if cache_client and content:
            cache_client.set_image_cache(tile_hash, (content, ext))

    if timings:
        headers["X-Server-Timings"] = "; ".join(
            ["{} - {:0.2f}".format(name, time * 1000) for (name, time) in timings]
        )

    # By default we set a 3600 second TLL
    headers["Cache-Control"] = "max-age=3600"

    return Response(content, media_type=ext.mediatype, headers=headers)
