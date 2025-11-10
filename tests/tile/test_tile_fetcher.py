#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and / or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aviary.core.enums import (
    ChannelName,
    InterpolationMode,
    WMSVersion,
)
from aviary.tile.tile_fetcher import (
    CompositeFetcher,
    TileFetcher,
    VRTFetcher,
    VRTFetcherConfig,
    WMSFetcher,
    WMSFetcherConfig,
)


def test_composite_fetcher_init() -> None:
    tile_fetchers = [
        MagicMock(spec=TileFetcher),
        MagicMock(spec=TileFetcher),
        MagicMock(spec=TileFetcher),
    ]
    max_num_threads = None

    composite_fetcher = CompositeFetcher(
        tile_fetchers=tile_fetchers,
        max_num_threads=max_num_threads,
    )

    assert composite_fetcher._tile_fetchers == tile_fetchers
    assert composite_fetcher._max_num_threads == max_num_threads


def test_composite_fetcher_init_defaults() -> None:
    signature = inspect.signature(CompositeFetcher)
    max_num_threads = signature.parameters['max_num_threads'].default

    expected_max_num_threads = None

    assert max_num_threads == expected_max_num_threads


@pytest.mark.skip(reason='Not implemented')
def test_composite_fetcher_from_config() -> None:
    pass


@patch('aviary.tile.tile_fetcher.composite_fetcher')
def test_composite_fetcher_call(
    mocked_composite_fetcher: MagicMock,
    composite_fetcher: CompositeFetcher,
) -> None:
    coordinates = (0, 0)

    expected = 'expected'
    mocked_composite_fetcher.return_value = expected

    tile = composite_fetcher(coordinates=coordinates)

    assert tile == expected
    mocked_composite_fetcher.assert_called_once_with(
        coordinates=coordinates,
        tile_fetchers=composite_fetcher._tile_fetchers,
        max_num_threads=composite_fetcher._max_num_threads,
    )


def test_vrt_fetcher_init() -> None:
    path = Path('test/test.vrt')
    epsg_code = 25832
    channel_names = [
        ChannelName.R,
        ChannelName.G,
        ChannelName.B,
        ChannelName.NIR,
        'custom',
    ]
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0

    vrt_fetcher = VRTFetcher(
        path=path,
        epsg_code=epsg_code,
        channel_names=channel_names,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
    )

    assert vrt_fetcher._path == path
    assert vrt_fetcher._epsg_code == epsg_code
    assert vrt_fetcher._channel_names == channel_names
    assert vrt_fetcher._tile_size == tile_size
    assert vrt_fetcher._ground_sampling_distance == ground_sampling_distance
    assert vrt_fetcher._interpolation_mode == interpolation_mode
    assert vrt_fetcher._buffer_size == buffer_size


def test_vrt_fetcher_init_defaults() -> None:
    signature = inspect.signature(VRTFetcher)
    interpolation_mode = signature.parameters['interpolation_mode'].default
    buffer_size = signature.parameters['buffer_size'].default

    expected_interpolation_mode = InterpolationMode.BILINEAR
    expected_buffer_size = 0

    assert interpolation_mode == expected_interpolation_mode
    assert buffer_size == expected_buffer_size


def test_vrt_fetcher_from_config() -> None:
    path = Path('test/test.vrt')
    epsg_code = 25832
    channel_names = [
        ChannelName.R,
        ChannelName.G,
        ChannelName.B,
        ChannelName.NIR,
        'custom',
    ]
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0
    vrt_fetcher_config = VRTFetcherConfig(
        path=path,
        epsg_code=epsg_code,
        channel_names=channel_names,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
    )

    vrt_fetcher = VRTFetcher.from_config(vrt_fetcher_config)

    assert vrt_fetcher._path == path
    assert vrt_fetcher._epsg_code == epsg_code
    assert vrt_fetcher._channel_names == channel_names
    assert vrt_fetcher._tile_size == tile_size
    assert vrt_fetcher._ground_sampling_distance == ground_sampling_distance
    assert vrt_fetcher._interpolation_mode == interpolation_mode
    assert vrt_fetcher._buffer_size == buffer_size


