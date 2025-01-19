import rasterio as rio

from aviary.core.enums import InterpolationMode


def test_interpolation_mode_to_rio() -> None:
    assert InterpolationMode.BILINEAR.to_rio() == rio.enums.Resampling.bilinear
    assert InterpolationMode.NEAREST.to_rio() == rio.enums.Resampling.nearest
