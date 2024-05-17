from pathlib import Path
from unittest.mock import patch

from ...data import (
    VRTDataFetcher,
)
from ...utils.types import (
    DataFetcherInfo,
    DType,
    InterpolationMode,
)


@patch('aviary.data.data_fetcher.vrt_data_fetcher_info')
def test_init_vrt_data_fetcher(
    mocked_vrt_data_fetcher_info,
) -> None:
    path = Path('test/test.vrt')
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = None
    drop_channels = None
    expected_bounding_box = (-128, -128, 128, 128)
    expected_dtype = [DType.UINT8, DType.UINT8, DType.UINT8]
    expected_epsg_code = 25832
    expected_ground_sampling_distance = .5
    expected_num_channels = 3
    expected = DataFetcherInfo(
        bounding_box=expected_bounding_box,
        dtype=expected_dtype,
        epsg_code=expected_epsg_code,
        ground_sampling_distance=expected_ground_sampling_distance,
        num_channels=expected_num_channels,
    )
    mocked_vrt_data_fetcher_info.return_value = expected
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
    mocked_vrt_data_fetcher_info.assert_called_once_with(
        path=path,
    )
    assert vrt_data_fetcher.src_bounding_box == expected_bounding_box
    assert vrt_data_fetcher.src_dtype == expected_dtype
    assert vrt_data_fetcher.src_epsg_code == expected_epsg_code
    assert vrt_data_fetcher.src_ground_sampling_distance == expected_ground_sampling_distance
    assert vrt_data_fetcher.src_num_channels == expected_num_channels


@patch('aviary.data.data_fetcher.vrt_data_fetcher')
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
