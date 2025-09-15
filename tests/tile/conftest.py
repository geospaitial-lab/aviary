from pathlib import Path
from unittest.mock import MagicMock

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
    WMSFetcher,
)


@pytest.fixture(scope='session')
def composite_fetcher() -> CompositeFetcher:
    tile_fetchers = [
        MagicMock(spec=TileFetcher),
        MagicMock(spec=TileFetcher),
        MagicMock(spec=TileFetcher),
    ]
    max_num_threads = None
    return CompositeFetcher(
        tile_fetchers=tile_fetchers,
        max_num_threads=max_num_threads,
    )


@pytest.fixture(scope='session')
def vrt_fetcher() -> VRTFetcher:
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
    return VRTFetcher(
        path=path,
        epsg_code=epsg_code,
        channel_names=channel_names,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
    )


@pytest.fixture(scope='session')
def wms_fetcher() -> WMSFetcher:
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
    return WMSFetcher(
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
