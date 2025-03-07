from pathlib import Path
from unittest.mock import MagicMock

import pytest

from aviary.core.enums import (
    ChannelName,
    InterpolationMode,
    WMSVersion,
)
from aviary.inference.aviary import (
    Aviary,
    Channels,
    ModelCard,
    Type,
)
from aviary.inference.exporter import SegmentationExporter
from aviary.inference.tile_fetcher import (
    CompositeFetcher,
    TileFetcher,
    VRTFetcher,
    WMSFetcher,
)


@pytest.fixture(scope='session')
def aviary(
    model_card: ModelCard,
) -> Aviary:
    model_cards = [model_card] * 3
    return Aviary(
        model_cards=model_cards,
    )


@pytest.fixture(scope='session')
def composite_fetcher() -> CompositeFetcher:
    tile_fetchers = [
        MagicMock(spec=TileFetcher),
        MagicMock(spec=TileFetcher),
        MagicMock(spec=TileFetcher),
    ]
    num_workers = 1
    return CompositeFetcher(
        tile_fetchers=tile_fetchers,
        num_workers=num_workers,
    )


@pytest.fixture(scope='session')
def model_card() -> ModelCard:
    name = 'name'
    repo = 'repo'
    path = 'path'
    type_ = Type.SEGMENTATION
    required_channels = [Channels.RGB, Channels.NIR]
    num_channels = 4
    ground_sampling_distance = .2
    num_classes = 3
    description = 'description'
    return ModelCard(
        name=name,
        repo=repo,
        path=path,
        type=type_,
        required_channels=required_channels,
        num_channels=num_channels,
        ground_sampling_distance=ground_sampling_distance,
        num_classes=num_classes,
        description=description,
    )


@pytest.fixture(scope='session')
def segmentation_exporter() -> SegmentationExporter:
    path = Path('test')
    tile_size = 128
    ground_sampling_distance = .2
    epsg_code = 25832
    field_name = 'class'
    num_workers = 4
    return SegmentationExporter(
        path=path,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        epsg_code=epsg_code,
        field_name=field_name,
        num_workers=num_workers,
    )


@pytest.fixture(scope='session')
def vrt_fetcher() -> VRTFetcher:
    path = Path('test/test.vrt')
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
    time_step = None
    return VRTFetcher(
        path=path,
        channel_names=channel_names,
        tile_size=tile_size,
        ground_sampling_distance=ground_sampling_distance,
        interpolation_mode=interpolation_mode,
        buffer_size=buffer_size,
        time_step=time_step,
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
    time_step = None
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
        time_step=time_step,
    )
