from unittest.mock import patch

from src.data import GridGenerator


def test_init() -> None:
    bounding_box = (-128, -128, 128, 128)
    epsg_code = 25832
    grid_generator = GridGenerator(
        bounding_box=bounding_box,
        epsg_code=epsg_code,
    )

    assert grid_generator.bounding_box == bounding_box
    assert grid_generator.epsg_code == epsg_code
    assert grid_generator.x_min == bounding_box[0]
    assert grid_generator.y_min == bounding_box[1]
    assert grid_generator.x_max == bounding_box[2]
    assert grid_generator.y_max == bounding_box[3]


@patch('src.data.grid_generator.compute_coordinates')
def test_compute_coordinates(
    mocked_compute_coordinates,
    grid_generator: GridGenerator,
) -> None:
    tile_size = 128
    quantize = True
    expected = 'expected'
    mocked_compute_coordinates.return_value = expected
    coordinates = grid_generator.compute_coordinates(
        tile_size=tile_size,
        quantize=quantize,
    )

    mocked_compute_coordinates.assert_called_once_with(
        bounding_box=grid_generator.bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )
    assert coordinates == expected


@patch('src.data.grid_generator.generate_grid')
def test_generate_grid(
    mocked_generate_grid,
    grid_generator: GridGenerator,
) -> None:
    tile_size = 128
    quantize = True
    expected = 'expected'
    mocked_generate_grid.return_value = expected
    grid = grid_generator.generate_grid(
        tile_size=tile_size,
        quantize=quantize,
    )

    assert mocked_generate_grid.called_once_with(
        bounding_box=grid_generator.bounding_box,
        tile_size=tile_size,
        epsg_code=grid_generator.epsg_code,
        quantize=quantize,
    )
    assert grid == expected
