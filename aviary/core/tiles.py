from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy.typing as npt

from aviary.core.enums import Channel

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        BufferSize,
        CoordinatesSet,
        TileSize,
    )


@dataclass
class Tiles(Iterable[tuple[Channel | str, npt.NDArray]]):
    """The tiles specify a batch of tiles.

    Attributes:
        data: data
        coordinates: coordinates (x_min, y_min) of each tile
        tile_size: tile size in meters
        buffer_size: buffer size in meters
    """
    data: dict[Channel | str, npt.NDArray]
    coordinates: CoordinatesSet
    tile_size: TileSize
    buffer_size: BufferSize
    _built_in_channels = frozenset(channel.value for channel in Channel)

    def __init__(
        self,
        data: dict[Channel | str, npt.NDArray],
        coordinates: CoordinatesSet,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
    ) -> None:
        """
        Parameters:
            data: data
            coordinates: coordinates (x_min, y_min) of each tile
            tile_size: tile size in meters
            buffer_size: buffer size in meters
        """
        self._data = data
        self._coordinates = coordinates
        self._tile_size = tile_size
        self._buffer_size = buffer_size

        self._validate()

    def _validate(self) -> None:
        """Validates the tiles."""
        pass
