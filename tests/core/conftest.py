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
