from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import aviary.inference.tile_fetcher
from aviary.core.enums import (
    ChannelType,
    InterpolationMode,
    WMSVersion,
)
from aviary.inference.tile_fetcher import (
    CompositeFetcher,
    TileFetcher,
    VRTFetcher,
    VRTFetcherConfig,
    WMSFetcher,
    WMSFetcherConfig,
)


def test_globals() -> None:
    class_names = [
        'CompositeFetcher',
        'VRTFetcher',
        'WMSFetcher',
    ]

    for class_name in class_names:
        assert hasattr(aviary.inference.tile_fetcher, class_name)


def test_composite_fetcher_init() -> None:
    tile_fetchers = [
        MagicMock(spec=TileFetcher),
        MagicMock(spec=TileFetcher),
        MagicMock(spec=TileFetcher),
    ]
    axis = 'channel'
    num_workers = 1
    composite_fetcher = CompositeFetcher(
        tile_fetchers=tile_fetchers,
        axis=axis,
        num_workers=num_workers,
    )

    assert composite_fetcher._tile_fetchers == tile_fetchers
    assert composite_fetcher._axis == axis
    assert composite_fetcher._num_workers == num_workers


@pytest.mark.skip(reason='Not implemented')
def test_composite_fetcher_from_config() -> None:
    pass


@patch('aviary.inference.tile_fetcher.composite_fetcher')
def test_composite_fetcher_call(
    mocked_composite_fetcher: MagicMock,
    composite_fetcher: CompositeFetcher,
) -> None:
    coordinates = (0, 0)
    expected = 'expected'
    mocked_composite_fetcher.return_value = expected
    tile = composite_fetcher(coordinates=coordinates)

    mocked_composite_fetcher.assert_called_once_with(
        coordinates=coordinates,
        tile_fetchers=composite_fetcher._tile_fetchers,
        axis=composite_fetcher._axis,
        num_workers=composite_fetcher._num_workers,
    )
    assert tile == expected


def test_vrt_fetcher_init() -> None:
    path = Path('test/test.vrt')
    channels = [
        ChannelType.R,
        ChannelType.G,
        ChannelType.B,
        ChannelType.NIR,
        'custom',
    ]
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0
    ignore_channels = None
    vrt_fetcher = VRTFetcher(
        path=path,
        channels=channels,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
        ignore_channels=ignore_channels,
    )

    assert vrt_fetcher._path == path
    assert vrt_fetcher._channels == channels
    assert vrt_fetcher._tile_size == tile_size
    assert vrt_fetcher._ground_sampling_distance == ground_sampling_distance
    assert vrt_fetcher._interpolation_mode == interpolation_mode
    assert vrt_fetcher._buffer_size == buffer_size
    assert vrt_fetcher._ignore_channels == ignore_channels


def test_vrt_fetcher_from_config() -> None:
    path = Path('test/test.vrt')
    channels = [
        ChannelType.R,
        ChannelType.G,
        ChannelType.B,
        ChannelType.NIR,
        'custom',
    ]
    tile_size = 128
    ground_sampling_distance = .2
    interpolation_mode = InterpolationMode.BILINEAR
    buffer_size = 0
    ignore_channels = None
    vrt_fetcher_config = VRTFetcherConfig(
        path=path,
        channels=channels,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
        ignore_channels=ignore_channels,
    )
    vrt_fetcher = VRTFetcher.from_config(vrt_fetcher_config)

    assert vrt_fetcher._path == path
    assert vrt_fetcher._channels == channels
    assert vrt_fetcher._tile_size == tile_size
    assert vrt_fetcher._ground_sampling_distance == ground_sampling_distance
    assert vrt_fetcher._interpolation_mode == interpolation_mode
    assert vrt_fetcher._buffer_size == buffer_size
    assert vrt_fetcher._ignore_channels == ignore_channels


