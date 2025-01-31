import numpy as np
import numpy.typing as npt
import pytest

from aviary.core.bounding_box import BoundingBox
from aviary.core.enums import ChannelName
from aviary.core.process_area import ProcessArea
from aviary.core.tile import Tile


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
def tile(
    tile_data: dict[ChannelName | str, npt.NDArray],
) -> Tile:
    data = tile_data
    coordinates = (0, 0)
    tile_size = 128
    buffer_size = 16
    return Tile(
        data=data,
        coordinates=coordinates,
        tile_size=tile_size,
        buffer_size=buffer_size,
    )


@pytest.fixture(scope='function')
def tile_data() -> dict[ChannelName | str, npt.NDArray]:
    data_r = np.full(
        shape=(800, 800, 2),
        fill_value=0,
        dtype=np.uint8,
    )
    data_g = np.full(
        shape=(800, 800, 2),
        fill_value=1,
        dtype=np.uint8,
    )
    data_b = np.full(
        shape=(800, 800, 2),
        fill_value=2,
        dtype=np.uint8,
    )
    data_nir = np.full(
        shape=(800, 800, 2),
        fill_value=3,
        dtype=np.uint8,
    )
    data_custom = np.full(
        shape=(800, 800, 2),
        fill_value=4,
        dtype=np.uint8,
    )
    return {
        ChannelName.R: data_r,
        ChannelName.G: data_g,
        ChannelName.B: data_b,
        ChannelName.NIR: data_nir,
        'custom': data_custom,
    }
