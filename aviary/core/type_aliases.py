#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

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
