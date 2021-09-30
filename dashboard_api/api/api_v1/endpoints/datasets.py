"""Dataset endpoints."""
from dashboard_api.api import utils
from dashboard_api.core import config
from dashboard_api.db.memcache import CacheLayer
from dashboard_api.db.static.datasets import datasets_manager
from dashboard_api.db.static.errors import InvalidIdentifier
from dashboard_api.models.static import Datasets, Dataset

from fastapi import APIRouter, Depends, HTTPException, Response

from starlette.requests import Request

router = APIRouter()


@router.get(
    "/datasets",
    responses={200: dict(description="return a list of all available datasets")},
    response_model=Datasets,
)
def get_datasets(
    request: Request,
    response: Response,
    cache_client: CacheLayer = Depends(utils.get_cache),
):
    """Return a list of datasets."""
    content = None
    if cache_client:
        content = cache_client.get_dataset("_all")
        if content:
            content = Datasets.parse_raw(content)
            response.headers["X-Cache"] = "HIT"
    if not content:
        scheme = request.url.scheme
        host = request.headers["host"]
        if config.API_VERSION_STR:
            host += config.API_VERSION_STR

        content = datasets_manager.get_all(api_url=f"{scheme}://{host}")

        if cache_client and content:
            cache_client.set_dataset("_all", content)

    return content


@router.get(
    "/datasets/{dataset_id}",
    responses={
        200: dict(description="return datasets available for a given spotlight")
    },
    response_model=Dataset,
)
def get_dataset(
    request: Request,
    dataset_id: str,
    response: Response,
    cache_client: CacheLayer = Depends(utils.get_cache),
):
    """Return dataset info for all datasets available for a given spotlight"""
    try:
        content = None

        if cache_client:
            content = cache_client.get_dataset(dataset_id)
            if content:
                content = Datasets.parse_raw(content)
                response.headers["X-Cache"] = "HIT"
        if not content:
            scheme = request.url.scheme
            host = request.headers["host"]
            if config.API_VERSION_STR:
                host += config.API_VERSION_STR

            content = datasets_manager.get(dataset_id, api_url=f"{scheme}://{host}")

            if cache_client and content:
                cache_client.set_dataset(dataset_id, content)

        return content.datasets[0]
    except InvalidIdentifier:
        raise HTTPException(
            status_code=404, detail=f"Invalid dataset identifier: {dataset_id}"
        )
