import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pytest
from shapely.geometry import box

from aviary.core.bounding_box import BoundingBox
from aviary.core.channel import (
    Channel,
    RasterChannel,
    VectorChannel,
)
from aviary.core.enums import ChannelName
from aviary.core.grid import Grid
from aviary.core.tiles import Tiles
from aviary.core.type_aliases import CoordinatesSet
from aviary.core.vector import Vector
from aviary.core.vector_layer import VectorLayer


@pytest.fixture(scope='function')
def bounding_box() -> BoundingBox:
    return get_bounding_box()


def get_bounding_box() -> BoundingBox:
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
def grid() -> Grid:
    return get_grid()


def get_grid() -> Grid:
    coordinates = get_grid_coordinates()
    tile_size = 128
    return Grid(
        coordinates=coordinates,
        tile_size=tile_size,
    )


@pytest.fixture(scope='function')
def grid_coordinates() -> CoordinatesSet:
    return get_grid_coordinates()


def get_grid_coordinates() -> CoordinatesSet:
    return np.array(
        [[-128, -128], [0, -128], [-128, 0], [0, 0]],
        dtype=np.int32,
    )


@pytest.fixture(scope='function')
def metadata() -> dict[str, object]:
    return get_metadata()


def get_metadata() -> dict[str, object]:
    return {
        'test_key_1': 'test_value_1',
        'test_key_2': 'test_value_2',
        'test_key_3': 'test_value_3',
    }


@pytest.fixture(scope='function')
def raster_channel() -> RasterChannel:
    return get_raster_channel()


def get_raster_channel() -> RasterChannel:
    data = get_raster_channel_data()
    name = ChannelName.R
    buffer_size = 0.
    metadata = None
    copy = False
    return RasterChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def raster_channel_data() -> list[npt.NDArray]:
    return get_raster_channel_data()


def get_raster_channel_data() -> list[npt.NDArray]:
    return [
        get_raster_channel_data_item(),
        get_raster_channel_data_item(),
    ]


@pytest.fixture(scope='function')
def raster_channel_data_item() -> npt.NDArray:
    return get_raster_channel_data_item()


def get_raster_channel_data_item() -> npt.NDArray:
    return np.ones(
        shape=(640, 640),
        dtype=np.uint8,
    )


def get_raster_channel_buffered_data_item() -> npt.NDArray:
    data = np.zeros(
        shape=(960, 960),
        dtype=np.uint8,
    )
    data[160:800, 160:800] = 1
    return data


@pytest.fixture(scope='function')
def tiles() -> Tiles:
    return get_tiles()


