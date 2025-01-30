import numpy as np
import pytest

from aviary.core.bounding_box import BoundingBox
from aviary.core.enums import ChannelType
from aviary.core.tile import Tile


def test_tile_init(
    tile_data: dict[ChannelType | str, np.ndarray],
) -> None:
    data = tile_data
    coordinates = (0, 0)
    tile_size = 128
    buffer_size = 16
    tile = Tile(
        data=data,
        coordinates=coordinates,
        tile_size=tile_size,
        buffer_size=buffer_size,
    )

    assert tile.data == data
    assert tile.coordinates == coordinates
    assert tile.tile_size == tile_size
    assert tile.buffer_size == buffer_size


def test_tile_setters(
    tile: Tile,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tile.data = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tile.coordinates = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tile.tile_size = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tile.buffer_size = None


def test_tile_area(
    tile: Tile,
) -> None:
    expected = 25600

    assert tile.area == expected


def test_tile_bounding_box(
    tile: Tile,
) -> None:
    expected = BoundingBox(
        x_min=-16,
        y_min=-16,
        x_max=144,
        y_max=144,
    )

    assert tile.bounding_box == expected


def test_tile_channels(
    tile: Tile,
) -> None:
    expected = [
        ChannelType.R,
        ChannelType.G,
        ChannelType.B,
        ChannelType.NIR,
        'custom',
    ]
    expected = set(expected)

    assert tile.channels == expected


def test_tile_ground_sampling_distance(
    tile: Tile,
) -> None:
    expected = .2

    assert tile.ground_sampling_distance == expected


def test_tile_num_channels(
    tile: Tile,
) -> None:
    expected = 5

    assert tile.num_channels == expected


def test_tile_num_time_steps(
    tile: Tile,
) -> None:
    expected = 2

    assert tile.num_time_steps == expected


def test_tile_shape(
    tile: Tile,
) -> None:
    expected = (800, 800, 2)

    assert tile.shape == expected
