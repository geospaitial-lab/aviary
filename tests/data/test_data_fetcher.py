from pathlib import Path
from unittest.mock import MagicMock, patch

# noinspection PyProtectedMember
from aviary._utils.types import InterpolationMode
from aviary.data.data_fetcher import (
    VRTFetcher,
    VRTFetcherConfig,
)


def test_vrt_fetcher_init() -> None:
    path = Path('test/test.vrt')
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0
    drop_channels = None
    vrt_fetcher = VRTFetcher(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
        drop_channels=drop_channels,
    )

    assert vrt_fetcher.path == path
    assert vrt_fetcher.tile_size == tile_size
    assert vrt_fetcher.ground_sampling_distance == ground_sampling_distance
    assert vrt_fetcher.interpolation_mode == interpolation_mode
    assert vrt_fetcher.buffer_size == buffer_size
    assert vrt_fetcher.drop_channels == drop_channels


def test_vrt_fetcher_from_config() -> None:
    path = Path('test/test.vrt')
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0
    drop_channels = None
    vrt_fetcher_config = VRTFetcherConfig(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
        drop_channels=drop_channels,
    )
    vrt_fetcher = VRTFetcher.from_config(vrt_fetcher_config)

    assert vrt_fetcher.path == path
    assert vrt_fetcher.tile_size == tile_size
    assert vrt_fetcher.ground_sampling_distance == ground_sampling_distance
    assert vrt_fetcher.interpolation_mode == interpolation_mode
    assert vrt_fetcher.buffer_size == buffer_size
    assert vrt_fetcher.drop_channels == drop_channels


@patch('aviary.data.data_fetcher.vrt_fetcher')
def test_vrt_fetcher_call(
    mocked_vrt_fetcher: MagicMock,
    vrt_fetcher: VRTFetcher,
) -> None:
    x_min = -128
    y_min = -128
    expected = 'expected'
    mocked_vrt_fetcher.return_value = expected
    data = vrt_fetcher(
        x_min=x_min,
        y_min=y_min,
    )

    mocked_vrt_fetcher.assert_called_once_with(
        x_min=x_min,
        y_min=y_min,
        path=vrt_fetcher.path,
        tile_size=vrt_fetcher.tile_size,
        ground_sampling_distance=vrt_fetcher.ground_sampling_distance,
        interpolation_mode=vrt_fetcher.interpolation_mode,
        buffer_size=vrt_fetcher.buffer_size,
        drop_channels=vrt_fetcher.drop_channels,
        fill_value=vrt_fetcher._FILL_VALUE,
    )
    assert data == expected
