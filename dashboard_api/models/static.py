"""Static models."""

from typing import Any, List, Optional, Union

from geojson_pydantic.geometries import Polygon
from pydantic import BaseModel


def to_camel(snake_str: str) -> str:
    """
    Converts snake_case_string to camelCaseString
    """
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])


class Source(BaseModel):
    """Base Source Model"""

    type: str


class NonGeoJsonSource(Source):
    """Source Model for all non-geojson data types"""

    tiles: List[str]
    source_layer: Optional[str]
    layer_type: Optional[str]
    source_url: Optional[str]
    minzoom: int = 0
    maxzoom: int = 23


class GeoJsonSource(Source):
    """Source Model for geojson data types"""

    data: str


class Swatch(BaseModel):
    """Swatch Model."""

    color: str
    name: str


class LabelStop(BaseModel):
    """Model for Legend stops with color + label"""

    color: str
    label: str


class Legend(BaseModel):
    """Legend Model."""

    type: str
    min: Optional[str]
    max: Optional[str]
    units: Optional[str]
    stops: Union[List[str], List[LabelStop]]


class DatasetComparison(BaseModel):
    """Dataset `compare` Model."""

    enabled: bool
    help: str
    year_diff: int
    map_label: str
    source: NonGeoJsonSource
    time_unit: Optional[str]


def snake_case_to_kebab_case(s):
    """Util method to convert kebab-case fieldnames to snake_case."""
    return s.replace("_", "-")


class Paint(BaseModel):
    """Paint Model."""

    class Config:
        """Paint Model Config"""

        alias_generator = snake_case_to_kebab_case
        allow_population_by_field_name = True


class RasterPaint(Paint):
    """Raster Paint Model."""

    raster_opacity: Optional[float] = None


class CirclePaint(Paint):
    """Circle Paint Model."""

    # To use the Union we must make at least one attribute non-optional in order to bypass this option in favor of RasterPaint, for example.
    circle_radius: float
    circle_color: Union[dict, str]
    circle_opacity: Optional[float]
    circle_stroke_color: Optional[str]
    circle_stroke_width: Optional[float]


class Dataset(BaseModel):
    """Dataset Model."""

    id: str
    name: Optional[str]
    type: Optional[str]
    is_periodic: bool = False
    time_unit: Optional[str] = ""
    domain: Optional[List[str]] = []
    source: Optional[Union[NonGeoJsonSource, GeoJsonSource]]
    background_source: Optional[Union[NonGeoJsonSource, GeoJsonSource]]
    exclusive_with: Optional[List[str]] = []
    swatch: Optional[Swatch]
    compare: Optional[DatasetComparison]
    legend: Optional[Legend]
    paint: Optional[Union[CirclePaint, RasterPaint]]
    info: Optional[str] = ""
    order: Optional[int] = 10000


class DatasetExternal(Dataset):
    """Public facing dataset model (uses camelCase fieldnames)"""

    class Config:
        """Generates alias to convert all fieldnames from snake_case to camelCase"""

        alias_generator = to_camel
        allow_population_by_field_name = True


class DatasetInternal(Dataset):
    """Private dataset model (includes the dataset's location in s3)"""

    s3_location: Optional[str]


class Datasets(BaseModel):
    """Dataset List Model."""

    datasets: List[DatasetExternal]


class Link(BaseModel):
    """
    Link for hypermedia
    """

    href: str
    rel: str
    type: Optional[str]
    title: Optional[str]


class CountryPilot(BaseModel):
    """CountryPilot Model."""

    id: str
    label: str
    summary: str
    center: List[float]
    polygon: Optional[Polygon] = None
    bounding_box: Optional[List[float]] = None
    indicators: List[Any] = []
    links: List[Link] = []
    datasets: List[DatasetExternal] = []


class CountryPilots(BaseModel):
    """CountryPilot List Model."""

    country_pilots: List[CountryPilot]


class Product(BaseModel):
    """Product Model."""

    id: str
    label: str
    summary: Optional[str]
    center: Optional[List[float]]
    polygon: Optional[Polygon]
    bounding_box: Optional[List[float]]
    indicators: List[Any] = []
    links: List[Link] = []
    datasets: List[DatasetExternal] = []


class Products(BaseModel):
    """Product List Model."""

    products: List[Product]


class IndicatorObservation(BaseModel):
    """Indicator Observation Model."""

    indicator: float
    indicator_conf_low: Optional[float]
    indicator_conf_high: Optional[float]
    baseline: Optional[float]
    baseline_conf_low: Optional[float]
    baseline_conf_high: Optional[float]
    anomaly: Optional[str]
