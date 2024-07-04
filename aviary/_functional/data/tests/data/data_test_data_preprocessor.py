import numpy as np

data = np.array(
    [
        [[0, 127, 255], [255, 0, 127]],
        [[127, 255, 0], [0, 127, 255]],
    ],
    dtype=np.uint8,
)

data_test_normalize_preprocessor = [
    (
        data,
        [0.] * 3,
        [255.] * 3,
        np.array(
            [
                [[0, .49803922, 1], [1, 0, .49803922]],
                [[.49803922, 1, 0], [0, .49803922, 1]],
            ],
            dtype=np.float32,
        ),
    ),
]

data_test_standardize_preprocessor = [
    (
        data,
        [127.] * 3,
        [127.] * 3,
        np.array(
            [
                [[-1, 0, 1.007874], [1.007874, -1, 0]],
                [[0, 1.007874, -1], [-1, 0, 1.007874]],
            ],
            dtype=np.float32,
        ),
    ),
]
