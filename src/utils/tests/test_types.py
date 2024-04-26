import rasterio as rio

from src.utils.types import (
    InterpolationMode,
)


def test_interpolation_mode_to_rio():
    assert InterpolationMode.BILINEAR.to_rio() == rio.enums.Resampling.bilinear
    assert InterpolationMode.NEAREST.to_rio() == rio.enums.Resampling.nearest