@patch('aviary.inference.tile_fetcher.vrt_fetcher')
def test_vrt_fetcher_call(
    mocked_vrt_fetcher: MagicMock,
    vrt_fetcher: VRTFetcher,
) -> None:
    coordinates = (0, 0)
    expected = 'expected'
    mocked_vrt_fetcher.return_value = expected
    tile = vrt_fetcher(coordinates=coordinates)

    mocked_vrt_fetcher.assert_called_once_with(
        coordinates=coordinates,
        path=vrt_fetcher._path,
        channels=vrt_fetcher._channels,
        tile_size=vrt_fetcher._tile_size,
        ground_sampling_distance=vrt_fetcher._ground_sampling_distance,
        interpolation_mode=vrt_fetcher._interpolation_mode,
        buffer_size=vrt_fetcher._buffer_size,
        ignore_channels=vrt_fetcher._ignore_channels,
        fill_value=vrt_fetcher._FILL_VALUE,
    )
    assert tile == expected


def test_wms_fetcher_init() -> None:
    url = 'https://www.test.com'
    version = WMSVersion.V1_3_0
    layer = 'test_layer'
    epsg_code = 25832
    response_format = 'image/png'
    channels = [
        ChannelType.R,
        ChannelType.G,
        ChannelType.B,
    ]
    tile_size = 128
    ground_sampling_distance = .2
    style = None
    buffer_size = 0
    ignore_channels = None
    wms_fetcher = WMSFetcher(
        url=url,
        version=version,
        layer=layer,
        epsg_code=epsg_code,
        response_format=response_format,
        channels=channels,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        style=style,
        buffer_size=buffer_size,
        ignore_channels=ignore_channels,
    )

    assert wms_fetcher._url == url
    assert wms_fetcher._version == version
    assert wms_fetcher._layer == layer
    assert wms_fetcher._epsg_code == epsg_code
    assert wms_fetcher._response_format == response_format
    assert wms_fetcher._channels == channels
    assert wms_fetcher._tile_size == tile_size
    assert wms_fetcher._ground_sampling_distance == ground_sampling_distance
    assert wms_fetcher._style == style
    assert wms_fetcher._buffer_size == buffer_size
    assert wms_fetcher._ignore_channels == ignore_channels


def test_wms_fetcher_from_config() -> None:
    url = 'https://www.test.com'
    version = WMSVersion.V1_3_0
    layer = 'test_layer'
    epsg_code = 25832
    response_format = 'image/png'
    channels = [
        ChannelType.R,
        ChannelType.G,
        ChannelType.B,
    ]
    tile_size = 128
    ground_sampling_distance = .2
    style = None
    buffer_size = 0
    ignore_channels = None
    wms_fetcher_config = WMSFetcherConfig(
        url=url,
        version=version,
        layer=layer,
        epsg_code=epsg_code,
        response_format=response_format,
        channels=channels,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        style=style,
        buffer_size=buffer_size,
        ignore_channels=ignore_channels,
    )
    wms_fetcher = WMSFetcher.from_config(wms_fetcher_config)

    assert wms_fetcher._url == url
    assert wms_fetcher._version == version
    assert wms_fetcher._layer == layer
    assert wms_fetcher._epsg_code == epsg_code
    assert wms_fetcher._response_format == response_format
    assert wms_fetcher._channels == channels
    assert wms_fetcher._tile_size == tile_size
    assert wms_fetcher._ground_sampling_distance == ground_sampling_distance
    assert wms_fetcher._style == style
    assert wms_fetcher._buffer_size == buffer_size
    assert wms_fetcher._ignore_channels == ignore_channels


@patch('aviary.inference.tile_fetcher.wms_fetcher')
def test_wms_fetcher_call(
    mocked_wms_fetcher: MagicMock,
    wms_fetcher: WMSFetcher,
) -> None:
    coordinates = (0, 0)
    expected = 'expected'
    mocked_wms_fetcher.return_value = expected
    tile = wms_fetcher(coordinates=coordinates)

    mocked_wms_fetcher.assert_called_once_with(
        coordinates=coordinates,
        url=wms_fetcher._url,
        version=wms_fetcher._version,
        layer=wms_fetcher._layer,
        epsg_code=wms_fetcher._epsg_code,
        response_format=wms_fetcher._response_format,
        channels=wms_fetcher._channels,
        tile_size=wms_fetcher._tile_size,
        ground_sampling_distance=wms_fetcher._ground_sampling_distance,
        style=wms_fetcher._style,
        buffer_size=wms_fetcher._buffer_size,
        ignore_channels=wms_fetcher._ignore_channels,
        fill_value=wms_fetcher._FILL_VALUE,
    )
    assert tile == expected
