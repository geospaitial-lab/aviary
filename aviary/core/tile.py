from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
)
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Literal,
)

import numpy as np
import numpy.typing as npt

from aviary.core.bounding_box import BoundingBox
from aviary.core.enums import Channel
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        BufferSize,
        Channels,
        ChannelsSet,
        Coordinates,
        GroundSamplingDistance,
        TileSize,
        TimeStep,
    )


@dataclass
class Tile(Iterable[tuple[Channel | str, npt.NDArray]]):
    """A tile specifies the data and the spatial extent of a tile.

    Attributes:
        data: data
        coordinates: coordinates (x_min, y_min) of the tile
        tile_size: tile size in meters
        buffer_size: buffer size in meters
    """
    data: dict[Channel | str, npt.NDArray]
    coordinates: Coordinates
    tile_size: TileSize
    buffer_size: BufferSize
    _built_in_channels = frozenset(channel.value for channel in Channel)

    def __init__(
        self,
        data: dict[Channel | str, npt.NDArray],
        coordinates: Coordinates,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
    ) -> None:
        """
        Parameters:
            data: data
            coordinates: coordinates (x_min, y_min) of the tile
            tile_size: tile size in meters
            buffer_size: buffer size in meters
        """
        self._data = data
        self._coordinates = coordinates
        self._tile_size = tile_size
        self._buffer_size = buffer_size

        self._validate()

    def _validate(self) -> None:
        """Validates the tile."""
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
        """Validates data.

        Raises:
            AviaryUserError: Invalid data (`data` is an empty dictionary)
            AviaryUserError: Invalid data (`data` of a channel is not an array of shape (n, n, t) or
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
                data.ndim != 3,  # noqa: PLR2004
                data.shape[0] != data.shape[1],
                data.shape != self.shape,
            ]

            if any(conditions):
                message = (
                    'Invalid data! '
                    f'data of the {channel} channel must be an array of shape (n, n, t) and '
                    'its shape must be equal to the shape of the other channels.'
                )
                raise AviaryUserError(message)

    def _validate_tile_size(self) -> None:
        """Validates tile_size.

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
        """Validates buffer_size.

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
    def coordinates(self) -> Coordinates:
        """
        Returns:
            coordinates (x_min, y_min) of the tile
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
        return self.bounding_box.area

    @property
    def bounding_box(self) -> BoundingBox:
        """
        Returns:
            bounding box
        """
        x_min, y_min = self._coordinates
        x_max = x_min + self._tile_size
        y_max = y_min + self._tile_size
        bounding_box = BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )
        return bounding_box.buffer(buffer_size=self._buffer_size)

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
        return (self._tile_size + 2 * self._buffer_size) / self.shape[0]

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
    def shape(self) -> tuple[int, int, int]:
        """
        Returns:
            shape of the data
        """
        return next(iter(self))[1].shape

    @classmethod
    def from_composite(
        cls,
        data: npt.NDArray,
        channels: Channels,
        coordinates: Coordinates,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
    ) -> Tile:
        """Creates a tile from composite data.

        Parameters:
            data: composite data
            channels: channels
            coordinates: coordinates (x_min, y_min) of the tile
            tile_size: tile size in meters
            buffer_size: buffer size in meters

        Returns:
            tile

        Raises:
            AviaryUserError: Invalid data (`data` is not an array of shape (n, n, c))
            AviaryUserError: Invalid channels (`channels` is an empty list)
            AviaryUserError: Invalid channels (the number of channels is not equal to the number of channels
                of the data)
        """
        if data.ndim == 2:  # noqa: PLR2004
            data = data[..., np.newaxis]

        conditions = [
            data.ndim != 3,  # noqa: PLR2004
            data.shape[0] != data.shape[1],
        ]

        if any(conditions):
            message = (
                'Invalid data! '
                'data must be an array of shape (n, n, c).'
            )
            raise AviaryUserError(message)

        if not channels:
            message = (
                'Invalid channels! '
                'channels must be a non-empty list.'
            )
            raise AviaryUserError(message)

        if data.shape[-1] != len(channels):
            message = (
                'Invalid channels! '
                'The number of channels must be equal to the number of channels of the data.'
            )
            raise AviaryUserError(message)

        channels = [
            Channel(channel) if isinstance(channel, str) and channel in cls._built_in_channels else channel
            for channel in channels
        ]

        data = {
            channel: data[..., i]
            for i, channel in enumerate(channels)
        }
        return cls(
            data=data,
            coordinates=coordinates,
            tile_size=tile_size,
            buffer_size=buffer_size,
        )

    @classmethod
    def from_tiles(
        cls,
        tiles: list[Tile],
        axis: Literal['channel', 'time_step'] = 'channel',
    ) -> Tile:
        """Creates a tile from tiles.

        Parameters:
            tiles: tiles
            axis: axis to concatenate the tiles (`channel`, `time_step`)

        Returns:
            tile

        Raises:
            AviaryUserError: Invalid tiles (`tiles` is an empty list)
            AviaryUserError: Invalid tiles (the coordinates, tile sizes and buffer sizes of the tiles are not equal)
            AviaryUserError: Invalid tiles (the number of time steps of the tiles are not equal)
            AviaryUserError: Invalid tiles (the channels of the tiles are not equal)
            AviaryUserError: Invalid axis
        """
        if not tiles:
            message = (
                'Invalid tiles! '
                'tiles must be a non-empty list.'
            )
            raise AviaryUserError(message)

        first_tile = tiles[0]
        coordinates = first_tile.coordinates
        tile_size = first_tile.tile_size
        buffer_size = first_tile.buffer_size

        for tile in tiles:
            conditions = [
                tile.coordinates != coordinates,
                tile.tile_size != tile_size,
                tile.buffer_size != buffer_size,
            ]

            if any(conditions):
                message = (
                    'Invalid tiles! '
                    'The coordinates, tile sizes and buffer sizes of the tiles must be equal.'
                )
                raise AviaryUserError(message)

        if axis == 'channel':
            num_time_steps = first_tile.num_time_steps

            for tile in tiles:
                if tile.num_time_steps != num_time_steps:
                    message = (
                        'Invalid tiles! '
                        'The number of time steps of the tiles must be equal.'
                    )
                    raise AviaryUserError(message)

            data = {
                channel: data
                for tile in tiles
                for channel, data in tile
            }
            return cls(
                data=data,
                coordinates=coordinates,
                tile_size=tile_size,
                buffer_size=buffer_size,
            )

        if axis == 'time_step':
            channels = first_tile.channels

            for tile in tiles:
                if tile.channels != channels:
                    message = (
                        'Invalid tiles! '
                        'The channels of the tiles must be equal.'
                    )
                    raise AviaryUserError(message)

            data = {
                channel: np.concatenate([tile[channel] for tile in tiles], axis=-1)
                for channel in channels
            }
            return cls(
                data=data,
                coordinates=coordinates,
                tile_size=tile_size,
                buffer_size=buffer_size,
            )

        message = 'Invalid axis!'
        raise AviaryUserError(message)

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            string representation
        """
        data_repr = '\n'.join(
            f'        {channel}: {data.shape},'
            for channel, data in self
        )
        return (
            'Tile(\n'
            f'    data=\n{data_repr}\n'
            f'    coordinates={self._coordinates},\n'
            f'    tile_size={self._tile_size},\n'
            f'    buffer_size={self._buffer_size},\n'
            ')'
        )

    def __eq__(
        self,
        other: Tile,
    ) -> bool:
        """Compares the tiles.

        Parameters:
            other: other tile

        Returns:
            True if the tiles are equal, False otherwise
        """
        if not isinstance(other, Tile):
            return False

        conditions = [
            self._data.keys() == other.data.keys(),
            all(
                np.array_equal(self._data[channel], other.data.get(channel, None))
                for channel in self.channels
            ),
            self._coordinates == other.coordinates,
            self._tile_size == other.tile_size,
            self._buffer_size == other.buffer_size,
        ]
        return all(conditions)

    def __len__(self) -> int:
        """Computes the number of channels.

        Returns:
            number of channels
        """
        return len(self._data)

    def __getattr__(
        self,
        channel: str,
    ) -> npt.NDArray:
        """Returns the channel data.

        Parameters:
            channel: channel

        Returns:
            channel data

        Raises:
            AviaryUserError: Invalid channel (the channel is not available)
        """
        if channel in self._built_in_channels:
            channel = Channel(channel)

        if channel not in self.channels:
            message = (
                'Invalid channel! '
                f'The {channel} channel is not available.'
            )
            raise AviaryUserError(message)

        return self[channel]

    def __getitem__(
        self,
        channel: Channel | str,
    ) -> npt.NDArray:
        """Returns the channel data.

        Parameters:
            channel: channel

        Returns:
            channel data

        Raises:
            AviaryUserError: Invalid channel (the channel is not available)
        """
        if isinstance(channel, str) and channel in self._built_in_channels:
            channel = Channel(channel)

        if channel not in self.channels:
            message = (
                'Invalid channel! '
                f'The {channel} channel is not available.'
            )
            raise AviaryUserError(message)

        return self._data[channel]

    def __iter__(self) -> Iterator[tuple[Channel | str, npt.NDArray]]:
        """Iterates over the channels.

        Yields:
            channel and data
        """
        yield from self._data.items()

    def append_channel(
        self,
        data: npt.NDArray,
        channel: Channel | str,
        inplace: bool = False,
    ) -> Tile:
        """Appends the channel to the tile.

        Parameters:
            data: channel data
            channel: channel
            inplace: if True, the channel is appended inplace

        Returns:
            tile

        Raises:
            AviaryUserError: Invalid channel (the channel is already available)
        """
        if isinstance(channel, str) and channel in self._built_in_channels:
            channel = Channel(channel)

        if channel in self.channels:
            message = (
                'Invalid channel! '
                f'The {channel} channel is already available.'
            )
            raise AviaryUserError(message)

        if inplace:
            self._data[channel] = data
            self._validate()
            return self

        data_ = {
            **self._data,
            channel: data,
        }
        return Tile(
            data=data_,
            coordinates=self._coordinates,
            tile_size=self._tile_size,
            buffer_size=self._buffer_size,
        )

    def remove_buffer(
        self,
        inplace: bool = False,
    ) -> Tile:
        """Removes the buffer from the tile.

        Parameters:
            inplace: if True, the buffer is removed inplace

        Returns:
            tile
        """
        if self._buffer_size == 0:
            if inplace:
                return self

            return Tile(
                data=self._data,
                coordinates=self._coordinates,
                tile_size=self._tile_size,
                buffer_size=self._buffer_size,
            )

        buffer_size = int(self._buffer_size / self.ground_sampling_distance)

        data = {
            channel: data[buffer_size:-buffer_size, buffer_size:-buffer_size, :]
            for channel, data in self
        }

        if inplace:
            self._data = data
            self._buffer_size = 0
            self._validate()
            return self

        return Tile(
            data=data,
            coordinates=self._coordinates,
            tile_size=self._tile_size,
            buffer_size=0,
        )

    def to_cir(
        self,
        time_step: TimeStep = 0,
    ) -> npt.NDArray:
        """Converts the tile to color-infrared data.

        Parameters:
            time_step: time step (supports negative indexing)

        Returns:
            color-infrared data
        """
        channels = [
            Channel.NIR,
            Channel.R,
            Channel.G,
        ]
        return self.to_composite(
            channels=channels,
            time_step=time_step,
        )

    def to_composite(
        self,
        channels: Channels,
        time_step: TimeStep = 0,
    ) -> npt.NDArray:
        """Converts the tile to composite data.

        Parameters:
            channels: channels
            time_step: time step (supports negative indexing)

        Returns:
            composite data

        Raises:
            AviaryUserError: Invalid channels (`channels` is an empty list)
            AviaryUserError: Invalid time step (`time_step` >= number of time steps)
        """
        if not channels:
            message = (
                'Invalid channels! '
                'channels must be a non-empty list.'
            )
            raise AviaryUserError(message)

        if time_step >= self.num_time_steps:
            message = (
                'Invalid time step! '
                f'time_step must be less than {self.num_time_steps}.'
            )
            raise AviaryUserError(message)

        channels = [
            Channel(channel) if isinstance(channel, str) and channel in self._built_in_channels else channel
            for channel in channels
        ]
        data = [
            self[channel][..., time_step]
            for channel in channels
        ]
        return np.stack(data, axis=-1)

    def to_nir(
        self,
        time_step: TimeStep = 0,
    ) -> npt.NDArray:
        """Converts the tile to near-infrared data.

        Parameters:
            time_step: time step (supports negative indexing)

        Returns:
            near-infrared data
        """
        channels = [
            Channel.NIR,
            Channel.NIR,
            Channel.NIR,
        ]
        return self.to_composite(
            channels=channels,
            time_step=time_step,
        )

    def to_rgb(
        self,
        time_step: TimeStep = 0,
    ) -> npt.NDArray:
        """Converts the data to rgb data.

        Parameters:
            time_step: time step (supports negative indexing)

        Returns:
            rgb data
        """
        channels = [
            Channel.R,
            Channel.G,
            Channel.B,
        ]
        return self.to_composite(
            channels=channels,
            time_step=time_step,
        )

    def to_rgbi(
        self,
        time_step: TimeStep = 0,
    ) -> npt.NDArray:
        """Converts the tile to rgb-infrared data.

        Parameters:
            time_step: time step (supports negative indexing)

        Returns:
            rgb-infrared data
        """
        channels = [
            Channel.R,
            Channel.G,
            Channel.B,
            Channel.NIR,
        ]
        return self.to_composite(
            channels=channels,
            time_step=time_step,
        )
