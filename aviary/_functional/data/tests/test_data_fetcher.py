from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import numpy.typing as npt
import pytest

from ..data_fetcher import (
    _compute_tile_size_pixels,
    _drop_channels,
    _permute_data,
    vrt_data_fetcher_info,
)
from .data.data_test_data_fetcher import (
    data_test__compute_tile_size_pixels,
    data_test__drop_channels,
    data_test__permute_data,
)
from ...._utils.types import (
    BoundingBox,
    BufferSize,
    DataFetcherInfo,
    DType,
    GroundSamplingDistance,
    TileSize,
)


@pytest.mark.skip(reason='Not implemented')
def test_vrt_data_fetcher() -> None:
    pass


@pytest.mark.parametrize(
    'tile_size, buffer_size, ground_sampling_distance, expected',
    data_test__compute_tile_size_pixels,
)
def test__compute_tile_size_pixels(
    tile_size: TileSize,
    buffer_size: BufferSize | None,
    ground_sampling_distance: GroundSamplingDistance,
    expected: int,
) -> None:
    tile_size_pixels = _compute_tile_size_pixels(
        tile_size=tile_size,
        buffer_size=buffer_size,
        ground_sampling_distance=ground_sampling_distance,
    )

    assert tile_size_pixels == expected


@pytest.mark.parametrize('data, drop_channels, expected', data_test__drop_channels)
def test__drop_channels(
    data: npt.NDArray,
    drop_channels: list[int] | None,
    expected: npt.NDArray,
) -> None:
    data = _drop_channels(
        data=data,
        drop_channels=drop_channels,
    )

    np.testing.assert_array_equal(data, expected)


@pytest.mark.parametrize('data, expected', data_test__permute_data)
def test__permute_data(
    data: npt.NDArray,
    expected: npt.NDArray,
) -> None:
    data = _permute_data(
        data=data,
    )

    np.testing.assert_array_equal(data, expected)


@patch('aviary._functional.data.data_fetcher.rio.open')
def test_vrt_data_fetcher_info(
    mocked_rio_open,
) -> None:
    path = Path('test/test.vrt')
    mocked_src = MagicMock()
    mocked_src.bounds.left = -127.9
    mocked_src.bounds.bottom = -127.9
    mocked_src.bounds.right = 127.9
    mocked_src.bounds.top = 127.9
    mocked_src.dtypes = ['uint8', 'uint8', 'uint8']
    mocked_src.crs.to_epsg.return_value = 25832
    mocked_src.res = (.5, .5)
    mocked_src.count = 3
    mocked_rio_open.return_value.__enter__.return_value = mocked_src
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
    vrt_data_fetcher_info_ = vrt_data_fetcher_info(
        path=path,
    )

    assert vrt_data_fetcher_info_ == expected
