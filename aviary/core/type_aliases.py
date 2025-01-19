from typing import TypeAlias

import numpy as np
import numpy.typing as npt

from aviary.core.enums import Channel

BufferSize: TypeAlias = int
Channels: TypeAlias = list[Channel | str]
ChannelsSet: TypeAlias = set[Channel | str]
Coordinate: TypeAlias = int
Coordinates: TypeAlias = tuple[Coordinate, Coordinate]
CoordinatesSet: TypeAlias = npt.NDArray[np.int32]
EPSGCode: TypeAlias = int
GroundSamplingDistance: TypeAlias = float
TileSize: TypeAlias = int
TimeStep: TypeAlias = int
