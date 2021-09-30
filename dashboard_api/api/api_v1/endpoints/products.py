"""products endpoint."""

from dashboard_api.api import utils
from dashboard_api.db.static.products import products as products_manager
from dashboard_api.db.static.datasets import datasets_manager
from dashboard_api.db.memcache import CacheLayer
from dashboard_api.core import config
from dashboard_api.models.static import Product, Products

from fastapi import APIRouter, Depends, HTTPException, Response, Request

router = APIRouter()


@router.get(
    "/products",
    responses={200: dict(description="return a list of all available products")},
    response_model=Products,
)
def get_products(
        request: Request,
        response: Response,
        cache_client: CacheLayer = Depends(utils.get_cache)):
    """Return list of products."""
    products = None
    if cache_client:
        products = cache_client.get_product("_all")
        if products:
            response.headers["X-Cache"] = "HIT"
    if not products:
        scheme = request.url.scheme
        host = request.headers["host"]
        if config.API_VERSION_STR:
            host += config.API_VERSION_STR

        products = products_manager.get_all(api_url=f"{scheme}://{host}")

        if cache_client and products:
            cache_client.set_product("_all", products)

    return products


@router.get(
    "/products/{product_id}",
    responses={200: dict(description="return a product")},
    response_model=Product,
)
def get_product(
    request: Request,
    product_id: str,
    response: Response,
    cache_client: CacheLayer = Depends(utils.get_cache),
):
    """Return product info."""
    product = None

    if cache_client:
        product = cache_client.get_product(product_id)

    if product:
        response.headers["X-Cache"] = "HIT"
    else:
        api_url = _api_url(request)
        if product_id == "global":
            product = Product(id="global", label="Global", datasets=datasets_manager.get_all(api_url).datasets)
        else:    
            product = products_manager.get(product_id, api_url)
        if cache_client and product:
            cache_client.set_product(product_id, product)

    if not product:
        raise HTTPException(
            status_code=404, detail=f"Non-existant product identifier: {product_id}"
        )

    return product
    

def _api_url(request: Request) -> str:
    scheme = request.url.scheme
    host = request.headers["host"]
    if config.API_VERSION_STR:
        host += config.API_VERSION_STR

    return f"{scheme}://{host}"
