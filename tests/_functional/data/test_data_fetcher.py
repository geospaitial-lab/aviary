import numpy as np
import numpy.typing as npt
import pytest

# noinspection PyProtectedMember
from aviary._functional.data.data_fetcher import (
    _compute_tile_size_pixels,
    _drop_channels,
    _permute_data,
)

# noinspection PyProtectedMember
from aviary._utils.types import (
    BufferSize,
    GroundSamplingDistance,
    TileSize,
)
from tests._functional.data.data.data_test_data_fetcher import (
    data_test__compute_tile_size_pixels,
    data_test__drop_channels,
    data_test__permute_data,
)


@pytest.mark.skip(reason='Not implemented')
def test_vrt_fetcher() -> None:
    pass


@pytest.mark.parametrize(
    ('tile_size', 'buffer_size', 'ground_sampling_distance', 'expected'),
    data_test__compute_tile_size_pixels,
)
def test__compute_tile_size_pixels(
    tile_size: TileSize,
    buffer_size: BufferSize,
    ground_sampling_distance: GroundSamplingDistance,
    expected: int,
) -> None:
    tile_size_pixels = _compute_tile_size_pixels(
        tile_size=tile_size,
        buffer_size=buffer_size,
        ground_sampling_distance=ground_sampling_distance,
    )

    assert tile_size_pixels == expected


@pytest.mark.parametrize(('data', 'drop_channels', 'expected'), data_test__drop_channels)
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


@pytest.mark.parametrize(('data', 'expected'), data_test__permute_data)
def test__permute_data(
    data: npt.NDArray,
    expected: npt.NDArray,
) -> None:
    data = _permute_data(
        data=data,
    )

    np.testing.assert_array_equal(data, expected)
