import inspect
import pickle

import numpy as np
import pytest

from aviary.core.channel import Channel
from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError
from aviary.core.grid import Grid
from aviary.core.tiles import (
    Tile,
    Tiles,
)
from aviary.core.type_aliases import (
    Coordinates,
    CoordinatesSet,
    TileSize,
)
from tests.core.data.data_test_tiles import (
    data_test_tiles_bool,
    data_test_tiles_contains,
    data_test_tiles_eq,
    data_test_tiles_getattr,
    data_test_tiles_getitem,
    data_test_tiles_init,
    data_test_tiles_init_exceptions,
)


def test_tiles_type_alias() -> None:
    assert Tile is Tiles


@pytest.mark.parametrize(
    (
        'channels',
        'coordinates',
        'tile_size',
        'metadata',
        'copy',
        'expected_channels',
        'expected_coordinates',
        'expected_tile_size',
        'expected_metadata',
        'expected_copy',
    ),
    data_test_tiles_init,
)
def test_tiles_init(
    channels: list[Channel],
    coordinates: Coordinates | CoordinatesSet,
    tile_size: TileSize,
    metadata: dict[str, object] | None,
    copy: bool,
    expected_channels: list[Channel],
    expected_coordinates: Coordinates | CoordinatesSet,
    expected_tile_size: TileSize,
    expected_metadata: dict[str, object],
    expected_copy: bool,
) -> None:
    tiles = Tiles(
        channels=channels,
        coordinates=coordinates,
        tile_size=tile_size,
        metadata=metadata,
        copy=copy,
    )

    assert tiles.channels == expected_channels

    if not isinstance(coordinates, np.ndarray):
        assert tiles.coordinates == expected_coordinates
    else:
        np.testing.assert_array_equal(tiles.coordinates, expected_coordinates)

    assert tiles.tile_size == expected_tile_size
    assert tiles.metadata == expected_metadata
    assert tiles.is_copied is expected_copy


@pytest.mark.parametrize(('channels', 'coordinates', 'tile_size', 'message'), data_test_tiles_init_exceptions)
def test_tiles_init_exceptions(
    channels: list[Channel],
    coordinates: CoordinatesSet,
    tile_size: TileSize,
    message: str,
) -> None:
    metadata = None
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = Tiles(
            channels=channels,
            coordinates=coordinates,
            tile_size=tile_size,
            metadata=metadata,
            copy=copy,
        )


def test_tiles_init_defaults() -> None:
    signature = inspect.signature(Tiles)
    metadata = signature.parameters['metadata'].default
    copy = signature.parameters['copy'].default

    expected_metadata = None
    expected_copy = False

    assert metadata is expected_metadata
    assert copy is expected_copy


def test_tiles_mutability_no_copy(
    tiles_channels: list[Channel],
    tiles_coordinates: CoordinatesSet,
    metadata: dict[str, object],
) -> None:
    tile_size = 128
    copy = False

    tiles = Tiles(
        channels=tiles_channels,
        coordinates=tiles_coordinates,
        tile_size=tile_size,
        metadata=metadata,
        copy=copy,
    )

    assert id(tiles._channels) == id(tiles_channels)

    for channel, channel_ in zip(tiles, tiles_channels, strict=True):
        assert id(channel) == id(channel_)

    assert id(tiles.channels) == id(tiles._channels)
    assert id(tiles._coordinates) != id(tiles_coordinates)
    assert id(tiles.coordinates) != id(tiles._coordinates)
    assert id(tiles._metadata) == id(metadata)
    assert id(tiles.metadata) == id(tiles._metadata)


def test_tiles_mutability_copy(
    tiles_channels: list[Channel],
    tiles_coordinates: CoordinatesSet,
    metadata: dict[str, object],
) -> None:
    tile_size = 128
    copy = True

    tiles = Tiles(
        channels=tiles_channels,
        coordinates=tiles_coordinates,
        tile_size=tile_size,
        metadata=metadata,
        copy=copy,
    )

    assert id(tiles._channels) != id(tiles_channels)

    for channel, channel_ in zip(tiles, tiles_channels, strict=True):
        assert id(channel) != id(channel_)

    assert id(tiles.channels) == id(tiles._channels)
    assert id(tiles._coordinates) != id(tiles_coordinates)
    assert id(tiles.coordinates) != id(tiles._coordinates)
    assert id(tiles._metadata) != id(metadata)
    assert id(tiles.metadata) == id(tiles._metadata)


def test_tiles_setters(
    tiles: Tiles,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tiles.channels = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tiles.coordinates = None

    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        tiles.tile_size = None


def test_tiles_serializability(
    tiles: Tiles,
) -> None:
    serialized_tiles = pickle.dumps(tiles)
    deserialized_tiles = pickle.loads(serialized_tiles)  # noqa: S301

    assert tiles == deserialized_tiles


def test_tiles_area(
    tiles: Tiles,
) -> None:
    expected = 32768

    assert tiles.area == expected


def test_tiles_batch_size(
    tiles: Tiles,
) -> None:
    expected = 2

    assert tiles.batch_size == expected


def test_tiles_channel_names(
    tiles: Tiles,
) -> None:
    expected = {
        ChannelName.R,
        ChannelName.G,
        ChannelName.B,
        'custom',
    }

    assert tiles.channel_names == expected


def test_tiles_grid(
    tiles: Tiles,
    tiles_coordinates: CoordinatesSet,
) -> None:
    expected_tile_size = 128
    expected = Grid(
        coordinates=tiles_coordinates,
        tile_size=expected_tile_size,
    )

    assert tiles.grid == expected


@pytest.mark.parametrize(('other', 'expected'), data_test_tiles_eq)
def test_tiles_eq(
    other: object,
    expected: bool,
    tiles: Tiles,
) -> None:
    equals = tiles == other

    assert equals is expected


def test_tiles_len(
    tiles: Tiles,
) -> None:
    expected = 4

    assert len(tiles) == expected


@pytest.mark.parametrize(('tiles', 'expected'), data_test_tiles_bool)
def test_tiles_bool(
    tiles: Tiles,
    expected: bool,
) -> None:
    assert bool(tiles) is expected


@pytest.mark.parametrize(('channel_name', 'expected'), data_test_tiles_contains)
def test_tiles_contains(
    channel_name: ChannelName | str,
    expected: bool,
    tiles: Tiles,
) -> None:
    contains = channel_name in tiles

    assert contains is expected


@pytest.mark.parametrize(('channel_name', 'expected'), data_test_tiles_getattr)
def test_tiles_getattr(
    channel_name: str,
    expected: Channel,
    tiles: Tiles,
) -> None:
    channel = getattr(tiles, channel_name)

    assert channel == expected


@pytest.mark.parametrize(('channel_name', 'expected'), data_test_tiles_getitem)
def test_tiles_getitem(
    channel_name: ChannelName | str,
    expected: Channel,
    tiles: Tiles,
) -> None:
    channel = tiles[channel_name]

    assert channel == expected


def test_tiles_iter(
    tiles: Tiles,
    tiles_channels: list[Channel],
) -> None:
    assert list(tiles) == tiles_channels


def test_tiles_copy(
    tiles: Tiles,
) -> None:
    copied_tiles = tiles.copy()

    assert copied_tiles == tiles
    assert copied_tiles.is_copied is True
    assert id(copied_tiles) != id(tiles)
    assert id(copied_tiles.channels) != id(tiles.channels)

    for copied_channel, channel in zip(copied_tiles, tiles, strict=True):
        assert id(copied_channel) != id(channel)

    assert id(copied_tiles.metadata) != id(tiles.metadata)
