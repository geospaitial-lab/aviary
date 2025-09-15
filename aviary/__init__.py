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
    'VectorChannel',
    'VectorLayer',
    'WMSVersion',
    '__version__',
]

__version__ = '1.0.0b4'

logger.disable(name='aviary')
