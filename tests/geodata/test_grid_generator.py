from unittest.mock import MagicMock, patch

from aviary.core.bounding_box import BoundingBox
from aviary.geodata.grid_generator import GridGenerator


def test_init() -> None:
    bounding_box = BoundingBox(
        x_min=-128,
        y_min=-128,
        x_max=128,
        y_max=128,
    )
    epsg_code = 25832
    grid_generator = GridGenerator(
        bounding_box=bounding_box,
        epsg_code=epsg_code,
    )

    assert grid_generator.bounding_box == bounding_box
    assert grid_generator.epsg_code == epsg_code


@patch('aviary.geodata.grid_generator.compute_coordinates')
def test_compute_coordinates(
    mocked_compute_coordinates: MagicMock,
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


@patch('aviary.geodata.grid_generator.generate_grid')
def test_generate_grid(
    mocked_generate_grid: MagicMock,
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

    mocked_generate_grid.assert_called_once_with(
        bounding_box=grid_generator.bounding_box,
        tile_size=tile_size,
        epsg_code=grid_generator.epsg_code,
        quantize=quantize,
    )
    assert grid == expected
