import copy
import inspect
import pickle

import geopandas as gpd
import geopandas.testing
import pytest
from shapely.geometry import box

from aviary.core.bounding_box import BoundingBox
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import (
    BufferSize,
    Coordinate,
)
from tests.core.data.data_test_bounding_box import (
    data_test_bounding_box_area,
    data_test_bounding_box_buffer,
    data_test_bounding_box_buffer_exceptions,
    data_test_bounding_box_quantize,
    data_test_bounding_box_quantize_exceptions,
    data_test_bounding_box_validation,
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


@pytest.mark.parametrize(('x_min', 'y_min', 'x_max', 'y_max', 'message'), data_test_bounding_box_validation)
def test_bounding_box_validation(
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


def test_bounding_box_from_gdf() -> None:
    geometry = [box(-128, -64, 128, 192)]
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    bounding_box = BoundingBox.from_gdf(gdf)
    expected_x_min = -128
    expected_y_min = -64
    expected_x_max = 128
    expected_y_max = 192
    expected = BoundingBox(
        x_min=expected_x_min,
        y_min=expected_y_min,
        x_max=expected_x_max,
        y_max=expected_y_max,
    )

    assert bounding_box == expected


def test_bounding_box_eq(
    bounding_box: BoundingBox,
) -> None:
    other_x_min = -128
    other_y_min = -64
    other_x_max = 128
    other_y_max = 192
    other_bounding_box = BoundingBox(
        x_min=other_x_min,
        y_min=other_y_min,
        x_max=other_x_max,
        y_max=other_y_max,
    )

    assert bounding_box == other_bounding_box

    other_x_min = -64
    other_y_min = -64
    other_x_max = 64
    other_y_max = 64
    other_bounding_box = BoundingBox(
        x_min=other_x_min,
        y_min=other_y_min,
        x_max=other_x_max,
        y_max=other_y_max,
    )

    assert bounding_box != other_bounding_box

    other = 'invalid'

    assert bounding_box != other


def test_bounding_box_len(
    bounding_box: BoundingBox,
) -> None:
    expected = 4

    assert len(bounding_box) == expected


def test_bounding_box_getitem(
    bounding_box: BoundingBox,
) -> None:
    expected_x_min = bounding_box.x_min
    expected_y_min = bounding_box.y_min
    expected_x_max = bounding_box.x_max
    expected_y_max = bounding_box.y_max

    assert bounding_box[0] == expected_x_min
    assert bounding_box[1] == expected_y_min
    assert bounding_box[2] == expected_x_max
    assert bounding_box[3] == expected_y_max
    assert bounding_box[-1] == expected_y_max
    assert bounding_box[-2] == expected_x_max
    assert bounding_box[-3] == expected_y_min
    assert bounding_box[-4] == expected_x_min


def test_bounding_box_iter(
    bounding_box: BoundingBox,
) -> None:
    expected = [
        bounding_box.x_min,
        bounding_box.y_min,
        bounding_box.x_max,
        bounding_box.y_max,
    ]

    assert list(bounding_box) == expected


@pytest.mark.parametrize(('buffer_size', 'expected'), data_test_bounding_box_buffer)
def test_bounding_box_buffer(
    buffer_size: BufferSize,
    expected: BoundingBox,
    bounding_box: BoundingBox,
) -> None:
    copied_bounding_box = copy.deepcopy(bounding_box)

    bounding_box_ = bounding_box.buffer(
        buffer_size=buffer_size,
        inplace=False,
    )

    assert bounding_box == copied_bounding_box
    assert bounding_box_ == expected


@pytest.mark.parametrize(('buffer_size', 'expected'), data_test_bounding_box_buffer)
def test_bounding_box_buffer_inplace(
    buffer_size: BufferSize,
    expected: BoundingBox,
    bounding_box: BoundingBox,
) -> None:
    bounding_box.buffer(
        buffer_size=buffer_size,
        inplace=True,
    )

    assert bounding_box == expected


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

    assert inplace is False


@pytest.mark.parametrize(('bounding_box', 'value', 'expected'), data_test_bounding_box_quantize)
def test_bounding_box_quantize(
    bounding_box: BoundingBox,
    value: int,
    expected: BoundingBox,
) -> None:
    copied_bounding_box = copy.deepcopy(bounding_box)

    bounding_box_ = bounding_box.quantize(
        value=value,
        inplace=False,
    )

    assert bounding_box == copied_bounding_box
    assert bounding_box_ == expected


@pytest.mark.parametrize(('bounding_box', 'value', 'expected'), data_test_bounding_box_quantize)
def test_bounding_box_quantize_inplace(
    bounding_box: BoundingBox,
    value: int,
    expected: BoundingBox,
) -> None:
    bounding_box.quantize(
        value=value,
        inplace=True,
    )

    assert bounding_box == expected


@pytest.mark.parametrize(('value', 'message'), data_test_bounding_box_quantize_exceptions)
def test_bounding_box_quantize_exceptions(
    value: int,
    message: str,
    bounding_box: BoundingBox,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = bounding_box.quantize(
            value=value,
            inplace=False,
        )


def test_bounding_box_quantize_defaults() -> None:
    signature = inspect.signature(BoundingBox.quantize)
    inplace = signature.parameters['inplace'].default

    assert inplace is False


def test_bounding_box_to_gdf(
    bounding_box: BoundingBox,
) -> None:
    epsg_code = 25832
    gdf = bounding_box.to_gdf(epsg_code=epsg_code)
    expected_geometry = [box(-128, -64, 128, 192)]
    expected_epsg_code = 25832
    expected = gpd.GeoDataFrame(
        geometry=expected_geometry,
        crs=f'EPSG:{expected_epsg_code}',
    )

    gpd.testing.assert_geodataframe_equal(gdf, expected)
