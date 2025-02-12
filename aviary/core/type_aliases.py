from typing import TypeAlias

import numpy as np
import numpy.typing as npt

from aviary.core.channel import Channel
from aviary.core.enums import ChannelName

BufferSize: TypeAlias = int
TimeStep: TypeAlias = int
ChannelKey: TypeAlias = tuple[ChannelName | str, TimeStep | None]
ChannelKeySet: TypeAlias = set[ChannelKey]
ChannelNameKeySet: TypeAlias = set[ChannelName | str | ChannelKey]
ChannelNames: TypeAlias = list[ChannelName | str]
ChannelNameSet: TypeAlias = set[ChannelName | str]
Channels: TypeAlias = list[Channel]
Coordinate: TypeAlias = int
Coordinates: TypeAlias = tuple[Coordinate, Coordinate]
CoordinatesSet: TypeAlias = npt.NDArray[np.int32]
EPSGCode: TypeAlias = int
FractionalBufferSize: TypeAlias = float
GroundSamplingDistance: TypeAlias = float
TileSize: TypeAlias = int


def _is_channel_key(
    value: object,
) -> bool:
    """Checks if `value` is a valid ChannelKey.

    Parameters:
        value: value

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
