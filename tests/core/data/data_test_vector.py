import re

from tests.core.conftest import (
    get_metadata,
    get_vector_layer_1,
    get_vector_layers,
)

data_test_vector_init = [
    # test case 1: Default
    (
        get_vector_layers(),
        None,
        False,
        get_vector_layers(),
        {},
        False,
    ),
    # test case 2: metadata is not None
    (
        get_vector_layers(),
        get_metadata(),
        False,
        get_vector_layers(),
        get_metadata(),
        False,
    ),
]

data_test_vector_init_exceptions = [
    # test case 1: layers contains duplicate layer names
    (
        [
            *get_vector_layers(),
            get_vector_layer_1(),
        ],
        re.escape('Invalid layers! The layers must contain unique layer names.'),
    ),
]
