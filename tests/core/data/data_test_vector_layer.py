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
