from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import geopandas as gpd
    import numpy.typing as npt

from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.tile import Tile
    from aviary.core.type_aliases import BufferSize


class Channel(ABC):
    """Abstract class for channels

    Currently implemented channels:
        - `ArrayChannel`: Contains an array
        - `GdfChannel`: Contains a geodataframe
    """
    _built_in_channel_names = frozenset(channel_name.value for channel_name in ChannelName)

    def __init__(
        self,
        data: object,
        name: ChannelName | str,
        buffer_size: BufferSize,
        tile_ref: Tile | None = None,
    ) -> None:
        """
        Parameters:
            data: Data
            name: Name
            buffer_size: Buffer size in meters
            tile_ref: Tile reference
        """
        self._data = data
        self._name = name
        self._buffer_size = buffer_size
        self._tile_ref = tile_ref

        self._validate()

    def _validate(self) -> None:
        """Validates the channel."""
        self._cast_name()
        self._validate_buffer_size()

    def _cast_name(self) -> None:
        """Casts the name to `ChannelName`."""
        if isinstance(self._name, str) and self._name in self._built_in_channel_names:
            self._name = ChannelName(self._name)

    def _validate_buffer_size(self) -> None:
        """Validates `buffer_size`.

        Raises:
            AviaryUserError: Invalid buffer size (`buffer_size` is negative)
        """
        if self._buffer_size < 0:
            message = (
                'Invalid buffer size! '
                'buffer_size must be positive or zero.'
            )
            raise AviaryUserError(message)

    @property
    def data(self) -> object:
        """
        Returns:
            Data
        """
        return self._data

    @property
    def name(self) -> ChannelName | str:
        """
        Returns:
            Name
        """
        return self._name

    @property
    def buffer_size(self) -> BufferSize:
        """
        Returns:
            Buffer size in meters
        """
        return self._buffer_size

    @property
    def data_type(self) -> type:
        """
        Returns:
            Data type
        """
        return type(self._data)

    @abstractmethod
    def __eq__(
        self,
        other: object,
    ) -> bool:
        """Compares the channels.

        Parameters:
            other: Other channel

        Returns:
            True if the channels are equal, false otherwise
        """

    def ref_tile(
        self,
        tile: Tile,
    ) -> None:
        """References the tile.

        Parameters:
            tile: Tile
        """
        self._tile_ref = tile


class ArrayChannel(Channel):
    """Channel that contains an array"""

    def __init__(
        self,
        data: npt.NDArray,
        name: ChannelName | str,
        buffer_size: BufferSize,
        tile_ref: Tile | None = None,
    ) -> None:
        """
        Parameters:
            data: Data
            name: Name
            buffer_size: Buffer size in meters
            tile_ref: Tile reference
        """
        super().__init__(
            data=data,
            name=name,
            buffer_size=buffer_size,
            tile_ref=tile_ref,
        )

    def __eq__(
        self,
        other: ArrayChannel,
    ) -> bool:
        """Compares the array channels.

        Parameters:
            other: Other array channel

        Returns:
            True if the array channels are equal, false otherwise
        """
        if not isinstance(other, ArrayChannel):
            return False

        conditions = [
            np.array_equal(self._data, other.data),
            self._name == other.name,
            self._buffer_size == other.buffer_size,
        ]
        return all(conditions)


class GdfChannel(Channel):
    """Channel that contains a geodataframe"""

    def __init__(
        self,
        data: gpd.GeoDataFrame,
        name: ChannelName | str,
        buffer_size: BufferSize,
        tile_ref: Tile | None = None,
    ) -> None:
        """
        Parameters:
            data: Data
            name: Name
            buffer_size: Buffer size in meters
            tile_ref: Tile reference
        """
        super().__init__(
            data=data,
            name=name,
            buffer_size=buffer_size,
            tile_ref=tile_ref,
        )

    def __eq__(
        self,
        other: GdfChannel,
    ) -> bool:
        """Compares the geodataframe channels.

        Parameters:
            other: Other geodataframe channel

        Returns:
            True if the geodataframe channels are equal, false otherwise
        """
        if not isinstance(other, GdfChannel):
            return False

        # noinspection PyUnresolvedReferences
        conditions = [
            self._data.equals(other.data),
            self._name == other.name,
            self._buffer_size == other.buffer_size,
        ]
        return all(conditions)
