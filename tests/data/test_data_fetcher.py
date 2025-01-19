from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import aviary.data.data_fetcher

from aviary.core.enums import (
    InterpolationMode,
    WMSVersion,
)
from aviary.data.data_fetcher import (
    CompositeFetcher,
    DataFetcher,
    VRTFetcher,
    VRTFetcherConfig,
    WMSFetcher,
    WMSFetcherConfig,
)


def test_globals() -> None:
    class_names = [
        'VRTFetcher',
        'WMSFetcher',
    ]

    for class_name in class_names:
        assert hasattr(aviary.data.data_fetcher, class_name)


def test_composite_fetcher_init() -> None:
    data_fetchers = [
        MagicMock(spec=DataFetcher),
        MagicMock(spec=DataFetcher),
        MagicMock(spec=DataFetcher),
    ]
    num_workers = 1
    composite_fetcher = CompositeFetcher(
        data_fetchers=data_fetchers,
        num_workers=num_workers,
    )

    assert composite_fetcher.data_fetchers == data_fetchers
    assert composite_fetcher.num_workers == num_workers


@pytest.mark.skip(reason='Not implemented')
def test_composite_fetcher_from_config() -> None:
    pass


@patch('aviary.data.data_fetcher.composite_fetcher')
def test_composite_fetcher_call(
    mocked_composite_fetcher: MagicMock,
    composite_fetcher: CompositeFetcher,
) -> None:
    x_min = -128
    y_min = -128
    expected = 'expected'
    mocked_composite_fetcher.return_value = expected
    data = composite_fetcher(
        x_min=x_min,
        y_min=y_min,
    )

    mocked_composite_fetcher.assert_called_once_with(
        x_min=x_min,
        y_min=y_min,
        data_fetchers=composite_fetcher.data_fetchers,
        num_workers=composite_fetcher.num_workers,
    )
    assert data == expected


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


def test_wms_fetcher_init() -> None:
    url = 'https://www.test.com'
    version = WMSVersion.V1_3_0
    layer = 'test_layer'
    epsg_code = 25832
    response_format = 'image/png'
    tile_size = 128
    ground_sampling_distance = .2
    style = None
    buffer_size = 0
    drop_channels = None
    wms_fetcher = WMSFetcher(
        url=url,
        version=version,
        layer=layer,
        epsg_code=epsg_code,
        response_format=response_format,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        style=style,
        buffer_size=buffer_size,
        drop_channels=drop_channels,
    )

    assert wms_fetcher.url == url
    assert wms_fetcher.version == version
    assert wms_fetcher.layer == layer
    assert wms_fetcher.epsg_code == epsg_code
    assert wms_fetcher.response_format == response_format
    assert wms_fetcher.tile_size == tile_size
    assert wms_fetcher.ground_sampling_distance == ground_sampling_distance
    assert wms_fetcher.style == style
    assert wms_fetcher.buffer_size == buffer_size
    assert wms_fetcher.drop_channels == drop_channels


def test_wms_fetcher_from_config() -> None:
    url = 'https://www.test.com'
    version = WMSVersion.V1_3_0
    layer = 'test_layer'
    epsg_code = 25832
    response_format = 'image/png'
    tile_size = 128
    ground_sampling_distance = .2
    style = None
    buffer_size = 0
    drop_channels = None
    wms_fetcher_config = WMSFetcherConfig(
        url=url,
        version=version,
        layer=layer,
        epsg_code=epsg_code,
        response_format=response_format,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        style=style,
        buffer_size=buffer_size,
        drop_channels=drop_channels,
    )
    wms_fetcher = WMSFetcher.from_config(wms_fetcher_config)

    assert wms_fetcher.url == url
    assert wms_fetcher.version == version
    assert wms_fetcher.layer == layer
    assert wms_fetcher.epsg_code == epsg_code
    assert wms_fetcher.response_format == response_format
    assert wms_fetcher.tile_size == tile_size
    assert wms_fetcher.ground_sampling_distance == ground_sampling_distance
    assert wms_fetcher.style == style
    assert wms_fetcher.buffer_size == buffer_size
    assert wms_fetcher.drop_channels == drop_channels


@patch('aviary.data.data_fetcher.wms_fetcher')
def test_wms_fetcher_call(
    mocked_wms_fetcher: MagicMock,
    wms_fetcher: WMSFetcher,
) -> None:
    x_min = -128
    y_min = -128
    expected = 'expected'
    mocked_wms_fetcher.return_value = expected
    data = wms_fetcher(
        x_min=x_min,
        y_min=y_min,
    )

    mocked_wms_fetcher.assert_called_once_with(
        x_min=x_min,
        y_min=y_min,
        url=wms_fetcher.url,
        version=wms_fetcher.version,
        layer=wms_fetcher.layer,
        epsg_code=wms_fetcher.epsg_code,
        response_format=wms_fetcher.response_format,
        tile_size=wms_fetcher.tile_size,
        ground_sampling_distance=wms_fetcher.ground_sampling_distance,
        style=wms_fetcher.style,
        buffer_size=wms_fetcher.buffer_size,
        drop_channels=wms_fetcher.drop_channels,
        fill_value=wms_fetcher._FILL_VALUE,
    )
    assert data == expected
