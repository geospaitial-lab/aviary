from typing import TypeAlias

import numpy as np
import numpy.typing as npt

from aviary.core.channel import _coerce_channel_name
from aviary.core.enums import ChannelName

BufferSize: TypeAlias = int
TimeStep: TypeAlias = int
ChannelKey: TypeAlias = tuple[ChannelName | str, TimeStep | None]
ChannelKeySet: TypeAlias = set[ChannelKey]
ChannelNameKeySet: TypeAlias = set[ChannelName | str | ChannelKey]
ChannelNameSet: TypeAlias = set[ChannelName | str]
Coordinate: TypeAlias = int
Coordinates: TypeAlias = tuple[Coordinate, Coordinate]
CoordinatesSet: TypeAlias = npt.NDArray[np.int32]
EPSGCode: TypeAlias = int
FractionalBufferSize: TypeAlias = float
GroundSamplingDistance: TypeAlias = float
TileSize: TypeAlias = int


def _coerce_channel_key(
    channel_key: ChannelName | str | ChannelKey,
) -> ChannelKey:
    """Coerces `channel_key` to `ChannelKey`.

    Parameters:
        channel_key: Channel name or channel name and time step combination

    Returns:
        Channel name and time step combination
    """
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
        None,
) -> ChannelKeySet:
    """Parses `channel_keys` to `ChannelKeySet`.
    """Coerces `channel_keys` to `ChannelKeySet`.

    Parameters:
        channel_keys: Channel name, channel name and time step combination, channel names,
            or channel name and time step combinations

    Returns:
        Channel name and time step combinations
    """
    if channel_keys is None:
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
