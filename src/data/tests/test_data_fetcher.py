from pathlib import Path
from unittest.mock import patch

from src.data.data_fetcher import (
    VRTDataFetcher,
)
from src.utils.types import (
    InterpolationMode,
)


def test_init_vrt_data_fetcher() -> None:
    path = Path('test/test.vrt')
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = None
    drop_channels = None
    vrt_data_fetcher = VRTDataFetcher(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
        drop_channels=drop_channels,
    )

    assert vrt_data_fetcher.path == path
    assert vrt_data_fetcher.tile_size == tile_size
    assert vrt_data_fetcher.ground_sampling_distance == ground_sampling_distance
    assert vrt_data_fetcher.interpolation_mode == interpolation_mode
    assert vrt_data_fetcher.buffer_size == buffer_size
    assert vrt_data_fetcher.drop_channels == drop_channels


@patch('src.data.data_fetcher.vrt_data_fetcher')
def test_call_vrt_data_fetcher(
    mocked_vrt_data_fetcher,
    vrt_data_fetcher: VRTDataFetcher,
) -> None:
    x_min = -128
    y_min = -128
    expected = 'expected'
    mocked_vrt_data_fetcher.return_value = expected
    data = vrt_data_fetcher(
        x_min=x_min,
        y_min=y_min,
    )

    mocked_vrt_data_fetcher.assert_called_once_with(
        x_min=x_min,
        y_min=y_min,
        path=vrt_data_fetcher.path,
        tile_size=vrt_data_fetcher.tile_size,
        ground_sampling_distance=vrt_data_fetcher.ground_sampling_distance,
        interpolation_mode=vrt_data_fetcher.interpolation_mode,
        buffer_size=vrt_data_fetcher.buffer_size,
        drop_channels=vrt_data_fetcher.drop_channels,
        fill_value=vrt_data_fetcher._FILL_VALUE,
    )
    assert data == expected
