from tests.core.conftest import (
    get_metadata,
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
