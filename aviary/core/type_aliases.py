from typing import TypeAlias

import numpy as np
import numpy.typing as npt

from aviary.core.enums import ChannelName

BufferSize: TypeAlias = int
"""Buffer size in meters"""

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
