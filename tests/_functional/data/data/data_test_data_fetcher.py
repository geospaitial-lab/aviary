import numpy as np

from aviary.core.bounding_box import BoundingBox
from aviary.core.enums import WMSVersion

data_test__compute_tile_size_pixels = [
    # test case 1: buffer_size is 0
    (128, 0, .5, 256),
    # test case 2: buffer_size is not 0
    (128, 64, .5, 512),
]

data = np.array(
    [
        [[0, 127, 255], [255, 0, 127]],
        [[127, 255, 0], [0, 127, 255]],
    ],
    dtype=np.uint8,
)

data_test__drop_channels = [
    # test case 1: drop_channels is None
    (
        data,
        None,
        data,
    ),
    # test case 2: drop_channels is empty
    (
        data,
        [],
        data,
    ),
    # test case 3: drop_channels is not empty
    (
        data,
        [0, 2],
        np.array(
            [
                [[127], [0]],
                [[255], [127]],
            ],
            dtype=np.uint8,
        ),
    ),
    # test case 4: drop_channels contains a negative index
    (
        data,
        [0, -1],
        np.array(
            [
                [[127], [0]],
                [[255], [127]],
            ],
            dtype=np.uint8,
        ),
    ),
]

data_test__get_wms_params = [
    # test case 1: WMS version is 1.3.0 and style is None
    (
        WMSVersion.V1_3_0,
        'test_layer',
        25832,
        'image/png',
        640,
        BoundingBox(-64, -64, 64, 64),
        None,
        '0x000000',
        {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetMap',
            'layers': 'test_layer',
            'crs': 'EPSG:25832',
            'format': 'image/png',
            'width': '640',
            'height': '640',
            'bbox': '-64,-64,64,64',
            'styles': '',
            'transparent': 'false',
            'bgcolor': '0x000000',
        },
    ),
    # test case 2: WMS version is 1.3.0 and style is not None
    (
        WMSVersion.V1_3_0,
        'test_layer',
        25832,
        'image/png',
        640,
        BoundingBox(-64, -64, 64, 64),
        'test_style',
        '0x000000',
        {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetMap',
            'layers': 'test_layer',
            'crs': 'EPSG:25832',
            'format': 'image/png',
            'width': '640',
            'height': '640',
            'bbox': '-64,-64,64,64',
            'styles': 'test_style',
            'transparent': 'false',
            'bgcolor': '0x000000',
        },
    ),
    # test case 3: WMS version is 1.1.1 and style is None
    (
        WMSVersion.V1_1_1,
        'test_layer',
        25832,
        'image/png',
        640,
        BoundingBox(-64, -64, 64, 64),
        None,
        '0x000000',
        {
            'service': 'WMS',
            'version': '1.1.1',
            'request': 'GetMap',
            'layers': 'test_layer',
            'srs': 'EPSG:25832',
            'format': 'image/png',
            'width': '640',
            'height': '640',
            'bbox': '-64,-64,64,64',
            'styles': '',
            'transparent': 'false',
            'bgcolor': '0x000000',
        },
    ),
]

data_test__permute_data = [
    (
        np.array([
            [[0, 255], [127, 0]],
            [[127, 0], [255, 127]],
            [[255, 127], [0, 255]],
        ]),
        data,
    ),
]
