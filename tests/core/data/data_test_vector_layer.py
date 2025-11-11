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

import geopandas as gpd
from shapely.geometry import box

from aviary.core.vector_layer import VectorLayer
from tests.core.conftest import (
    get_metadata,
    get_vector_layer,
    get_vector_layer_data,
)

data_test_vector_layer_init = [
    # test case 1: Default
    (
        get_vector_layer_data(),
        'custom',
        None,
        False,
        get_vector_layer_data(),
        'custom',
        {},
        False,
    ),
    # test case 2: metadata is not None
    (
        get_vector_layer_data(),
        'custom',
        get_metadata(),
        False,
        get_vector_layer_data(),
        'custom',
        get_metadata(),
        False,
    ),
]


data_test_vector_layer_eq = [
    # test case 1: other is equal
    (
        get_vector_layer(),
        True,
    ),
    # test case 2: data is not equal
    (
        VectorLayer(
            data=[
                gpd.GeoDataFrame(
                    geometry=[
                        box(-128, -128, 0, 0),
                        box(0, -128, 128, 0),
                        box(-128, 0, 0, 128),
                        box(0, 0, 128, 128),
                        box(128, 128, 256, 256),
                    ],
                ),
            ],
            name='custom',
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 3: name is not equal
    (
        VectorLayer(
            data=get_vector_layer_data(),
            name='r',
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 4: metadata is not equal
    (
        VectorLayer(
            data=get_vector_layer_data(),
            name='custom',
            metadata=get_metadata(),
            copy=False,
        ),
        False,
    ),
    # test case 5: copy is not equal
    (
        VectorLayer(
            data=get_vector_layer_data(),
            name='custom',
            metadata=None,
            copy=True,
        ),
        True,
    ),
    # test case 6: other is not of type VectorLayer
    (
        'invalid',
        False,
    ),
]
