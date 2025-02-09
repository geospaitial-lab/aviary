import re

import numpy as np

data_test_raster_channel_init_exceptions = [
    # test case 1: data has not two dimensions
    (
        np.ones(shape=(640, 640, 3), dtype=np.uint8),
        0.,
        re.escape('Invalid data! The data must be in shape (n, n).'),
    ),
    # test case 2: data is not a square
    (
        np.ones(shape=(640, 320), dtype=np.uint8),
        0.,
        re.escape('Invalid data! The data must be in shape (n, n).'),
    ),
    # test case 3: buffer_size is negative
    (
        np.ones(shape=(640, 640), dtype=np.uint8),
        -1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 4: buffer_size is .5
    (
        np.ones(shape=(640, 640), dtype=np.uint8),
        .5,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
    # test case 5: buffer_size is greater than .5
    (
        np.ones(shape=(640, 640), dtype=np.uint8),
        1.,
        re.escape('Invalid buffer_size! The buffer size must be in the range [0, 0.5).'),
    ),
]
