from pathlib import Path
from unittest.mock import MagicMock

import geopandas as gpd
import numpy as np
import pytest

from ...geodata import (
    CompositeFilter,
    CoordinatesFilter,
    DuplicatesFilter,
    GeospatialFilter,
    GridGenerator,
    MaskFilter,
    SetFilter,
    Vectorizer,
)
from ..._utils.types import (
    BoundingBox,
    GeospatialFilterMode,
    SetFilterMode,
)


@pytest.fixture(scope='session')
def composite_filter() -> CompositeFilter:
    coordinates_filters = [
        MagicMock(spec=CoordinatesFilter),
        MagicMock(spec=CoordinatesFilter),
        MagicMock(spec=CoordinatesFilter),
    ]
    return CompositeFilter(
        coordinates_filters=coordinates_filters,
    )


@pytest.fixture(scope='session')
def duplicates_filter() -> DuplicatesFilter:
    return DuplicatesFilter()


@pytest.fixture(scope='session')
def geospatial_filter() -> GeospatialFilter:
    tile_size = 128
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=[],
        crs=f'EPSG:{epsg_code}',
    )
    mode = GeospatialFilterMode.DIFFERENCE
    return GeospatialFilter(
        tile_size=tile_size,
        epsg_code=epsg_code,
        gdf=gdf,
        mode=mode,
    )


@pytest.fixture(scope='session')
def grid_generator() -> GridGenerator:
    bounding_box = BoundingBox(
        x_min=-128,
        y_min=-128,
        x_max=128,
        y_max=128,
    )
    epsg_code = 25832
    return GridGenerator(
        bounding_box=bounding_box,
        epsg_code=epsg_code,
    )


@pytest.fixture(scope='session')
def mask_filter() -> MaskFilter:
    mask = np.array([0, 1, 0, 1], dtype=np.bool_)
    return MaskFilter(
        mask=mask,
    )


@pytest.fixture(scope='session')
def set_filter() -> SetFilter:
    other = np.array([[-128, 0], [0, 0]], dtype=np.int32)
    mode = SetFilterMode.DIFFERENCE
    return SetFilter(
        other=other,
        mode=mode,
    )


@pytest.fixture(scope='session')
def vectorizer() -> Vectorizer:
    path = Path('test')
    tile_size = 128
    ground_sampling_distance = .2
    epsg_code = 25832
    field_name = 'class'
    num_workers = 1
    return Vectorizer(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        epsg_code=epsg_code,
        field_name=field_name,
        num_workers=num_workers,
    )
