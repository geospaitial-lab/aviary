#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import numpy.typing as npt
import pytest

# noinspection PyProtectedMember
from aviary._functional.tile.tile_fetcher import (
    _compute_tile_size_pixels,
    _get_wms_params,
    _permute_data,
)
from aviary.core.bounding_box import BoundingBox
from aviary.core.enums import WMSVersion
from aviary.core.exceptions import AviaryUserError
from aviary.core.type_aliases import (
    BufferSize,
    EPSGCode,
    GroundSamplingDistance,
    TileSize,
)
from tests._functional.tile.data.data_test_tile_fetcher import (
    data_test__compute_tile_size_pixels,
    data_test__compute_tile_size_pixels_exceptions,
    data_test__get_wms_params,
    data_test__permute_data,
)


@pytest.mark.skip(reason='Not implemented')
def test_composite_fetcher() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test_vrt_fetcher() -> None:
    pass


@pytest.mark.skip(reason='Not implemented')
def test_wms_fetcher() -> None:
    pass


@pytest.mark.parametrize(
    (
        'tile_size',
        'buffer_size',
        'ground_sampling_distance',
        'expected',
    ),
    data_test__compute_tile_size_pixels,
)
def test__compute_tile_size_pixels(
    tile_size: TileSize,
    buffer_size: BufferSize,
    ground_sampling_distance: GroundSamplingDistance,
    expected: TileSize,
) -> None:
    tile_size_pixels = _compute_tile_size_pixels(
        tile_size=tile_size,
        buffer_size=buffer_size,
        ground_sampling_distance=ground_sampling_distance,
    )

    assert tile_size_pixels == expected


@pytest.mark.parametrize(
    (
        'tile_size',
        'buffer_size',
        'ground_sampling_distance',
        'message',
    ),
    data_test__compute_tile_size_pixels_exceptions,
)
def test__compute_tile_size_pixels_exceptions(
    tile_size: TileSize,
    buffer_size: BufferSize,
    ground_sampling_distance: GroundSamplingDistance,
    message: str,
) -> None:
    with pytest.raises(AviaryUserError, match=message):
        _ = _compute_tile_size_pixels(
            tile_size=tile_size,
            buffer_size=buffer_size,
            ground_sampling_distance=ground_sampling_distance,
        )


@pytest.mark.parametrize(
    (
        'version',
        'layer',
        'epsg_code',
        'response_format',
        'tile_size_pixels',
        'bounding_box',
        'style',
        'fill_value',
        'expected',
    ),
    data_test__get_wms_params,
)
def test__get_wms_params(
    version: WMSVersion,
    layer: str,
    epsg_code: EPSGCode,
    response_format: str,
    tile_size_pixels: int,
    bounding_box: BoundingBox,
    style: str | None,
    fill_value: str,
    expected: dict[str, str],
) -> None:
    params = _get_wms_params(
        version=version,
        layer=layer,
        epsg_code=epsg_code,
        response_format=response_format,
        tile_size_pixels=tile_size_pixels,
        bounding_box=bounding_box,
        style=style,
        fill_value=fill_value,
    )

    assert params == expected


@pytest.mark.parametrize(('data', 'expected'), data_test__permute_data)
def test__permute_data(
    data: npt.NDArray,
    expected: npt.NDArray,
) -> None:
    data = _permute_data(data=data)

    np.testing.assert_array_equal(data, expected)


@pytest.mark.skip(reason='Not implemented')
def test__request_wms() -> None:
    pass
