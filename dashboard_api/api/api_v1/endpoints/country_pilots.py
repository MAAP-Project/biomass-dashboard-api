"""country_pilots endpoint."""

from dashboard_api.api import utils
from dashboard_api.db.static.country_pilots import country_pilots as country_pilots_manager
from dashboard_api.db.memcache import CacheLayer
from dashboard_api.core import config
from dashboard_api.models.static import CountryPilot, CountryPilots

from fastapi import APIRouter, Depends, HTTPException, Response, Request

router = APIRouter()


@router.get(
    "/country_pilots",
    responses={200: dict(description="return a list of all available country pilots")},
    response_model=CountryPilots,
)
def get_country_pilots(
        request: Request,
        response: Response,
        cache_client: CacheLayer = Depends(utils.get_cache)):
    """Return list of country pilots."""
    country_pilots = None
    if cache_client:
        country_pilots_raw = cache_client.get_country_pilot("_all")
        if country_pilots_raw:
            country_pilots = CountryPilots.parse_raw(country_pilots_raw)
            response.headers["X-Cache"] = "HIT"
    if not country_pilots:
        scheme = request.url.scheme
        host = request.headers["host"]
        if config.API_VERSION_STR:
            host += config.API_VERSION_STR

        country_pilots = country_pilots_manager.get_all(api_url=f"{scheme}://{host}")

        if cache_client and country_pilots:
            cache_client.set_country_pilot("_all", country_pilots)

    return country_pilots


@router.get(
    "/country_pilots/{country_pilot_id}",
    responses={200: dict(description="return a country_pilot")},
    response_model=CountryPilot,
)
def get_country_pilot(
    request: Request,
    country_pilot_id: str,
    response: Response,
    cache_client: CacheLayer = Depends(utils.get_cache),
):
    """Return country_pilot info."""
    country_pilot = None

    if cache_client:
        country_pilot = cache_client.get_country_pilot(country_pilot_id)

    if country_pilot:
        response.headers["X-Cache"] = "HIT"
    else:
        country_pilot = country_pilots_manager.get(country_pilot_id, _api_url(request))
        if cache_client and country_pilot:
            cache_client.set_country_pilot(country_pilot_id, country_pilot)

    if not country_pilot:
        raise HTTPException(
            status_code=404, detail=f"Non-existant country_pilot identifier: {country_pilot_id}"
        )

    return country_pilot
    

def _api_url(request: Request) -> str:
    scheme = request.url.scheme
    host = request.headers["host"]
    if config.API_VERSION_STR:
        host += config.API_VERSION_STR

    return f"{scheme}://{host}"
