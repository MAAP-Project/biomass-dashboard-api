"""dashboard_api.cache.memcache: memcached layer."""

from typing import Dict, Optional, Tuple, Union
from dashboard_api.api import utils

from bmemcached import Client

from dashboard_api.models.static import Datasets, Products, CountryPilots
from dashboard_api.ressources.enums import ImageType


class CacheLayer(object):
    """Memcache Wrapper."""

    def __init__(
        self,
        host,
        port: int = 11211,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Init Cache Layer."""
        self.client = Client((f"{host}:{port}",), user, password)

    def get_image_from_cache(self, img_hash: str) -> Tuple[bytes, ImageType]:
        """
        Get image body from cache layer.

        Attributes
        ----------
            img_hash : str
                file url.

        Returns
        -------
            img : bytes
                image body.
            ext : str
                image ext

        """
        content, ext = self.client.get(img_hash)
        return content, ext

    def set_image_cache(
        self, img_hash: str, body: Tuple[bytes, ImageType], timeout: int = 432000
    ) -> bool:
        """
        Set base64 encoded image body in cache layer.

        Attributes
        ----------
            img_hash : str
                file url.
            body : tuple
                image body + ext
        Returns
        -------
            bool

        """
        try:
            return self.client.set(img_hash, body, time=timeout)
        except Exception:
            return False

    def get_country_pilot(self, country_pilot_id: str) -> Union[Dict, bool]:
        """Get country_pilot response from cache layer"""
        return self.get_object(utils.get_hash(country_pilot_id=country_pilot_id))

    def set_country_pilot(self, country_pilot_id: str, country_pilots: CountryPilots) -> bool:
        """Set country_pilot response in cache layer"""
        try:
            return self.set_object(utils.get_hash(country_pilot_id=country_pilot_id), country_pilots.json())
        except Exception:
            return False

    def get_product(self, product_id: str) -> Union[Dict, bool]:
        """Get product response from cache layer"""
        return self.get_object(utils.get_hash(product_id=product_id))

    def set_product(self, product_id: str, products: Products) -> bool:
        """Set product response in cache layer"""
        try:
            return self.set_object(utils.get_hash(product_id=product_id), products.json())
        except Exception:
            return False

    def get_dataset(self, dataset_id: str) -> Union[Dict, bool]:
        """Get dataset response from cache layer"""
        return self.get_object(utils.get_hash(dataset_id=dataset_id))

    def set_dataset(self, dataset_id: str, datasets: Datasets) -> bool:
        """Set dataset response in cache layer"""
        try:
            return self.get_object(utils.get_hash(dataset_id=dataset_id), datasets.json())
        except Exception:
            return False

    def get_object(self, hash_id: str) -> Union[Dict, bool]:
        """Get dataset response from cache layer"""
        return self.client.get(hash_id)

    def set_object(self, hash_id: str, body: str) -> bool:
        """Set dataset response in cache layer"""
        try:
            return self.client.set(hash_id, body, time=60)
        except Exception:
            return False
