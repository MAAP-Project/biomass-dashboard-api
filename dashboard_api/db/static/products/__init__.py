""" dashboard_api static products """
import os
import json

import botocore
from cachetools import TTLCache
from typing import Optional

from dashboard_api.db.utils import s3_get
from dashboard_api.models.static import Products, Link
from dashboard_api.core.config import PRODUCT_METADATA_FILENAME, BUCKET
from dashboard_api.db.utils import indicator_exists, indicator_folders
from dashboard_api.models.static import Product, Products
from dashboard_api.db.static.datasets import datasets_manager

class ProductManager(object):
    """Default Product holder."""

    def __init__(self):
        self.products_cache = TTLCache(1, 60)

    def get(self, identifier: str, api_url: str) -> Optional[Product]:
        """Fetch a Product."""
        products = self.get_all(api_url)
        return next(filter(lambda x: x.id == identifier, products.products), None)

    def get_all(self, api_url: str) -> Products:
        """Fetch all Products."""

        products = self.products_cache.get("products")
        indicators = []

        if products:
            cache_hit = True
        else:
            cache_hit = False
            if os.environ.get('ENV') == 'local':
                # Useful for local testing
                example_products = "example-products-metadata.json"
                print(f"Loading {example_products}")
                s3_products = json.loads(open(example_products).read())
                products = Products(**s3_products)
            else:    
                try:
                    print(f"Loading s3://{BUCKET}/{PRODUCT_METADATA_FILENAME}")
                    s3_products = json.loads(
                        s3_get(bucket=BUCKET, key=PRODUCT_METADATA_FILENAME)
                    )
                    indicators = indicator_folders()
                    print("products json successfully loaded from S3")

                except botocore.errorfactory.ClientError as e:
                    print("Error accessing S3 files")
                    if e.response["Error"]["Code"] in ["ResourceNotFoundException", "NoSuchKey"]:
                        s3_products = json.loads(open("example-products-metadata.json").read())
                    else:
                        raise e

            products = Products(**s3_products)

            for product in products.products:
                product.links.append(Link(
                    href=f"{api_url}/products/{product.id}",
                    rel="self",
                    type="application/json",
                    title="Self"
                ))
                product.indicators = [ind for ind in indicators if indicator_exists(product.id, ind)]

                # we have to flatten the datasets list because of how the api works
                datasets = [datasets_manager.get(
                    ds.id, api_url).datasets for ds in product.datasets]
                product.datasets = [i for sub in datasets for i in sub]

        if not cache_hit and products:
            self.products_cache["products"] = products

        return products


products = ProductManager()
