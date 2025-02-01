from __future__ import annotations

import copy
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
    from aviary.core.bounding_box import BoundingBox
    from aviary.core.tile import Tile
    from aviary.core.type_aliases import (
        BufferSize,
        Coordinates,
        GroundSamplingDistance,
        TileSize,
    )


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
    def area(self) -> int:
        """
        Returns:
            Area in square meters
        """
        return self.bounding_box.area

    @property
    def bounding_box(self) -> BoundingBox:
        """
        Returns:
            Bounding box
        """
        if self._tile_ref is None:
            message = 'Tile reference is not set!'
            raise AviaryUserError(message)

        bounding_box = self._tile_ref.bounding_box
        return bounding_box.buffer(buffer_size=self._buffer_size)

    @property
    def coordinates(self) -> Coordinates:
        """
        Returns:
            Coordinates (x_min, y_min) of the tile
        """
        if self._tile_ref is None:
            message = 'Tile reference is not set!'
            raise AviaryUserError(message)

        return self._tile_ref.coordinates

    @property
    def data_type(self) -> type:
        """
        Returns:
            Data type
        """
        return type(self._data)

    @property
    def tile_size(self) -> TileSize:
        """
        Returns:
            Tile size in meters
        """
        if self._tile_ref is None:
            message = 'Tile reference is not set!'
            raise AviaryUserError(message)

        return self._tile_ref.tile_size

    @abstractmethod
    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """

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
    _data: npt.NDArray

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

        self._validate_data()

    def _validate_data(self) -> None:
        """Validates `data`.

        Raises:
            AviaryUserError: Invalid data (`data` is not an array of shape (m, m, n))
        """
        conditions = [
            self._data.ndim != 3,  # noqa: PLR2004
            self._data.shape[0] != self._data.shape[1],
        ]

        if any(conditions):
            message = (
                'Invalid data! '
                'data must be an array of shape (m, m, n).'
            )
            raise AviaryUserError(message)

        self._data = copy.deepcopy(self._data)

    @property
    def ground_sampling_distance(self) -> GroundSamplingDistance:
        """
        Returns:
            Ground sampling distance in meters
        """
        return (self.tile_size + 2 * self._buffer_size) / self.shape[0]

    @property
    def shape(self) -> tuple[int, int, int]:
        """
        Returns:
            Shape
        """
        return self._data.shape

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        data_repr = self.shape
        tile_ref_repr = id(self._tile_ref) if self._tile_ref is not None else None
        return (
            'ArrayChannel(\n'
            f'    data={data_repr},\n'
            f'    name={self._name},\n'
            f'    buffer_size={self._buffer_size},\n'
            f'    tile_ref={tile_ref_repr},\n'
            ')'
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
    _data: gpd.GeoDataFrame

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

        self._validate_data()

    def _validate_data(self) -> None:
        """Validates `data`."""
        self._data = copy.deepcopy(self._data)

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        data_repr = len(self._data)
        tile_ref_repr = id(self._tile_ref) if self._tile_ref is not None else None
        return (
            'GdfChannel(\n'
            f'    data={data_repr},\n'
            f'    name={self._name},\n'
            f'    buffer_size={self._buffer_size},\n'
            f'    tile_ref={tile_ref_repr},\n'
            ')'
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

        conditions = [
            self._data.equals(other.data),
            self._name == other.name,
            self._buffer_size == other.buffer_size,
        ]
        return all(conditions)