@patch('aviary.tile.tile_fetcher.vrt_fetcher')
def test_vrt_fetcher_call(
    mocked_vrt_fetcher: MagicMock,
    vrt_fetcher: VRTFetcher,
) -> None:
    coordinates = (0, 0)

    expected = 'expected'
    mocked_vrt_fetcher.return_value = expected

    tile = vrt_fetcher(coordinates=coordinates)

    assert tile == expected
    mocked_vrt_fetcher.assert_called_once_with(
        coordinates=coordinates,
        path=vrt_fetcher._path,
        epsg_code=vrt_fetcher._epsg_code,
        channel_names=vrt_fetcher._channel_names,
        tile_size=vrt_fetcher._tile_size,
        ground_sampling_distance=vrt_fetcher._ground_sampling_distance,
        interpolation_mode=vrt_fetcher._interpolation_mode,
        buffer_size=vrt_fetcher._buffer_size,
        fill_value=vrt_fetcher._FILL_VALUE,
    )


def test_wms_fetcher_init() -> None:
    url = 'https://www.test.com'
    version = WMSVersion.V1_3_0
    layer = 'test_layer'
    epsg_code = 25832
    response_format = 'image/png'
    channel_names = [
        ChannelName.R,
        ChannelName.G,
        ChannelName.B,
    ]
    tile_size = 128
    ground_sampling_distance = .2
    style = None
    buffer_size = 0

    wms_fetcher = WMSFetcher(
        url=url,
        version=version,
        layer=layer,
        epsg_code=epsg_code,
        response_format=response_format,
        channel_names=channel_names,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        style=style,
        buffer_size=buffer_size,
    )

    assert wms_fetcher._url == url
    assert wms_fetcher._version == version
    assert wms_fetcher._layer == layer
    assert wms_fetcher._epsg_code == epsg_code
    assert wms_fetcher._response_format == response_format
    assert wms_fetcher._channel_names == channel_names
    assert wms_fetcher._tile_size == tile_size
    assert wms_fetcher._ground_sampling_distance == ground_sampling_distance
    assert wms_fetcher._style == style
    assert wms_fetcher._buffer_size == buffer_size


def test_wms_fetcher_init_defaults() -> None:
    signature = inspect.signature(WMSFetcher)
    style = signature.parameters['style'].default
    buffer_size = signature.parameters['buffer_size'].default

    expected_style = None
    expected_buffer_size = 0

    assert style is expected_style
    assert buffer_size == expected_buffer_size


def test_wms_fetcher_from_config() -> None:
    url = 'https://www.test.com'
    version = WMSVersion.V1_3_0
    layer = 'test_layer'
    epsg_code = 25832
    response_format = 'image/png'
    channel_names = [
        ChannelName.R,
        ChannelName.G,
        ChannelName.B,
    ]
    tile_size = 128
    ground_sampling_distance = .2
    style = None
    buffer_size = 0
    wms_fetcher_config = WMSFetcherConfig(
        url=url,
        version=version,
        layer=layer,
        epsg_code=epsg_code,
        response_format=response_format,
        channel_names=channel_names,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        style=style,
        buffer_size=buffer_size,
    )

    wms_fetcher = WMSFetcher.from_config(wms_fetcher_config)

    assert wms_fetcher._url == url
    assert wms_fetcher._version == version
    assert wms_fetcher._layer == layer
    assert wms_fetcher._epsg_code == epsg_code
    assert wms_fetcher._response_format == response_format
    assert wms_fetcher._channel_names == channel_names
    assert wms_fetcher._tile_size == tile_size
    assert wms_fetcher._ground_sampling_distance == ground_sampling_distance
    assert wms_fetcher._style == style
    assert wms_fetcher._buffer_size == buffer_size


@patch('aviary.tile.tile_fetcher.wms_fetcher')
def test_wms_fetcher_call(
    mocked_wms_fetcher: MagicMock,
    wms_fetcher: WMSFetcher,
) -> None:
    coordinates = (0, 0)

    expected = 'expected'
    mocked_wms_fetcher.return_value = expected

    tile = wms_fetcher(coordinates=coordinates)

    assert tile == expected
    mocked_wms_fetcher.assert_called_once_with(
        coordinates=coordinates,
        url=wms_fetcher._url,
        version=wms_fetcher._version,
        layer=wms_fetcher._layer,
        epsg_code=wms_fetcher._epsg_code,
        response_format=wms_fetcher._response_format,
        channel_names=wms_fetcher._channel_names,
        tile_size=wms_fetcher._tile_size,
        ground_sampling_distance=wms_fetcher._ground_sampling_distance,
        style=wms_fetcher._style,
        buffer_size=wms_fetcher._buffer_size,
        fill_value=wms_fetcher._FILL_VALUE,
    )
