import numpy as np
from shapely.geometry import box

data_test__generate_polygons = [
    (np.array([[0, 0]]),
     256,
     [box(0, 0, 256, 256)]),
    (np.array([[-256, -256], [0, 0], [256, 256]]),
     256,
     [box(-256, -256, 0, 0), box(0, 0, 256, 256), box(256, 256, 512, 512)]),
]

data_test__quantize_coordinates = [
    (-257, -257, 256, (-512, -512)),
    (-256, -256, 256, (-256, -256)),
    (-255, -255, 256, (-256, -256)),
    (-1, -1, 256, (-256, -256)),
    (0, 0, 256, (0, 0)),
    (1, 1, 256, (0, 0)),
    (255, 255, 256, (0, 0)),
    (256, 256, 256, (256, 256)),
    (257, 257, 256, (256, 256)),
]

data_test__validate_quantize_type_error = [
    ('True',
     'Invalid type for quantize. '
     'Expected <class \'bool\'>, but got <class \'str\'>.'),
]
