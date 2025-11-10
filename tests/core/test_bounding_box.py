#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and / or modify it under the terms of the
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

import geopandas as gpd
import geopandas.testing
import pytest

from aviary.core.bounding_box import BoundingBox
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import (
    BufferSize,
    Coordinate,
    EPSGCode,
)
from tests.core.data.data_test_bounding_box import (
    data_test_bounding_box_area,
    data_test_bounding_box_buffer,
    data_test_bounding_box_buffer_exceptions,
    data_test_bounding_box_buffer_inplace,
    data_test_bounding_box_buffer_inplace_return,
    data_test_bounding_box_eq,
    data_test_bounding_box_from_gdf,
    data_test_bounding_box_from_gdf_exceptions,
    data_test_bounding_box_getitem,
    data_test_bounding_box_init_exceptions,
    data_test_bounding_box_snap,
    data_test_bounding_box_snap_exceptions,
    data_test_bounding_box_snap_inplace,
    data_test_bounding_box_snap_inplace_return,
    data_test_bounding_box_to_gdf,
)


def test_bounding_box_init() -> None:
    x_min = -128
    y_min = -64
    x_max = 128
    y_max = 192

    bounding_box = BoundingBox(
        x_min=x_min,
        y_min=y_min,
        x_max=x_max,
        y_max=y_max,
    )

    assert bounding_box.x_min == x_min
    assert bounding_box.y_min == y_min
    assert bounding_box.x_max == x_max
    assert bounding_box.y_max == y_max


@pytest.mark.parametrize(('x_min', 'y_min', 'x_max', 'y_max', 'message'), data_test_bounding_box_init_exceptions)
def test_bounding_box_init_exceptions(
    x_min: Coordinate,
    y_min: Coordinate,
    x_max: Coordinate,
    y_max: Coordinate,
    message: str,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )


