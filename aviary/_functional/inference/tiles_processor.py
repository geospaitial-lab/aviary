from __future__ import annotations

from typing import TYPE_CHECKING

from aviary.core.tiles import Tiles

if TYPE_CHECKING:
    from aviary.core.enums import ChannelName
    from aviary.core.type_aliases import (
        ChannelKey,
        ChannelKeySet,
        ChannelNameKeySet,
        ChannelNameSet,
    )
    from aviary.tile.tiles_processor import TilesProcessor


def copy_processor(
    tiles: Tiles,
    channel_key: ChannelName | str | ChannelKey,
    new_channel_key: ChannelName | str | ChannelKey | None = None,
) -> Tiles:
    """Copies the channel.

    Parameters:
        tiles: Tiles
        channel_key: Channel name or channel name and time step combination
        new_channel_key: New channel name or channel name and time step combination

    Returns:
        Tiles
    """


def normalize_processor(
    tiles: Tiles,
    channel_key: ChannelName | str | ChannelKey,
    min_value: float,
    max_value: float,
    new_channel_key: ChannelName | str | ChannelKey | None = None,
) -> Tiles:
    """Normalizes the channel.

    Parameters:
        tiles: Tiles
        channel_key: Channel name or channel name and time step combination
        min_value: Minimum value
        max_value: Maximum value
        new_channel_key: New channel name or channel name and time step combination

    Returns:
        Tiles
    """


def parallel_composite_processor(
    tiles: Tiles,
    tiles_processors: list[TilesProcessor],
) -> Tiles:
    """Processes the tiles with each tiles processor.

    Parameters:
        tiles: Tiles
        tiles_processors: Tiles processors

    Returns:
        Tiles
    """
    tiles = [
        tiles_processor(tiles=tiles.copy())
        for tiles_processor in tiles_processors
    ]
    return Tiles.from_tiles(
        tiles=tiles,
        copy=False,
    )


def remove_buffer_processor(
    tiles: Tiles,
    channel_keys:
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        bool |
        None = True,
) -> Tiles:
    """Removes the buffer of the channels.

    Parameters:
        tiles: Tiles
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, no channels (False or None), or all channels (True)

    Returns:
        Tiles
    """
    return tiles.remove_buffer(
        channel_keys=channel_keys,
        inplace=True,
    )


def remove_processor(
    tiles: Tiles,
    channel_keys:
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        bool |
        None = True,
) -> Tiles:
    """Removes the channels.

    Parameters:
        tiles: Tiles
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, no channels (False or None), or all channels (True)

    Returns:
        Tiles
    """
    return tiles.remove(
        channel_keys=channel_keys,
        inplace=True,
    )


def select_processor(
    tiles: Tiles,
    channel_keys:
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        bool |
        None = True,
) -> Tiles:
    """Selects the channels.

    Parameters:
        tiles: Tiles
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, no channels (False or None), or all channels (True)

    Returns:
        Tiles
    """
    return tiles.select(
        channel_keys=channel_keys,
        inplace=True,
    )


def sequential_composite_processor(
    tiles: Tiles,
    tiles_processors: list[TilesProcessor],
) -> Tiles:
    """Processes the tiles with each tiles processor.

    Parameters:
        tiles: Tiles
        tiles_processors: Tiles processors

    Returns:
        Tiles
    """
    for tiles_processor in tiles_processors:
        tiles = tiles_processor(tiles=tiles)

    return tiles


def standardize_processor(
    tiles: Tiles,
    channel_key: ChannelName | str | ChannelKey,
    mean_value: float,
    std_value: float,
    new_channel_key: ChannelName | str | ChannelKey | None = None,
) -> Tiles:
    """Standardizes the channel.

    Parameters:
        tiles: Tiles
        channel_key: Channel name or channel name and time step combination
        mean_value: Mean value
        std_value: Standard deviation value
        new_channel_key: New channel name or channel name and time step combination

    Returns:
        Tiles
    """


def vectorize_processor(
    tiles: Tiles,
    channel_key: ChannelName | str | ChannelKey,
    ignore_background_class: bool = True,
    new_channel_key: ChannelName | str | ChannelKey | None = None,
    max_num_threads: int | None = None,
) -> Tiles:
    """Vectorizes the channel.

    Parameters:
        tiles: Tiles
        channel_key: Channel name or channel name and time step combination
        ignore_background_class: If True, the background class (value 0) is not vectorized
        new_channel_key: New channel name or channel name and time step combination
        max_num_threads: Maximum number of threads

    Returns:
        Tiles
    """
