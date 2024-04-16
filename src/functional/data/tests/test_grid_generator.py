from unittest.mock import patch

import geopandas as gpd
import geopandas.testing
import numpy as np
import pytest
from shapely.geometry import box, Polygon

from src.functional.data.grid_generator import (
    compute_coordinates,
    generate_grid,
    _generate_polygons,
    _quantize_coordinates,
    _validate_compute_coordinates,
    _validate_generate_grid,
    validate_grid_generator,
    _validate_quantize,
)
from src.functional.data.tests.data.data_test_grid_generator import (
    data_test_compute_coordinates,
    data_test__generate_polygons,
    data_test__quantize_coordinates,
    data_test__validate_quantize_type_error,
)
from src.utils.types import (
    BoundingBox,
    Coordinates,
    TileSize,
    XMin,
    YMin,
)


@pytest.mark.parametrize('bounding_box, tile_size, quantize, expected', data_test_compute_coordinates)
@patch('src.functional.data.grid_generator._validate_compute_coordinates')
def test_compute_coordinates(
    mocked__validate_compute_coordinates,
    bounding_box: BoundingBox,
    tile_size: TileSize,
    quantize: bool,
    expected: Coordinates,
) -> None:
    coordinates = compute_coordinates(
        bounding_box=bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )

    mocked__validate_compute_coordinates.assert_called_once_with(
        bounding_box=bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )
    np.testing.assert_array_equal(coordinates, expected)


@patch('src.functional.data.grid_generator._generate_polygons')
@patch('src.functional.data.grid_generator.compute_coordinates')
@patch('src.functional.data.grid_generator._validate_generate_grid')
def test_generate_grid(
    mocked__validate_generate_grid,
    mocked_compute_coordinates,
    mocked__generate_polygons,
) -> None:
    bounding_box = (-128, -128, 128, 128)
    tile_size = 128
    epsg_code = 25832
    quantize = True
    expected_polygons = [
        box(-128, -128, 0, 0),
        box(0, -128, 128, 0),
        box(-128, 0, 0, 128),
        box(0, 0, 128, 128),
    ]
    mocked__generate_polygons.return_value = expected_polygons
    expected = gpd.GeoDataFrame(
        geometry=mocked__generate_polygons.return_value,
        crs=f'EPSG:{epsg_code}',
    )
    grid = generate_grid(
        bounding_box=bounding_box,
        tile_size=tile_size,
        epsg_code=epsg_code,
        quantize=quantize,
    )

    mocked__validate_generate_grid.assert_called_once_with(
        bounding_box=bounding_box,
        tile_size=tile_size,
        epsg_code=epsg_code,
        quantize=quantize,
    )
    mocked_compute_coordinates.assert_called_once_with(
        bounding_box=bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )
    mocked__generate_polygons.assert_called_once_with(
        coordinates=mocked_compute_coordinates.return_value,
        tile_size=tile_size,
    )
    gpd.testing.assert_geodataframe_equal(grid, expected)


@pytest.mark.parametrize('coordinates, tile_size, expected', data_test__generate_polygons)
def test__generate_polygons(
    coordinates: Coordinates,
    tile_size: TileSize,
    expected: list[Polygon],
) -> None:
    polygons = _generate_polygons(
        coordinates=coordinates,
        tile_size=tile_size,
    )

    assert all(polygon.equals(expected[i]) for i, polygon in enumerate(polygons))


@pytest.mark.parametrize('x_min, y_min, tile_size, expected', data_test__quantize_coordinates)
def test__quantize_coordinates(
    x_min: XMin,
    y_min: YMin,
    tile_size: TileSize,
    expected: tuple[XMin, YMin],
) -> None:
    quantized_x_min, quantized_y_min = _quantize_coordinates(
        x_min=x_min,
        y_min=y_min,
        tile_size=tile_size,
    )

    assert quantized_x_min == expected[0]
    assert quantized_y_min == expected[1]


@patch('src.functional.data.grid_generator._validate_quantize')
@patch('src.functional.data.grid_generator.validate_bounding_box')
@patch('src.functional.data.grid_generator.validate_tile_size')
def test__validate_compute_coordinates(
    mocked_validate_tile_size,
    mocked_validate_bounding_box,
    mocked__validate_quantize,
) -> None:
    bounding_box = (-128, -128, 128, 128)
    tile_size = 256
    quantize = True
    _validate_compute_coordinates(
        bounding_box=bounding_box,
        tile_size=tile_size,
        quantize=quantize,
    )

    mocked_validate_tile_size.assert_called_once_with(tile_size)
    mocked_validate_bounding_box.assert_called_once_with(bounding_box)
    mocked__validate_quantize.assert_called_once_with(quantize)


@patch('src.functional.data.grid_generator._validate_quantize')
@patch('src.functional.data.grid_generator.validate_epsg_code')
@patch('src.functional.data.grid_generator.validate_bounding_box')
@patch('src.functional.data.grid_generator.validate_tile_size')
def test__validate_generate_grid(
    mocked_validate_tile_size,
    mocked_validate_bounding_box,
    mocked_validate_epsg_code,
    mocked__validate_quantize,
) -> None:
    bounding_box = (-128, -128, 128, 128)
    tile_size = 256
    epsg_code = 25832
    quantize = True
    _validate_generate_grid(
        bounding_box=bounding_box,
        tile_size=tile_size,
        epsg_code=epsg_code,
        quantize=quantize,
    )

    mocked_validate_tile_size.assert_called_once_with(tile_size)
    mocked_validate_bounding_box.assert_called_once_with(bounding_box)
    mocked_validate_epsg_code.assert_called_once_with(epsg_code)
    mocked__validate_quantize.assert_called_once_with(quantize)


@patch('src.functional.data.grid_generator.validate_epsg_code')
@patch('src.functional.data.grid_generator.validate_bounding_box')
def test_validate_grid_generator(
    mocked_validate_bounding_box,
    mocked_validate_epsg_code,
) -> None:
    bounding_box = (-128, -128, 128, 128)
    epsg_code = 25832
    validate_grid_generator(
        bounding_box=bounding_box,
        epsg_code=epsg_code,
    )

    mocked_validate_bounding_box.assert_called_once_with(bounding_box)
    mocked_validate_epsg_code.assert_called_once_with(epsg_code)


def test__validate_quantize() -> None:
    quantize = True
    _validate_quantize(quantize)


@pytest.mark.parametrize('quantize, message', data_test__validate_quantize_type_error)
def test__validate_bounding_box_type_error(
    quantize,
    message: str,
) -> None:
    with pytest.raises(TypeError) as e:
        _validate_quantize(quantize)

    assert str(e.value) == message
