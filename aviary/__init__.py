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

from loguru import logger

from .core.bounding_box import BoundingBox
from .core.channel import (
    Channel,
    RasterChannel,
    VectorChannel,
)
from .core.enums import (
    ChannelName,
    GeospatialFilterMode,
    InterpolationMode,
    SetFilterMode,
    WMSVersion,
)
from .core.exceptions import (
    AviaryUserError,
    AviaryUserWarning,
)
from .core.grid import (
    Grid,
    GridConfig,
)
from .core.tiles import (
    Tile,
    Tiles,
)
from .core.type_aliases import (
    BufferSize,
    ChannelNameSet,
    Coordinate,
    Coordinates,
    CoordinatesSet,
    EPSGCode,
    FractionalBufferSize,
    GroundSamplingDistance,
    TileSize,
)
from .core.vector import Vector
from .core.vector_layer import VectorLayer

__all__ = [
    'AviaryUserError',
    'AviaryUserWarning',
    'BoundingBox',
    'BufferSize',
    'Channel',
    'ChannelName',
    'ChannelNameSet',
    'Coordinate',
    'Coordinates',
    'CoordinatesSet',
    'EPSGCode',
    'FractionalBufferSize',
    'GeospatialFilterMode',
    'Grid',
    'GridConfig',
    'GroundSamplingDistance',
    'InterpolationMode',
    'RasterChannel',
    'SetFilterMode',
    'Tile',
    'TileSize',
    'Tiles',
    'Vector',
    'VectorChannel',
    'VectorLayer',
    'WMSVersion',
    '__version__',
]

__version__ = '1.0.1'

logger.disable(name='aviary')
