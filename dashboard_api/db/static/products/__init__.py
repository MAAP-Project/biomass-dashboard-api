""" dashboard_api static products """

import json
import os
from typing import Optional

import botocore
from cachetools import TTLCache

from dashboard_api.core.config import BUCKET, PRODUCT_METADATA_FILENAME
from dashboard_api.db.static.datasets import datasets_manager
from dashboard_api.db.utils import indicator_exists, indicator_folders, s3_get
from dashboard_api.models.static import Link, Product, Products


class ProductManager:
    """Default Product holder."""

    def __init__(self):
        """init."""
        self.products_cache = TTLCache(1, 60)

    def get(self, identifier: str, api_url: str) -> Optional[Product]:
        """Fetch a Product."""
        products = self.get_all(api_url)
        return next(filter(lambda x: x.id == identifier, products.products), None)  # type: ignore

    def get_all(self, api_url: str) -> Products:
        """Fetch all Products."""

        products = self.products_cache.get("products")
        indicators = []

        if products:
            cache_hit = True
        else:
            cache_hit = False
            if os.environ.get("ENV") == "local":
                # Useful for local testing
                example_products = "example-products-metadata.json"
                s3_products = json.loads(open(example_products).read())
                products = Products(**s3_products)
            else:
                try:
                    s3_products = json.loads(
                        s3_get(bucket=BUCKET, key=PRODUCT_METADATA_FILENAME)
                    )
                    indicators = indicator_folders()

                except botocore.errorfactory.ClientError as e:
                    print("Error accessing S3 files")
                    if e.response["Error"]["Code"] in [
                        "ResourceNotFoundException",
                        "NoSuchKey",
                    ]:
                        s3_products = json.loads(
                            open("example-products-metadata.json").read()
                        )
                    else:
                        raise e

            products = Products(**s3_products)

            for product in products.products:
                product.links.append(
                    Link(
                        href=f"{api_url}/products/{product.id}",
                        rel="self",
                        type="application/json",
                        title="Self",
                    )
                )
                product.indicators = [
                    ind for ind in indicators if indicator_exists(product.id, ind)
                ]

                # we have to flatten the datasets list because of how the api works
                datasets = [
                    datasets_manager.get(ds.id, api_url).datasets
                    for ds in product.datasets
                ]
                product.datasets = [i for sub in datasets for i in sub]

        if not cache_hit and products:
            self.products_cache["products"] = products

        return products


products = ProductManager()
