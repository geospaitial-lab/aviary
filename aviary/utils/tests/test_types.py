import geopandas as gpd
import geopandas.testing
import pytest
import rasterio as rio
from shapely.geometry import box

from .data.data_test_types import (
    data_test_bounding_box_buffer,
    data_test_bounding_box_buffer_exceptions,
    data_test_bounding_box_init_exceptions,
    data_test_bounding_box_properties_exceptions,
    data_test_bounding_box_quantize,
    data_test_bounding_box_quantize_exceptions,
)
from ..types import (
    BoundingBox,
    BufferSize,
    DType,
    InterpolationMode,
    XMax,
    XMin,
    YMax,
    YMin,
)


def test_bounding_box_init() -> None:
    x_min = -128
    y_min = -128
    x_max = 128
    y_max = 128
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


@pytest.mark.parametrize('x_min, y_min, x_max, y_max, message', data_test_bounding_box_init_exceptions)
def test_bounding_box_init_exceptions(
    x_min: XMin,
    y_min: YMin,
    x_max: XMax,
    y_max: YMax,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        _ = BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )


def test_bounding_box_properties(
    bounding_box: BoundingBox,
) -> None:
    x_min = -192
    y_min = -192
    x_max = 192
    y_max = 192
    bounding_box.x_min = x_min
    bounding_box.y_min = y_min
    bounding_box.x_max = x_max
    bounding_box.y_max = y_max

    assert bounding_box.x_min == x_min
    assert bounding_box.y_min == y_min
    assert bounding_box.x_max == x_max
    assert bounding_box.y_max == y_max


@pytest.mark.parametrize('property_, value, message', data_test_bounding_box_properties_exceptions)
def test_bounding_box_properties_exceptions(
    property_: str,
    value: int,
    message: str,
    bounding_box: BoundingBox,
) -> None:
    with pytest.raises(ValueError, match=message):
        setattr(bounding_box, property_, value)


def test_bounding_box_from_gdf() -> None:
    geometry = [box(-128, -128, 128, 128)]
    epsg_code = 25832
    gdf = gpd.GeoDataFrame(
        geometry=geometry,
        crs=f'EPSG:{epsg_code}',
    )
    bounding_box = BoundingBox.from_gdf(gdf)
    expected_x_min = -128
    expected_y_min = -128
    expected_x_max = 128
    expected_y_max = 128
    expected = BoundingBox(
        x_min=expected_x_min,
        y_min=expected_y_min,
        x_max=expected_x_max,
        y_max=expected_y_max,
    )

    assert bounding_box == expected


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


@pytest.mark.parametrize('buffer_size, expected', data_test_bounding_box_buffer)
def test_bounding_box_buffer(
    buffer_size: BufferSize,
    expected: BoundingBox,
    bounding_box: BoundingBox,
) -> None:
    bounding_box = bounding_box.buffer(buffer_size)

    assert bounding_box == expected


@pytest.mark.parametrize('buffer_size, expected', data_test_bounding_box_buffer)
def test_bounding_box_buffer_inplace(
    buffer_size: BufferSize,
    expected: BoundingBox,
    bounding_box: BoundingBox,
) -> None:
    bounding_box.buffer(buffer_size, inplace=True)

    assert bounding_box == expected


@pytest.mark.parametrize('buffer_size, message', data_test_bounding_box_buffer_exceptions)
def test_bounding_box_buffer_exceptions(
    buffer_size: BufferSize,
    message: str,
    bounding_box: BoundingBox,
) -> None:
    with pytest.raises(ValueError, match=message):
        _ = bounding_box.buffer(buffer_size)


@pytest.mark.parametrize('bounding_box, value, expected', data_test_bounding_box_quantize)
def test_bounding_box_quantize(
    bounding_box: BoundingBox,
    value: int,
    expected: BoundingBox,
) -> None:
    bounding_box = bounding_box.quantize(value)

    assert bounding_box == expected


@pytest.mark.parametrize('bounding_box, value, expected', data_test_bounding_box_quantize)
def test_bounding_box_quantize_inplace(
    bounding_box: BoundingBox,
    value: int,
    expected: BoundingBox,
) -> None:
    bounding_box.quantize(value, inplace=True)

    assert bounding_box == expected


@pytest.mark.parametrize('value, message', data_test_bounding_box_quantize_exceptions)
def test_bounding_box_quantize_exceptions(
    value: int,
    message: str,
    bounding_box: BoundingBox,
) -> None:
    with pytest.raises(ValueError, match=message):
        _ = bounding_box.quantize(value)


def test_bounding_box_to_gdf(
    bounding_box: BoundingBox,
) -> None:
    gdf = bounding_box.to_gdf(epsg_code=25832)
    expected_geometry = [box(-128, -128, 128, 128)]
    expected_epsg_code = 25832
    expected = gpd.GeoDataFrame(
        geometry=expected_geometry,
        crs=f'EPSG:{expected_epsg_code}',
    )

    gpd.testing.assert_geodataframe_equal(gdf, expected)


def test_dtype_from_rio() -> None:
    assert DType.from_rio(rio.dtypes.bool_) == DType.BOOL
    assert DType.from_rio(rio.dtypes.float32) == DType.FLOAT32
    assert DType.from_rio(rio.dtypes.uint8) == DType.UINT8


def test_interpolation_mode_to_rio() -> None:
    assert InterpolationMode.BILINEAR.to_rio() == rio.enums.Resampling.bilinear
    assert InterpolationMode.NEAREST.to_rio() == rio.enums.Resampling.nearest
