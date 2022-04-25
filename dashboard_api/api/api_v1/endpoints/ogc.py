"""API ogc."""

from urllib.parse import urlencode

from fastapi import APIRouter, Query
from rio_tiler.io import COGReader
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from dashboard_api.core import config
from dashboard_api.ressources.enums import ImageType, MediaType
from dashboard_api.ressources.responses import XMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="dashboard_api/templates")


@router.get(
    r"/WMTSCapabilities.xml",
    responses={200: {"content": {"application/xml": {}}}},
    response_class=XMLResponse,
)
def wtms(
    request: Request,
    response: Response,
    url: str = Query(..., description="Cloud Optimized GeoTIFF URL."),
    tile_format: ImageType = Query(
        ImageType.png, description="Output image type. Default is png."
    ),
    tile_scale: int = Query(
        1, gt=0, lt=4, description="Tile size scale. 1=256x256, 2=512x512..."
    ),
):
    """Wmts endpoint."""
    scheme = request.url.scheme
    host = request.headers["host"]
    if config.API_VERSION_STR:
        host += config.API_VERSION_STR
    endpoint = f"{scheme}://{host}"

    qs_key_to_remove = [
        "tile_format",
        "tile_scale",
        "service",
        "request",
    ]
    qs = [
        (key, value)
        for (key, value) in request.query_params._list
        if key.lower() not in qs_key_to_remove
    ]
    query_params = urlencode(qs)

    with COGReader(url) as cog:
        bounds = cog.geographic_bounds
        minzoom, maxzoom = cog.minzoom, cog.maxzoom

    tilesize = tile_scale * 256
    tileMatrix = []
    for zoom in range(minzoom, maxzoom + 1):
        tileMatrix.append(
            f"""<TileMatrix>
                <ows:Identifier>{zoom}</ows:Identifier>
                <ScaleDenominator>{559082264.02872 / 2 ** zoom / tile_scale}</ScaleDenominator>
                <TopLeftCorner>-20037508.34278925 20037508.34278925</TopLeftCorner>
                <TileWidth>{tilesize}</TileWidth>
                <TileHeight>{tilesize}</TileHeight>
                <MatrixWidth>{2 ** zoom}</MatrixWidth>
                <MatrixHeight>{2 ** zoom}</MatrixHeight>
            </TileMatrix>"""
        )

    return templates.TemplateResponse(
        "wmts.xml",
        {
            "request": request,
            "endpoint": endpoint,
            "bounds": bounds,
            "tileMatrix": tileMatrix,
            "title": "Cloud Optimized GeoTIFF",
            "query_string": query_params,
            "tile_scale": tile_scale,
            "tile_format": tile_format.value,
            "media_type": tile_format.mediatype,
        },
        media_type=MediaType.xml.value,
    )
