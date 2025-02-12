import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pytest
from shapely.geometry import box

from aviary.core.bounding_box import BoundingBox
from aviary.core.channel import (
    RasterChannel,
    VectorChannel,
)
from aviary.core.enums import ChannelName
from aviary.core.process_area import ProcessArea
from aviary.core.tile import Tile
from aviary.core.type_aliases import Channels


@pytest.fixture(scope='function')
def bounding_box() -> BoundingBox:
    x_min = -128
    y_min = -64
    x_max = 128
    y_max = 192
    return BoundingBox(
        x_min=x_min,
        y_min=y_min,
        x_max=x_max,
        y_max=y_max,
    )


@pytest.fixture(scope='function')
def process_area() -> ProcessArea:
    coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)
    tile_size = 128
    return ProcessArea(
        coordinates=coordinates,
        tile_size=tile_size,
    )


@pytest.fixture(scope='function')
def raster_channel(
    raster_channel_data: npt.NDArray,
) -> RasterChannel:
    name = ChannelName.R
    buffer_size = 0.
    time_step = None
    copy = False
    return RasterChannel(
        data=raster_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )


@pytest.fixture(scope='function')
def raster_channel_data() -> npt.NDArray:
    return np.ones(
        shape=(640, 640),
        dtype=np.uint8,
    )


@pytest.fixture(scope='function')
def tile(
    tile_channels: Channels,
) -> Tile:
    coordinates = (0, 0)
    tile_size = 128
    copy = False
    return Tile(
        channels=tile_channels,
        coordinates=coordinates,
        tile_size=tile_size,
        copy=copy,
    )


@pytest.fixture(scope='function')
def tile_channels(
    tile_channel_1: RasterChannel,
    tile_channel_2: RasterChannel,
    tile_channel_3: RasterChannel,
    tile_channel_4: VectorChannel,
) -> Channels:
    return [
        tile_channel_1,
        tile_channel_2,
        tile_channel_3,
        tile_channel_4,
    ]


@pytest.fixture(scope='function')
def tile_channel_1(
    raster_channel_data: npt.NDArray,
) -> RasterChannel:
    name = ChannelName.R
    buffer_size = 0.
    time_step = None
    copy = False
    return RasterChannel(
        data=raster_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )


@pytest.fixture(scope='function')
def tile_channel_2(
    raster_channel_data: npt.NDArray,
) -> RasterChannel:
    name = ChannelName.G
    buffer_size = 0.
    time_step = None
    copy = False
    return RasterChannel(
        data=raster_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )


@pytest.fixture(scope='function')
def tile_channel_3(
    raster_channel_data: npt.NDArray,
) -> RasterChannel:
    name = ChannelName.B
    buffer_size = 0.
    time_step = None
    copy = False
    return RasterChannel(
        data=raster_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )


@pytest.fixture(scope='function')
def tile_channel_4(
    vector_channel_data: gpd.GeoDataFrame,
) -> VectorChannel:
    name = 'custom'
    buffer_size = 0.
    time_step = None
    copy = False
    return VectorChannel(
        data=vector_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )


@pytest.fixture(scope='function')
def vector_channel(
    vector_channel_data: gpd.GeoDataFrame,
) -> VectorChannel:
    name = ChannelName.R
    buffer_size = 0.
    time_step = None
    copy = False
    return VectorChannel(
        data=vector_channel_data,
        name=name,
        buffer_size=buffer_size,
        time_step=time_step,
        copy=copy,
    )


@pytest.fixture(scope='function')
def vector_channel_data() -> gpd.GeoDataFrame:
    geometries = [
        box(0., 0., .1, .1),
        box(.9, 0., 1., .1),
        box(.9, .9, 1., 1.),
        box(0., .9, .1, 1.),
        box(.45, .45, .55, .55),
    ]
    return gpd.GeoDataFrame(geometry=geometries)
