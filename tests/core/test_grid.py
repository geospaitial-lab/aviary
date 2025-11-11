#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

import copy
import inspect
import pickle
from unittest.mock import MagicMock

import geopandas as gpd
import geopandas.testing
import numpy as np
import pytest

from aviary.core.bounding_box import BoundingBox
from aviary.core.exceptions import AviaryUserError
from aviary.core.grid import Grid
from aviary.core.type_aliases import (
    Coordinates,
    CoordinatesSet,
    EPSGCode,
    TileSize,
)
from aviary.utils.coordinates_filter import CoordinatesFilter
from tests.core.data.data_test_grid import (
    data_test_grid_add,
    data_test_grid_add_exceptions,
    data_test_grid_and,
    data_test_grid_and_exceptions,
    data_test_grid_append,
    data_test_grid_append_exceptions,
    data_test_grid_append_inplace,
    data_test_grid_append_inplace_return,
    data_test_grid_area,
    data_test_grid_bool,
    data_test_grid_chunk,
    data_test_grid_chunk_exceptions,
    data_test_grid_contains,
    data_test_grid_contains_exceptions,
    data_test_grid_eq,
    data_test_grid_from_bounding_box,
    data_test_grid_from_bounding_box_exceptions,
    data_test_grid_from_gdf,
    data_test_grid_from_gdf_exceptions,
    data_test_grid_from_grids,
    data_test_grid_from_grids_exceptions,
    data_test_grid_from_json,
    data_test_grid_from_json_exceptions,
    data_test_grid_getitem,
    data_test_grid_getitem_slice,
    data_test_grid_init,
    data_test_grid_init_exceptions,
    data_test_grid_or,
    data_test_grid_or_exceptions,
    data_test_grid_remove,
    data_test_grid_remove_exceptions,
    data_test_grid_remove_inplace,
    data_test_grid_remove_inplace_return,
    data_test_grid_snap,
    data_test_grid_snap_inplace,
    data_test_grid_snap_inplace_return,
    data_test_grid_sub,
    data_test_grid_sub_exceptions,
    data_test_grid_to_gdf,
)


@pytest.mark.parametrize(
    (
        'coordinates',
        'tile_size',
        'expected_coordinates',
        'expected_tile_size',
    ),
    data_test_grid_init,
)
def test_grid_init(
    coordinates: CoordinatesSet,
    tile_size: TileSize,
    expected_coordinates: CoordinatesSet,
    expected_tile_size: TileSize,
) -> None:
    grid = Grid(
        coordinates=coordinates,
        tile_size=tile_size,
    )

    np.testing.assert_array_equal(grid.coordinates, expected_coordinates)
    assert grid.tile_size == expected_tile_size