def test_bounding_box_setters(
    bounding_box: BoundingBox,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        bounding_box.x_min = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        bounding_box.y_min = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        bounding_box.x_max = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        bounding_box.y_max = None


def test_bounding_box_serializability(
    bounding_box: BoundingBox,
) -> None:
    serialized_bounding_box = pickle.dumps(bounding_box)
    deserialized_bounding_box = pickle.loads(serialized_bounding_box)  # noqa: S301

    assert bounding_box == deserialized_bounding_box


@pytest.mark.parametrize(('bounding_box', 'expected'), data_test_bounding_box_area)
def test_bounding_box_area(
    bounding_box: BoundingBox,
    expected: int,
) -> None:
    assert bounding_box.area == expected


@pytest.mark.parametrize(('gdf', 'expected'), data_test_bounding_box_from_gdf)
def test_bounding_box_from_gdf(
    gdf: gpd.GeoDataFrame,
    expected: BoundingBox,
) -> None:
    bounding_box = BoundingBox.from_gdf(gdf=gdf)

    assert bounding_box == expected


@pytest.mark.parametrize(('gdf', 'message'), data_test_bounding_box_from_gdf_exceptions)
def test_bounding_box_from_gdf_exceptions(
    gdf: gpd.GeoDataFrame,
    message: str,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = BoundingBox.from_gdf(gdf=gdf)


@pytest.mark.parametrize(('other', 'expected'), data_test_bounding_box_eq)
def test_bounding_box_eq(
    other: object,
    expected: bool,
    bounding_box: BoundingBox,
) -> None:
    equals = bounding_box == other

    assert equals is expected


def test_bounding_box_len(
    bounding_box: BoundingBox,
) -> None:
    expected = 4

    assert len(bounding_box) == expected


@pytest.mark.parametrize(('index', 'expected'), data_test_bounding_box_getitem)
def test_bounding_box_getitem(
    index: int,
    expected: Coordinate,
    bounding_box: BoundingBox,
) -> None:
    assert bounding_box[index] == expected


def test_bounding_box_iter(
    bounding_box: BoundingBox,
) -> None:
    expected_x_min = -128
    expected_y_min = -64
    expected_x_max = 128
    expected_y_max = 192
    expected = [
        expected_x_min,
        expected_y_min,
        expected_x_max,
        expected_y_max,
    ]

    assert list(bounding_box) == expected


@pytest.mark.parametrize(('bounding_box', 'buffer_size', 'expected'), data_test_bounding_box_buffer)
def test_bounding_box_buffer(
    bounding_box: BoundingBox,
    buffer_size: BufferSize,
    expected: BoundingBox,
) -> None:
    copied_bounding_box = copy.deepcopy(bounding_box)

    bounding_box_ = bounding_box.buffer(
        buffer_size=buffer_size,
        inplace=False,
    )

    assert bounding_box == copied_bounding_box
    assert bounding_box_ == expected
    assert id(bounding_box_) != id(bounding_box)


@pytest.mark.parametrize(('bounding_box', 'buffer_size', 'expected'), data_test_bounding_box_buffer_inplace)
def test_bounding_box_buffer_inplace(
    bounding_box: BoundingBox,
    buffer_size: BufferSize,
    expected: BoundingBox,
) -> None:
    bounding_box.buffer(
        buffer_size=buffer_size,
        inplace=True,
    )

    assert bounding_box == expected


@pytest.mark.parametrize(('bounding_box', 'buffer_size', 'expected'), data_test_bounding_box_buffer_inplace_return)
def test_bounding_box_buffer_inplace_return(
    bounding_box: BoundingBox,
    buffer_size: BufferSize,
    expected: BoundingBox,
) -> None:
    bounding_box_ = bounding_box.buffer(
        buffer_size=buffer_size,
        inplace=True,
    )

    assert bounding_box == expected
    assert bounding_box_ == expected
    assert id(bounding_box_) == id(bounding_box)


@pytest.mark.parametrize(('buffer_size', 'message'), data_test_bounding_box_buffer_exceptions)
def test_bounding_box_buffer_exceptions(
    buffer_size: BufferSize,
    message: str,
    bounding_box: BoundingBox,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = bounding_box.buffer(
            buffer_size=buffer_size,
            inplace=False,
        )


def test_bounding_box_buffer_defaults() -> None:
    signature = inspect.signature(BoundingBox.buffer)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


@pytest.mark.parametrize(('bounding_box', 'value', 'expected'), data_test_bounding_box_snap)
def test_bounding_box_snap(
    bounding_box: BoundingBox,
    value: int,
    expected: BoundingBox,
) -> None:
    copied_bounding_box = copy.deepcopy(bounding_box)

    bounding_box_ = bounding_box.snap(
        value=value,
        inplace=False,
    )

    assert bounding_box == copied_bounding_box
    assert bounding_box_ == expected
    assert id(bounding_box_) != id(bounding_box)


@pytest.mark.parametrize(('bounding_box', 'value', 'expected'), data_test_bounding_box_snap_inplace)
def test_bounding_box_snap_inplace(
    bounding_box: BoundingBox,
    value: int,
    expected: BoundingBox,
) -> None:
    bounding_box.snap(
        value=value,
        inplace=True,
    )

    assert bounding_box == expected


@pytest.mark.parametrize(('bounding_box', 'value', 'expected'), data_test_bounding_box_snap_inplace_return)
def test_bounding_box_snap_inplace_return(
    bounding_box: BoundingBox,
    value: int,
    expected: BoundingBox,
) -> None:
    bounding_box_ = bounding_box.snap(
        value=value,
        inplace=True,
    )

    assert bounding_box == expected
    assert bounding_box_ == expected
    assert id(bounding_box_) == id(bounding_box)


@pytest.mark.parametrize(('value', 'message'), data_test_bounding_box_snap_exceptions)
def test_bounding_box_snap_exceptions(
    value: int,
    message: str,
    bounding_box: BoundingBox,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = bounding_box.snap(
            value=value,
            inplace=False,
        )


def test_bounding_box_snap_defaults() -> None:
    signature = inspect.signature(BoundingBox.snap)
    inplace = signature.parameters['inplace'].default

    expected_inplace = False

    assert inplace is expected_inplace


@pytest.mark.parametrize(('epsg_code', 'expected'), data_test_bounding_box_to_gdf)
def test_bounding_box_to_gdf(
    epsg_code: EPSGCode | None,
    expected: gpd.GeoDataFrame,
    bounding_box: BoundingBox,
) -> None:
    gdf = bounding_box.to_gdf(epsg_code=epsg_code)

    gpd.testing.assert_geodataframe_equal(gdf, expected)
