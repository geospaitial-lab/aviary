from typing import (
    TypeAlias,
    overload,
)

import numpy as np
import numpy.typing as npt

from aviary.core.channel import _coerce_channel_name
from aviary.core.enums import ChannelName

BufferSize: TypeAlias = int
"""Buffer size in meters"""

TimeStep: TypeAlias = int
"""Time step"""

ChannelKey: TypeAlias = tuple[ChannelName | str, TimeStep | None]
"""Channel name and time step combination"""

ChannelKeySet: TypeAlias = set[ChannelKey]
"""Channel name and time step combinations"""

ChannelNameKeySet: TypeAlias = set[ChannelName | str | ChannelKey]
"""Channel name and time step combinations"""

ChannelNameSet: TypeAlias = set[ChannelName | str]
"""Channel names"""

Coordinate: TypeAlias = int
"""Coordinate in meters"""

Coordinates: TypeAlias = tuple[Coordinate, Coordinate]
"""Coordinates (x_min, y_min) of the tile in meters"""

CoordinatesSet: TypeAlias = npt.NDArray[np.int32]
"""Coordinates (x_min, y_min) of each tile in meters"""

EPSGCode: TypeAlias = int
"""EPSG code"""

FractionalBufferSize: TypeAlias = float
"""Buffer size as a fraction of the spatial extent of the data"""

GroundSamplingDistance: TypeAlias = float
"""Ground sampling distance in meters"""

TileSize: TypeAlias = int
"""Tile size in meters"""


@overload
def _coerce_channel_key(
    channel_key: ChannelName | str | ChannelKey,
) -> ChannelKey:
    ...


@overload
def _coerce_channel_key(
    channel_key: None,
) -> None:
    ...


def _coerce_channel_key(
    channel_key: ChannelName | str | ChannelKey | None,
) -> ChannelKey | None:
    """Coerces `channel_key` to `ChannelKey`.

    Parameters:
        channel_key: Channel name or channel name and time step combination

    Returns:
        Channel name and time step combination
    """
    if channel_key is None:
        return None

    if _is_channel_key(channel_key):
        channel_name, time_step = channel_key
    else:
        channel_name = channel_key
        time_step = None

    channel_name = _coerce_channel_name(channel_name=channel_name)
    return channel_name, time_step


def _coerce_channel_keys(
    channel_keys:
        ChannelName | str |
        ChannelKey |
        ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
        bool |
        None,
) -> ChannelKeySet | bool:
    """Coerces `channel_keys` to `ChannelKeySet`.

    Parameters:
        channel_keys: Channel name, channel name and time step combination, channel names,
            channel name and time step combinations, no channels (False or None), or all channels (True)

    Returns:
        Channel name and time step combinations or all channels (True)
    """
    if channel_keys is True:
        return True

    if channel_keys is False or channel_keys is None:
        return set()

    if isinstance(channel_keys, (ChannelName | str)) or _is_channel_key(channel_keys):
        return {_coerce_channel_key(channel_key=channel_keys)}

    return {
        _coerce_channel_key(channel_key=channel_key)
        for channel_key in channel_keys
    }


def _is_channel_key(
    value: object,
) -> bool:
    """Checks if `value` is a valid `ChannelKey`.

    Parameters:
        value: Value

    Returns:
        True if the value is a valid ChannelKey, False otherwise
    """
    if not isinstance(value, tuple):
        return False

    if len(value) != 2:  # noqa: PLR2004
        return False

    conditions = [
        isinstance(value[0], (ChannelName | str)),
        isinstance(value[1], (TimeStep | None)),
    ]
    return all(conditions)