def get_tiles() -> Tiles:
    channels = get_tiles_channels()
    coordinates = get_tiles_coordinates()
    tile_size = 128
    metadata = None
    copy = False
    return Tiles(
        channels=channels,
        coordinates=coordinates,
        tile_size=tile_size,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def tiles_channels() -> list[Channel]:
    return get_tiles_channels()


def get_tiles_channels() -> list[Channel]:
    return [
        get_tiles_channel_1(),
        get_tiles_channel_2(),
        get_tiles_channel_3(),
        get_tiles_channel_4(),
    ]


@pytest.fixture(scope='function')
def tiles_channel_1() -> RasterChannel:
    return get_tiles_channel_1()


def get_tiles_channel_1() -> RasterChannel:
    data = get_raster_channel_data()
    name = ChannelName.R
    buffer_size = 0.
    metadata = None
    copy = False
    return RasterChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def tiles_channel_2() -> RasterChannel:
    return get_tiles_channel_2()


def get_tiles_channel_2() -> RasterChannel:
    data = get_raster_channel_data()
    name = ChannelName.G
    buffer_size = 0.
    metadata = None
    copy = False
    return RasterChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def tiles_channel_3() -> RasterChannel:
    return get_tiles_channel_3()


def get_tiles_channel_3() -> RasterChannel:
    data = get_raster_channel_data()
    name = ChannelName.B
    buffer_size = 0.
    metadata = None
    copy = False
    return RasterChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def tiles_channel_4() -> VectorChannel:
    return get_tiles_channel_4()


def get_tiles_channel_4() -> VectorChannel:
    data = get_vector_channel_data()
    name = 'custom'
    buffer_size = 0.
    metadata = None
    copy = False
    return VectorChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def tiles_coordinates() -> CoordinatesSet:
    return get_tiles_coordinates()


def get_tiles_coordinates() -> CoordinatesSet:
    return np.array(
        [[128, -128], [128, 0]],
        dtype=np.int32,
    )


@pytest.fixture(scope='function')
def vector() -> Vector:
    return get_vector()


def get_vector() -> Vector:
    layers = get_vector_layers()
    metadata = None
    copy = False
    return Vector(
        layers=layers,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def vector_layers() -> list[VectorLayer]:
    return get_vector_layers()


def get_vector_layers() -> list[VectorLayer]:
    return [
        get_vector_layer_1(),
        get_vector_layer_2(),
    ]


@pytest.fixture(scope='function')
def vector_layer_1() -> VectorLayer:
    return get_vector_layer_1()


def get_vector_layer_1() -> VectorLayer:
    data = get_vector_layer_data()
    name = 'custom_1'
    metadata = None
    copy = False
    return VectorLayer(
        data=data,
        name=name,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def vector_layer_2() -> VectorLayer:
    return get_vector_layer_2()


def get_vector_layer_2() -> VectorLayer:
    data = get_vector_layer_data()
    name = 'custom_2'
    metadata = None
    copy = False
    return VectorLayer(
        data=data,
        name=name,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def vector_channel() -> VectorChannel:
    return get_vector_channel()


def get_vector_channel() -> VectorChannel:
    data = get_vector_channel_data()
    name = ChannelName.R
    buffer_size = 0.
    metadata = None
    copy = False
    return VectorChannel(
        data=data,
        name=name,
        buffer_size=buffer_size,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def vector_channel_data() -> list[gpd.GeoDataFrame]:
    return get_vector_channel_data()


def get_vector_channel_data() -> list[gpd.GeoDataFrame]:
    return [
        get_vector_channel_data_item(),
        get_vector_channel_data_item(),
    ]


@pytest.fixture(scope='function')
def vector_channel_data_item() -> gpd.GeoDataFrame:
    return get_vector_channel_data_item()


def get_vector_channel_data_item() -> gpd.GeoDataFrame:
    geometries = [
        box(.425, .425, .575, .575),
    ]
    return gpd.GeoDataFrame(geometry=geometries)


def get_vector_channel_buffered_data_item() -> gpd.GeoDataFrame:
    geometries = [
        box(0., 0., .1, .1),
        box(.9, 0., 1., .1),
        box(.9, .9, 1., 1.),
        box(0., .9, .1, 1.),
        box(.45, .45, .55, .55),
    ]
    return gpd.GeoDataFrame(geometry=geometries)


def get_vector_channel_empty_data_item() -> gpd.GeoDataFrame:
    geometries = []
    return gpd.GeoDataFrame(geometry=geometries)


@pytest.fixture(scope='function')
def vector_layer() -> VectorLayer:
    return get_vector_layer()


def get_vector_layer() -> VectorLayer:
    data = get_vector_layer_data()
    name = 'custom'
    metadata = None
    copy = False
    return VectorLayer(
        data=data,
        name=name,
        metadata=metadata,
        copy=copy,
    )


@pytest.fixture(scope='function')
def vector_layer_data() -> gpd.GeoDataFrame:
    return get_vector_layer_data()


def get_vector_layer_data() -> gpd.GeoDataFrame:
    geometries = [
        box(-128, -128, 0, 0),
        box(0, -128, 128, 0),
        box(-128, 0, 0, 128),
        box(0, 0, 128, 128),
    ]
    return gpd.GeoDataFrame(geometry=geometries)
