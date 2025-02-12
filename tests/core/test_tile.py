import inspect
import pickle

import pytest

from aviary.core.bounding_box import BoundingBox
from aviary.core.channel import Channel
from aviary.core.enums import ChannelName
from aviary.core.tile import Tile
from aviary.core.type_aliases import (
    ChannelKey,
    Channels,
)
from tests.core.data.data_test_tile import (
    data_test_tile_contains,
    data_test_tile_getattr,
    data_test_tile_getitem,
)


def test_tile_init(
    tile_channels: Channels,
) -> None:
    coordinates = (0, 0)
    tile_size = 128
    copy = False

    tile = Tile(
        channels=tile_channels,
        coordinates=coordinates,
        tile_size=tile_size,
        copy=copy,
    )

    assert tile.channels == tile_channels
    assert tile.coordinates == coordinates
    assert tile.tile_size == tile_size
    assert tile.is_copied == copy


def test_tile_init_defaults() -> None:
    signature = inspect.signature(Tile)
    copy = signature.parameters['copy'].default
    expected_copy = False

    assert copy is expected_copy


def test_tile_mutability_no_copy(
    tile_channels: Channels,
) -> None:
    coordinates = (0, 0)
    tile_size = 128
    copy = False

    tile = Tile(
        channels=tile_channels,
        coordinates=coordinates,
        tile_size=tile_size,
        copy=copy,
    )

    assert id(tile._channels) == id(tile_channels)
    assert id(tile.channels) == id(tile._channels)


def test_tile_mutability_copy(
    tile_channels: Channels,
) -> None:
    coordinates = (0, 0)
    tile_size = 128
    copy = True

    tile = Tile(
        channels=tile_channels,
        coordinates=coordinates,
        tile_size=tile_size,
        copy=copy,
    )

    assert id(tile._channels) != id(tile_channels)
    assert id(tile.channels) == id(tile._channels)


def test_tile_setters(
    tile: Tile,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tile.channels = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tile.coordinates = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tile.tile_size = None


def test_tile_serializability(
    tile: Tile,
) -> None:
    serialized_tile = pickle.dumps(tile)
    deserialized_tile_tile = pickle.loads(serialized_tile)  # noqa: S301

    assert tile == deserialized_tile_tile


def test_tile_area(
    tile: Tile,
) -> None:
    expected = 16384

    assert tile.area == expected


def test_tile_bounding_box(
    tile: Tile,
) -> None:
    expected_x_min = 0
    expected_y_min = 0
    expected_x_max = 128
    expected_y_max = 128
    expected = BoundingBox(
        x_min=expected_x_min,
        y_min=expected_y_min,
        x_max=expected_x_max,
        y_max=expected_y_max,
    )

    assert tile.bounding_box == expected


def test_tile_channel_keys(
    tile: Tile,
) -> None:
    expected = {
        (ChannelName.R, None),
        (ChannelName.G, None),
        (ChannelName.B, None),
        ('custom', None),
    }

    assert tile.channel_keys == expected


def test_tile_channel_names(
    tile: Tile,
) -> None:
    expected = {
        ChannelName.R,
        ChannelName.G,
        ChannelName.B,
        'custom',
    }

    assert tile.channel_names == expected


def test_tile_num_channels(
    tile: Tile,
) -> None:
    expected = 4

    assert tile.num_channels == expected


def test_tile_len(
    tile: Tile,
) -> None:
    expected = 4

    assert len(tile) == expected


@pytest.mark.parametrize(('channel_key', 'expected'), data_test_tile_contains)
def test_tile_contains(
    channel_key: ChannelName | str | ChannelKey,
    expected: bool,
    tile: Tile,
) -> None:
    contains = channel_key in tile

    assert contains is expected


@pytest.mark.parametrize(('channel_name', 'expected'), data_test_tile_getattr)
def test_tile_getattr(
    channel_name: str,
    expected: Channel,
    tile: Tile,
) -> None:
    assert getattr(tile, channel_name) == expected


@pytest.mark.parametrize(('channel_key', 'expected'), data_test_tile_getitem)
def test_tile_getitem(
    channel_key: ChannelName | str | ChannelKey,
    expected: Channel,
    tile: Tile,
) -> None:
    assert tile[channel_key] == expected


def test_tile_iter(
    tile: Tile,
    tile_channels: Channels,
) -> None:
    assert list(tile) == tile_channels


def test_tile_copy(
    tile: Tile,
) -> None:
    copied_tile = tile.copy()

    assert copied_tile == tile
    assert copied_tile.is_copied is True
    assert id(copied_tile) != id(tile)
    assert id(copied_tile.channels) != id(tile.channels)
