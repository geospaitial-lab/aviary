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

import re

from aviary.core.vector import Vector
from tests.core.conftest import (
    get_metadata,
    get_vector,
    get_vector_layer_1,
    get_vector_layer_2,
    get_vector_layers,
)

data_test_vector_bool = [
    # test case 1: layers contains no layers
    (
        Vector(
            layers=[],
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 2: layers contains layers
    (
        get_vector(),
        True,
    ),
]

data_test_vector_contains = [
    ('custom_1', True),
    ('custom_2', True),
    ('invalid', False),
]

data_test_vector_eq = [
    # test case 1: other is equal
    (
        get_vector(),
        True,
    ),
    # test case 2: layers is not equal
    (
        Vector(
            layers=[
                get_vector_layer_1(),
            ],
            metadata=None,
            copy=False,
        ),
        False,
    ),
    # test case 3: metadata is not equal
    (
        Vector(
            layers=get_vector_layers(),
            metadata=get_metadata(),
            copy=False,
        ),
        False,
    ),
    # test case 4: copy is not equal
    (
        Vector(
            layers=get_vector_layers(),
            metadata=None,
            copy=True,
        ),
        True,
    ),
    # test case 5: other is not of type Vector
    (
        'invalid',
        False,
    ),
]

data_test_vector_getattr = [
    ('custom_1', get_vector_layer_1()),
    ('custom_2', get_vector_layer_2()),
]

data_test_vector_getitem = [
    ('custom_1', get_vector_layer_1()),
    ('custom_2', get_vector_layer_2()),
]

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
    # test case 2: layers contains no layers
    (
        [],
        None,
        False,
        [],
        {},
        False,
    ),
    # test case 3: metadata is not None
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
