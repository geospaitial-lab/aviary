#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

from unittest.mock import MagicMock

import geopandas as gpd
import numpy as np
import pytest

from aviary.core.enums import (
    GeospatialFilterMode,
    SetFilterMode,
)
from aviary.utils.coordinates_filter import (
    CompositeFilter,
    CoordinatesFilter,
    DuplicatesFilter,
    GeospatialFilter,
    MaskFilter,
    SetFilter,
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
    geometry = []
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    mode = GeospatialFilterMode.DIFFERENCE
    return GeospatialFilter(
        tile_size=tile_size,
        gdf=gdf,
        mode=mode,
    )


@pytest.fixture(scope='session')
def mask_filter() -> MaskFilter:
    mask = np.array(
        [0, 1, 0, 1],
        dtype=np.bool_,
    )
    return MaskFilter(
        mask=mask,
    )


@pytest.fixture(scope='session')
def set_filter() -> SetFilter:
    other = np.array(
        [[-128, 0], [0, 0]],
        dtype=np.int32,
    )
    mode = SetFilterMode.DIFFERENCE
    return SetFilter(
        other=other,
        mode=mode,
    )
