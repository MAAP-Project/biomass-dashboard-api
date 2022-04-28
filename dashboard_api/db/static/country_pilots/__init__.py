""" dashboard_api static country_pilots """

import json
import os
from typing import Optional

import botocore
from cachetools import TTLCache

from dashboard_api.core.config import BUCKET, COUNTRY_PILOT_METADATA_FILENAME
from dashboard_api.db.static.datasets import datasets_manager
from dashboard_api.db.utils import indicator_exists, indicator_folders, s3_get
from dashboard_api.models.static import CountryPilot, CountryPilots, Link


class CountryPilotManager:
    """Default CountryPilot holder."""

    def __init__(self):
        """init."""
        self.country_pilots_cache = TTLCache(1, 60)

    def get(self, identifier: str, api_url: str) -> Optional[CountryPilot]:
        """Fetch a CountryPilot."""
        country_pilots = self.get_all(api_url)
        return next(
            filter(lambda x: x.id == identifier, country_pilots.country_pilots), None  # type: ignore
        )

    def get_all(self, api_url: str) -> CountryPilots:
        """Fetch all CountryPilots."""

        country_pilots = self.country_pilots_cache.get("country_pilots")
        indicators = []

        if country_pilots:
            cache_hit = True
        else:
            cache_hit = False
            if os.environ.get("ENV") == "local":
                # Useful for local testing
                example_country_pilots = "example-country-pilots-metadata.json"
                s3_datasets = json.loads(open(example_country_pilots).read())
                country_pilots = CountryPilots(**s3_datasets)
            else:
                try:
                    s3_datasets = json.loads(
                        s3_get(bucket=BUCKET, key=COUNTRY_PILOT_METADATA_FILENAME)
                    )
                    indicators = indicator_folders()

                except botocore.errorfactory.ClientError as e:
                    if e.response["Error"]["Code"] in [
                        "ResourceNotFoundException",
                        "NoSuchKey",
                    ]:
                        s3_datasets = json.loads(
                            open("example-country-pilots-metadata.json").read()
                        )
                    else:
                        raise e

            country_pilots = CountryPilots(**s3_datasets)

            for country_pilot in country_pilots.country_pilots:
                country_pilot.links.append(
                    Link(
                        href=f"{api_url}/country_pilots/{country_pilot.id}",
                        rel="self",
                        type="application/json",
                        title="Self",
                    )
                )
                country_pilot.indicators = [
                    ind for ind in indicators if indicator_exists(country_pilot.id, ind)
                ]

                # we have to flatten the datasets list because of how the api works
                datasets = [
                    datasets_manager.get(ds.id, api_url).datasets
                    for ds in country_pilot.datasets
                ]
                country_pilot.datasets = [i for sub in datasets for i in sub]

        if not cache_hit and country_pilots:
            self.country_pilots_cache["country_pilots"] = country_pilots

        return country_pilots


country_pilots = CountryPilotManager()
