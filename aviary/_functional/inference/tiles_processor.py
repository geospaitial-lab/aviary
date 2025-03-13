from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aviary.core.enums import ChannelName
    from aviary.core.tiles import Tiles
    from aviary.core.type_aliases import (
        ChannelKey,
        ChannelKeySet,
        ChannelNameKeySet,
        ChannelNameSet,
    )
    from aviary.inference.tiles_processor import TilesProcessor


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
    num_workers: int = 1,
) -> Tiles:
    """Vectorizes the channel.

    Parameters:
        tiles: Tiles
        channel_key: Channel name or channel name and time step combination
        ignore_background_class: If True, the background class (value 0) is not vectorized
        new_channel_key: New channel name or channel name and time step combination
        num_workers: Number of workers

    Returns:
        Tiles
    """
