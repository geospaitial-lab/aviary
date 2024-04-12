data_test_validate_bounding_box_type_error = [
    (128,
     'Invalid type for bounding_box. '
     'Expected <class \'tuple\'>, but got <class \'int\'>.'),
]

data_test_validate_bounding_box_value_error = [
    ((-128, -128, 128),
     'Invalid values for bounding_box. '
     'Expected a tuple of 4 integers, but got (-128, -128, 128).'),
    ((-128, -128, 128, 128.),
     'Invalid values for bounding_box. '
     'Expected a tuple of 4 integers, but got (-128, -128, 128, 128.0).'),
    ((0, 0, 0, 0),
     'Invalid values for bounding_box. '
     'Expected (x_min, y_min, x_max, y_max) where x_min < x_max and y_min < y_max, but got (0, 0, 0, 0).'),
    ((128, 128, -128, -128),
     'Invalid values for bounding_box. '
     'Expected (x_min, y_min, x_max, y_max) where x_min < x_max and y_min < y_max, but got (128, 128, -128, -128).'),
]

data_test_validate_epsg_code_type_error = [
    ('25832',
     'Invalid type for epsg_code. '
     'Expected <class \'int\'>, but got <class \'str\'>.'),
]

data_test_validate_epsg_code_value_error = [
    (12345,
     'Invalid value for epsg_code. '
     'Expected a valid EPSG code, but got 12345.'),
]

data_test_validate_tile_size_type_error = [
    ('256',
     'Invalid type for tile_size. '
     'Expected <class \'int\'>, but got <class \'str\'>.'),
]

data_test_validate_tile_size_value_error = [
    (0,
     'Invalid value for tile_size. '
     'Expected a positive integer, but got 0.'),
    (-1,
     'Invalid value for tile_size. '
     'Expected a positive integer, but got -1.'),
]
