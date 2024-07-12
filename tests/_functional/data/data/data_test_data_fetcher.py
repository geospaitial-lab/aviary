import numpy as np

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