@pytest.mark.parametrize(('coordinates', 'tile_size', 'message'), data_test_grid_init_exceptions)
def test_grid_init_exceptions(
    coordinates: CoordinatesSet,
    tile_size: TileSize,
    message: str,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = Grid(
            coordinates=coordinates,
            tile_size=tile_size,
        )


def test_grid_mutability(
    grid_coordinates: CoordinatesSet,
) -> None:
    tile_size = 128

    grid = Grid(
        coordinates=grid_coordinates,
        tile_size=tile_size,
    )

    assert id(grid._coordinates) != id(grid_coordinates)
    assert id(grid.coordinates) != id(grid._coordinates)


def test_grid_setters(
    grid: Grid,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        grid.coordinates = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        grid.tile_size = None


def test_grid_serializability(
    grid: Grid,
) -> None:
    serialized_grid = pickle.dumps(grid)
    deserialized_grid = pickle.loads(serialized_grid)  # noqa: S301

    assert grid == deserialized_grid


@pytest.mark.parametrize(('grid', 'expected'), data_test_grid_area)
def test_grid_area(
    grid: Grid,
    expected: int,
) -> None:
    assert grid.area == expected


@pytest.mark.parametrize(
    (
        'bounding_box',
        'tile_size',
        'snap',
        'expected',
    ),
    data_test_grid_from_bounding_box,
)
def test_grid_from_bounding_box(
    bounding_box: BoundingBox,
    tile_size: TileSize,
    snap: bool,
    expected: Grid,
) -> None:
    grid = Grid.from_bounding_box(
        bounding_box=bounding_box,
        tile_size=tile_size,
        snap=snap,
    )

    assert grid == expected


@pytest.mark.parametrize(('tile_size', 'message'), data_test_grid_from_bounding_box_exceptions)
def test_grid_from_bounding_box_exceptions(
    tile_size: TileSize,
    message: str,
    bounding_box: BoundingBox,
) -> None:
    snap = True

    with pytest.raises(AviaryUserError, match=message):
        _ = Grid.from_bounding_box(
            bounding_box=bounding_box,
            tile_size=tile_size,
            snap=snap,
        )


def test_grid_from_bounding_box_defaults() -> None:
    signature = inspect.signature(Grid.from_bounding_box)
    snap = signature.parameters['snap'].default

    expected_snap = True

    assert snap is expected_snap


@pytest.mark.parametrize(('gdf', 'tile_size', 'snap', 'expected'), data_test_grid_from_gdf)
def test_grid_from_gdf(
    gdf: gpd.GeoDataFrame,
    tile_size: TileSize,
    snap: bool,
    expected: Grid,
) -> None:
    grid = Grid.from_gdf(
        gdf=gdf,
        tile_size=tile_size,
        snap=snap,
    )

    assert grid == expected


@pytest.mark.parametrize(('gdf', 'tile_size', 'message'), data_test_grid_from_gdf_exceptions)
def test_grid_from_gdf_exceptions(
    gdf: gpd.GeoDataFrame,
    tile_size: TileSize,
    message: str,
) -> None:
    snap = True

    with pytest.raises(AviaryUserError, match=message):
        _ = Grid.from_gdf(
            gdf=gdf,
            tile_size=tile_size,
            snap=snap,
        )


def test_grid_from_gdf_defaults() -> None:
    signature = inspect.signature(Grid.from_gdf)
    snap = signature.parameters['snap'].default

    expected_snap = True

    assert snap is expected_snap


@pytest.mark.parametrize(('json_string', 'expected'), data_test_grid_from_json)
def test_grid_from_json(
    json_string: str,
    expected: Grid,
) -> None:
    grid = Grid.from_json(json_string=json_string)

    assert grid == expected


@pytest.mark.parametrize(('json_string', 'message'), data_test_grid_from_json_exceptions)
def test_grid_from_json_exceptions(
    json_string: str,
    message: str,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = Grid.from_json(json_string=json_string)


@pytest.mark.parametrize(('grids', 'expected'), data_test_grid_from_grids)
def test_grid_from_grids(
    grids: list[Grid],
    expected: Grid,
) -> None:
    grid = Grid.from_grids(grids=grids)

    assert grid == expected


@pytest.mark.parametrize(('grids', 'message'), data_test_grid_from_grids_exceptions)
def test_grid_from_grids_exceptions(
    grids: list[Grid],
    message: str,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = Grid.from_grids(grids=grids)


@pytest.mark.skip(reason='Not implemented')
def test_grid_from_config() -> None:
    pass


@pytest.mark.parametrize(('other', 'expected'), data_test_grid_eq)
def test_grid_eq(
    other: object,
    expected: bool,
    grid: Grid,
) -> None:
    equals = grid == other

    assert equals is expected


def test_grid_len(
    grid: Grid,
) -> None:
    expected = 4

    assert len(grid) == expected


@pytest.mark.parametrize(('grid', 'expected'), data_test_grid_bool)
def test_grid_bool(
    grid: Grid,
    expected: bool,
) -> None:
    assert bool(grid) is expected


@pytest.mark.parametrize(('coordinates', 'expected'), data_test_grid_contains)
def test_grid_contains(
    coordinates: Coordinates | CoordinatesSet,
    expected: bool,
    grid: Grid,
) -> None:
    contains = coordinates in grid

    assert contains is expected


@pytest.mark.parametrize(('coordinates', 'message'), data_test_grid_contains_exceptions)
def test_grid_contains_exceptions(
    coordinates: CoordinatesSet,
    message: str,
    grid: Grid,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = coordinates in grid


@pytest.mark.parametrize(('index', 'expected'), data_test_grid_getitem)
def test_grid_getitem(
    index: int,
    expected: Coordinates,
    grid: Grid,
) -> None:
    coordinates = grid[index]

    assert coordinates == expected


@pytest.mark.parametrize(('index', 'expected'), data_test_grid_getitem_slice)
def test_grid_getitem_slice(
    index: slice,
    expected: Grid,
    grid: Grid,
) -> None:
    grid = grid[index]

    assert grid == expected


def test_grid_iter(
    grid: Grid,
) -> None:
    expected = [
        (-128, -128),
        (0, -128),
        (-128, 0),
        (0, 0),
    ]

    assert list(grid) == expected


@pytest.mark.parametrize(('other', 'expected'), data_test_grid_add)
def test_grid_add(
    other: Grid,
    expected: Grid,
    grid: Grid,
) -> None:
    grid = grid + other

    assert grid == expected


@pytest.mark.parametrize(('other', 'message'), data_test_grid_add_exceptions)
def test_grid_add_exceptions(
    other: Grid,
    message: str,
    grid: Grid,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = grid + other


@pytest.mark.parametrize(('other', 'expected'), data_test_grid_sub)
def test_grid_sub(
    other: Grid,
    expected: Grid,
    grid: Grid,
) -> None:
    grid = grid - other

    assert grid == expected


@pytest.mark.parametrize(('other', 'message'), data_test_grid_sub_exceptions)
def test_grid_sub_exceptions(
    other: Grid,
    message: str,
    grid: Grid,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = grid - other


@pytest.mark.parametrize(('other', 'expected'), data_test_grid_and)
def test_grid_and(
    other: Grid,
    expected: Grid,
    grid: Grid,
) -> None:
    grid = grid & other

    assert grid == expected


@pytest.mark.parametrize(('other', 'message'), data_test_grid_and_exceptions)
def test_grid_and_exceptions(
    other: Grid,
    message: str,
    grid: Grid,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = grid & other


@pytest.mark.parametrize(('other', 'expected'), data_test_grid_or)
def test_grid_or(
    other: Grid,
    expected: Grid,
    grid: Grid,
) -> None:
    grid = grid | other

    assert grid == expected


@pytest.mark.parametrize(('other', 'message'), data_test_grid_or_exceptions)
def test_grid_or_exceptions(
    other: Grid,
    message: str,
    grid: Grid,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = grid | other


@pytest.mark.parametrize(('grid', 'coordinates', 'expected'), data_test_grid_append)
def test_grid_append(
    grid: Grid,
    coordinates: Coordinates | CoordinatesSet,
    expected: Grid,
) -> None:
    copied_grid = copy.deepcopy(grid)

    grid_ = grid.append(
        coordinates=coordinates,
        inplace=False,
    )

    assert grid == copied_grid
    assert grid_ == expected
    assert id(grid_) != id(grid)
    assert id(grid_.coordinates) != id(grid.coordinates)


@pytest.mark.parametrize(('grid', 'coordinates', 'expected'), data_test_grid_append_inplace)
def test_grid_append_inplace(
    grid: Grid,
    coordinates: Coordinates | CoordinatesSet,
    expected: Grid,
) -> None:
    grid.append(
        coordinates=coordinates,
        inplace=True,
    )

    assert grid == expected


@pytest.mark.parametrize(('grid', 'coordinates', 'expected'), data_test_grid_append_inplace_return)
def test_grid_append_inplace_return(
    grid: Grid,
    coordinates: Coordinates | CoordinatesSet,
    expected: Grid,
) -> None:
    grid_ = grid.append(
        coordinates=coordinates,
        inplace=True,
    )

    assert grid == expected
    assert grid_ == expected
    assert id(grid_) == id(grid)
    assert id(grid_.coordinates) != id(grid.coordinates)


@pytest.mark.parametrize(('coordinates', 'message'), data_test_grid_append_exceptions)
def test_grid_append_exceptions(
    coordinates: CoordinatesSet,
    message: str,
    grid: Grid,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = grid.append(
            coordinates=coordinates,
            inplace=False,
        )


def test_grid_append_defaults() -> None:
    signature = inspect.signature(Grid.append)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


@pytest.mark.parametrize(('grid', 'num_chunks', 'expected'), data_test_grid_chunk)
def test_grid_chunk(
    grid: Grid,
    num_chunks: int,
    expected: list[Grid],
) -> None:
    chunks = grid.chunk(num_chunks=num_chunks)

    assert chunks == expected


@pytest.mark.parametrize(('num_chunks', 'message'), data_test_grid_chunk_exceptions)
def test_grid_chunk_exceptions(
    num_chunks: int,
    message: str,
    grid: Grid,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = grid.chunk(num_chunks=num_chunks)


def test_grid_filter(
    grid: Grid,
    grid_coordinates: CoordinatesSet,
) -> None:
    copied_grid = copy.deepcopy(grid)

    coordinates_filter = MagicMock(spec=CoordinatesFilter)
    coordinates_filter.return_value = grid_coordinates

    grid_ = grid.filter(
        coordinates_filter=coordinates_filter,
        inplace=False,
    )

    expected_coordinates = grid_coordinates
    expected_tile_size = 128
    expected = Grid(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert grid == copied_grid
    assert grid_ == expected
    assert id(grid_) != id(grid)
    coordinates_filter.assert_called_once()


def test_grid_filter_inplace(
    grid: Grid,
    grid_coordinates: CoordinatesSet,
) -> None:
    coordinates_filter = MagicMock(spec=CoordinatesFilter)
    coordinates_filter.return_value = grid_coordinates

    grid.filter(
        coordinates_filter=coordinates_filter,
        inplace=True,
    )

    expected_coordinates = grid_coordinates
    expected_tile_size = 128
    expected = Grid(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert grid == expected
    coordinates_filter.assert_called_once()


def test_grid_filter_inplace_return(
    grid: Grid,
    grid_coordinates: CoordinatesSet,
) -> None:
    coordinates_filter = MagicMock(spec=CoordinatesFilter)
    coordinates_filter.return_value = grid_coordinates

    grid_ = grid.filter(
        coordinates_filter=coordinates_filter,
        inplace=True,
    )

    expected_coordinates = grid_coordinates
    expected_tile_size = 128
    expected = Grid(
        coordinates=expected_coordinates,
        tile_size=expected_tile_size,
    )

    assert grid == expected
    assert grid_ == expected
    assert id(grid_) == id(grid)
    coordinates_filter.assert_called_once()


def test_grid_filter_defaults() -> None:
    signature = inspect.signature(Grid.filter)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


@pytest.mark.parametrize(('grid', 'coordinates', 'expected'), data_test_grid_remove)
def test_grid_remove(
    grid: Grid,
    coordinates: Coordinates | CoordinatesSet,
    expected: Grid,
) -> None:
    copied_grid = copy.deepcopy(grid)

    grid_ = grid.remove(
        coordinates=coordinates,
        inplace=False,
    )

    assert grid == copied_grid
    assert grid_ == expected
    assert id(grid_) != id(grid)
    assert id(grid_.coordinates) != id(grid.coordinates)


@pytest.mark.parametrize(('grid', 'coordinates', 'expected'), data_test_grid_remove_inplace)
def test_grid_remove_inplace(
    grid: Grid,
    coordinates: Coordinates | CoordinatesSet,
    expected: Grid,
) -> None:
    grid.remove(
        coordinates=coordinates,
        inplace=True,
    )

    assert grid == expected


@pytest.mark.parametrize(('grid', 'coordinates', 'expected'), data_test_grid_remove_inplace_return)
def test_grid_remove_inplace_return(
    grid: Grid,
    coordinates: Coordinates | CoordinatesSet,
    expected: Grid,
) -> None:
    grid_ = grid.remove(
        coordinates=coordinates,
        inplace=True,
    )

    assert grid == expected
    assert grid_ == expected
    assert id(grid_) == id(grid)
    assert id(grid_.coordinates) != id(grid.coordinates)


@pytest.mark.parametrize(('coordinates', 'message'), data_test_grid_remove_exceptions)
def test_grid_remove_exceptions(
    coordinates: CoordinatesSet,
    message: str,
    grid: Grid,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = grid.remove(
            coordinates=coordinates,
            inplace=False,
        )


def test_grid_remove_defaults() -> None:
    signature = inspect.signature(Grid.remove)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


@pytest.mark.parametrize(('grid', 'expected'), data_test_grid_snap)
def test_grid_snap(
    grid: Grid,
    expected: Grid,
) -> None:
    copied_grid = copy.deepcopy(grid)

    grid_ = grid.snap(inplace=False)

    assert grid == copied_grid
    assert grid_ == expected
    assert id(grid_) != id(grid)


@pytest.mark.parametrize(('grid', 'expected'), data_test_grid_snap_inplace)
def test_grid_snap_inplace(
    grid: Grid,
    expected: Grid,
) -> None:
    grid.snap(inplace=True)

    assert grid == expected


@pytest.mark.parametrize(('grid', 'expected'), data_test_grid_snap_inplace_return)
def test_grid_snap_inplace_return(
    grid: Grid,
    expected: Grid,
) -> None:
    grid_ = grid.snap(inplace=True)

    assert grid == expected
    assert grid_ == expected
    assert id(grid_) == id(grid)


def test_grid_snap_defaults() -> None:
    signature = inspect.signature(Grid.snap)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


@pytest.mark.parametrize(('epsg_code', 'expected'), data_test_grid_to_gdf)
def test_grid_to_gdf(
    epsg_code: EPSGCode | None,
    expected: gpd.GeoDataFrame,
    grid: Grid,
) -> None:
    gdf = grid.to_gdf(epsg_code=epsg_code)

    gpd.testing.assert_geodataframe_equal(gdf, expected)


def test_grid_to_json(
    grid: Grid,
) -> None:
    json_string = grid.to_json()

    expected = '{"coordinates": [[-128, -128], [0, -128], [-128, 0], [0, 0]], "tile_size": 128}'

    assert json_string == expected


@pytest.mark.skip(reason='Not implemented')
def test_grid_config() -> None:
    pass
