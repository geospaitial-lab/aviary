from typing import TypeAlias

import numpy as np
import numpy.typing as npt

from aviary.core.channel import Channel
from aviary.core.enums import ChannelName

BufferSize: TypeAlias = int
ChannelNames: TypeAlias = list[ChannelName | str]
ChannelNameSet: TypeAlias = set[ChannelName | str]
Channels: TypeAlias = list[Channel]
Coordinate: TypeAlias = int
Coordinates: TypeAlias = tuple[Coordinate, Coordinate]
CoordinatesSet: TypeAlias = npt.NDArray[np.int32]
EPSGCode: TypeAlias = int
GroundSamplingDistance: TypeAlias = float
TileSize: TypeAlias = int
TimeStep: TypeAlias = int
