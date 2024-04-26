import rasterio as rio

from src.utils.types import (
    DType,
    InterpolationMode,
)


def test_dtype_from_rio():
    assert DType.from_rio(rio.dtypes.bool_) == DType.BOOL
    assert DType.from_rio(rio.dtypes.float32) == DType.FLOAT32
    assert DType.from_rio(rio.dtypes.uint8) == DType.UINT8


def test_interpolation_mode_to_rio():
    assert InterpolationMode.BILINEAR.to_rio() == rio.enums.Resampling.bilinear
    assert InterpolationMode.NEAREST.to_rio() == rio.enums.Resampling.nearest
