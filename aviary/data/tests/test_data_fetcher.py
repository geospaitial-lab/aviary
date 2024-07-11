from pathlib import Path
from unittest.mock import MagicMock, patch

# noinspection PyProtectedMember
from aviary._utils.types import (
    BoundingBox,
    DataFetcherInfo,
    DType,
    InterpolationMode,
)
from aviary.data.data_fetcher import (
    VRTFetcher,
    VRTFetcherConfig,
)


@patch('aviary.data.data_fetcher.vrt_fetcher_info')
def test_vrt_fetcher_init(
    mocked_vrt_fetcher_info: MagicMock,
) -> None:
    path = Path('test/test.vrt')
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0
    drop_channels = None
    expected_bounding_box = BoundingBox(
        x_min=-128,
        y_min=-128,
        x_max=128,
        y_max=128,
    )
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
    mocked_vrt_fetcher_info.return_value = expected
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
    mocked_vrt_fetcher_info.assert_called_once_with(
        path=path,
    )
    assert vrt_fetcher.src_bounding_box == expected_bounding_box
    assert vrt_fetcher.src_dtype == expected_dtype
    assert vrt_fetcher.src_epsg_code == expected_epsg_code
    assert vrt_fetcher.src_ground_sampling_distance == expected_ground_sampling_distance
    assert vrt_fetcher.src_num_channels == expected_num_channels


@patch('aviary.data.data_fetcher.vrt_fetcher_info')
def test_vrt_fetcher_from_config(
    mocked_vrt_fetcher_info: MagicMock,
) -> None:
    path = Path('test/test.vrt')
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0
    drop_channels = None
    expected_bounding_box = BoundingBox(
        x_min=-128,
        y_min=-128,
        x_max=128,
        y_max=128,
    )
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
    mocked_vrt_fetcher_info.return_value = expected
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
    mocked_vrt_fetcher_info.assert_called_once_with(
        path=path,
    )
    assert vrt_fetcher.src_bounding_box == expected_bounding_box
    assert vrt_fetcher.src_dtype == expected_dtype
    assert vrt_fetcher.src_epsg_code == expected_epsg_code
    assert vrt_fetcher.src_ground_sampling_distance == expected_ground_sampling_distance
    assert vrt_fetcher.src_num_channels == expected_num_channels


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
