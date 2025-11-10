#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and / or modify it under the terms of the
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

import numpy as np

from aviary.core.bounding_box import BoundingBox
from aviary.core.enums import WMSVersion

data_test__compute_tile_size_pixels = [
    # test case 1: buffer_size is 0
    (128, 0, .2, 640),
    # test case 2: buffer_size is not 0
    (128, 32, .2, 960),
]

data_test__compute_tile_size_pixels_exceptions = [
    (
        128,
        32,
        .123,
        re.escape(
            'Invalid tile_size! '
            'The tile size must match the spatial extent of the data, '
            'resulting in a whole number of pixels.',
        ),
    ),
]

data_test__get_wms_params = [
    # test case 1: WMS version is 1.3.0 and style is None
    (
        WMSVersion.V1_3_0,
        'layer',
        25832,
        'image/png',
        1280,
        BoundingBox(
            x_min=-128,
            y_min=-64,
            x_max=128,
            y_max=192,
        ),
        None,
        '0x000000',
        {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetMap',
            'layers': 'layer',
            'crs': 'EPSG:25832',
            'format': 'image/png',
            'width': '1280',
            'height': '1280',
            'bbox': '-128,-64,128,192',
            'styles': '',
            'transparent': 'false',
            'bgcolor': '0x000000',
        },
    ),
    # test case 2: WMS version is 1.1.1 and style is None
    (
        WMSVersion.V1_1_1,
        'layer',
        25832,
        'image/png',
        1280,
        BoundingBox(
            x_min=-128,
            y_min=-64,
            x_max=128,
            y_max=192,
        ),
        None,
        '0x000000',
        {
            'service': 'WMS',
            'version': '1.1.1',
            'request': 'GetMap',
            'layers': 'layer',
            'srs': 'EPSG:25832',
            'format': 'image/png',
            'width': '1280',
            'height': '1280',
            'bbox': '-128,-64,128,192',
            'styles': '',
            'transparent': 'false',
            'bgcolor': '0x000000',
        },
    ),
    # test case 3: WMS version is 1.3.0 and style is not None
    (
        WMSVersion.V1_3_0,
        'layer',
        25832,
        'image/png',
        1280,
        BoundingBox(
            x_min=-128,
            y_min=-64,
            x_max=128,
            y_max=192,
        ),
        'style',
        '0x000000',
        {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetMap',
            'layers': 'layer',
            'crs': 'EPSG:25832',
            'format': 'image/png',
            'width': '1280',
            'height': '1280',
            'bbox': '-128,-64,128,192',
            'styles': 'style',
            'transparent': 'false',
            'bgcolor': '0x000000',
        },
    ),
]

data_test__permute_data = [
    (
        np.array(
            [
                [[0, 255], [127, 0]],
                [[127, 0], [255, 127]],
                [[255, 127], [0, 255]],
            ],
            dtype=np.uint8,
        ),
        np.array(
            [
                [[0, 127, 255], [255, 0, 127]],
                [[127, 255, 0], [0, 127, 255]],
            ],
            dtype=np.uint8,
        ),
    ),
]
