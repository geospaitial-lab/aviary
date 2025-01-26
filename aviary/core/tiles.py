from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy.typing as npt

from aviary.core.enums import Channel
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        BufferSize,
        ChannelsSet,
        CoordinatesSet,
        GroundSamplingDistance,
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
        self._cast_channels()
        self._validate_data()
        self._validate_tile_size()
        self._validate_buffer_size()

    def _cast_channels(self) -> None:
        """Casts the channels to `Channel`."""
        self._data = {
            Channel(channel)
            if isinstance(channel, str) and channel in self._built_in_channels else channel: data
            for channel, data in self
        }

    def _validate_data(self) -> None:
        """Validates `data`.

        Raises:
            AviaryUserError: Invalid data (`data` is an empty dictionary)
            AviaryUserError: Invalid data (`data` of a channel is not an array of shape (b, n, n, t) or
                its shape is not equal to the shape of the other channels)
        """
        if not self._data:
            message = (
                'Invalid data! '
                'data must be a non-empty dictionary.'
            )
            raise AviaryUserError(message)

        for channel, data in self:
            conditions = [
                data.ndim != 4,  # noqa: PLR2004
                data.shape[1] != data.shape[2],
                data.shape != self.shape,
            ]

            if any(conditions):
                message = (
                    'Invalid data! '
                    f'data of the {channel} channel must be an array of shape (b, n, n, t) and '
                    'its shape must be equal to the shape of the other channels.'
                )
                raise AviaryUserError(message)

    def _validate_tile_size(self) -> None:
        """Validates `tile_size`.

        Raises:
            AviaryUserError: Invalid tile size (`tile_size` <= 0)
        """
        if self._tile_size <= 0:
            message = (
                'Invalid tile size! '
                'tile_size must be positive.'
            )
            raise AviaryUserError(message)

    def _validate_buffer_size(self) -> None:
        """Validates `buffer_size`.

        Raises:
            AviaryUserError: Invalid buffer size (`buffer_size` < 0)
        """
        if self._buffer_size < 0:
            message = (
                'Invalid buffer size! '
                'buffer_size must be non-negative.'
            )
            raise AviaryUserError(message)

    @property
    def data(self) -> dict[Channel | str, npt.NDArray]:
        """
        Returns:
            data
        """
        return self._data

    @property
    def coordinates(self) -> CoordinatesSet:
        """
        Returns:
            coordinates (x_min, y_min) of each tile
        """
        return self._coordinates

    @property
    def tile_size(self) -> TileSize:
        """
        Returns:
            tile size in meters
        """
        return self._tile_size

    @property
    def buffer_size(self) -> BufferSize:
        """
        Returns:
            buffer size in meters
        """
        return self._buffer_size

    @property
    def area(self) -> int:
        """
        Returns:
            area in square meters
        """
        return (self._tile_size + 2 * self._buffer_size) ** 2

    @property
    def channels(self) -> ChannelsSet:
        """
        Returns:
            channels
        """
        return set(self._data.keys())

    @property
    def ground_sampling_distance(self) -> GroundSamplingDistance:
        """
        Returns:
            ground sampling distance in meters
        """
        return (self._tile_size + 2 * self._buffer_size) / self.shape[1]

    @property
    def num_channels(self) -> int:
        """
        Returns:
            number of channels
        """
        return len(self)

    @property
    def num_time_steps(self) -> int:
        """
        Returns:
            number of time steps
        """
        return self.shape[-1]

    @property
    def shape(self) -> tuple[int, int, int, int]:
        """
        Returns:
            shape of the data
        """
        return next(iter(self))[1].shape

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            string representation
        """
        data_repr = '\n'.join(
            f'        {channel}: {data.shape},'
            for channel, data in self
        )

        max_coordinates = 4
        coordinates_repr = self._coordinates.tolist()

        if len(coordinates_repr) > max_coordinates:
            coordinates_repr = (
                coordinates_repr[:max_coordinates // 2] +
                [Ellipsis] +
                coordinates_repr[-max_coordinates // 2:]
            )

        coordinates_repr = str(coordinates_repr).replace('Ellipsis', '...')
        return (
            'Tile(\n'
            f'    data=\n{data_repr}\n'
            f'    coordinates={coordinates_repr},\n'
            f'    tile_size={self._tile_size},\n'
            f'    buffer_size={self._buffer_size},\n'
            ')'
        )

    def __len__(self) -> int:
        """Computes the number of channels.

        Returns:
            number of channels
        """
        return len(self._data)
