from typing import TypeAlias

import numpy as np
import numpy.typing as npt

from aviary.core.enums import ChannelType

BufferSize: TypeAlias = int
ChannelTypes: TypeAlias = list[ChannelType | str]
ChannelTypeSet: TypeAlias = set[ChannelType | str]
Coordinate: TypeAlias = int
Coordinates: TypeAlias = tuple[Coordinate, Coordinate]
CoordinatesSet: TypeAlias = npt.NDArray[np.int32]
EPSGCode: TypeAlias = int
GroundSamplingDistance: TypeAlias = float
TileSize: TypeAlias = int
TimeStep: TypeAlias = int
