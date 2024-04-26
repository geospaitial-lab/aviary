import numpy as np

data_test__compute_bounding_box = [
    # test case 1: x_min < 0 and y_min < 0, buffer_size is None
    (-128, -128, 128, None, (-128, -128, 0, 0)),
    # test case 2: x_min < 0 and y_min < 0, buffer_size is 0
    (-128, -128, 128, 0, (-128, -128, 0, 0)),
    # test case 3: x_min < 0 and y_min < 0, buffer_size is not 0
    (-128, -128, 128, 64, (-192, -192, 64, 64)),
    # test case 4: x_min = 0 and y_min = 0, buffer_size is None
    (0, 0, 128, None, (0, 0, 128, 128)),
    # test case 5: x_min = 0 and y_min = 0, buffer_size is 0
    (0, 0, 128, 0, (0, 0, 128, 128)),
    # test case 6: x_min = 0 and y_min = 0, buffer_size is not 0
    (0, 0, 128, 64, (-64, -64, 192, 192)),
    # test case 7: x_min > 0 and y_min > 0, buffer_size is None
    (128, 128, 128, None, (128, 128, 256, 256)),
    # test case 8: x_min > 0 and y_min > 0, buffer_size is 0
    (128, 128, 128, 0, (128, 128, 256, 256)),
    # test case 9: x_min > 0 and y_min > 0, buffer_size is not 0
    (128, 128, 128, 64, (64, 64, 320, 320)),
]

data_test__compute_tile_size_pixels = [
    # test case 1: buffer_size is None
    (128, None, .5, 256),
    # test case 2: buffer_size is 0
    (128, 0, .5, 256),
    # test case 3: buffer_size is not 0
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
