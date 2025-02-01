from __future__ import annotations

import copy
from collections.abc import (
    Iterable,
    Iterator,
)
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import numpy.typing as npt

from aviary.core.bounding_box import BoundingBox
from aviary.core.channel import Channel
from aviary.core.enums import ChannelName
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        BufferSize,
        ChannelNames,
        ChannelNameSet,
        Channels,
        Coordinates,
        TileSize,
    )


class Tile(Iterable[Channel]):
    """A tile specifies the channels and the spatial extent of a tile."""
    _built_in_channel_names = frozenset(channel_name.value for channel_name in ChannelName)

    def __init__(
        self,
        channels: Channels,
        coordinates: Coordinates,
        tile_size: TileSize,
    ) -> None:
        """
        Parameters:
            channels: Channels
            coordinates: Coordinates (x_min, y_min) of the tile
            tile_size: Tile size in meters
        """
        self._channels = channels
        self._coordinates = coordinates
        self._tile_size = tile_size

        self._validate()

        self._channel_dict = {channel.name: channel for channel in self._channels}

    def _validate(self) -> None:
        """Validates the tile."""
        self._validate_channels()
        self._ref_channels()
        self._copy_channels()
        self._validate_tile_size()

    def _validate_channels(self) -> None:
        """Validates `channels`.

        Raises:
            AviaryUserError: Invalid channels (`channels` is an empty list)
            AviaryUserError: Invalid channels (`channels` contains duplicate names)
        """
        if not self._channels:
            message = (
                'Invalid channels! '
                'channels must be a non-empty list.'
            )
            raise AviaryUserError(message)

        channel_names = [channel.name for channel in self._channels]
        unique_channel_names = set(channel_names)

        if len(channel_names) != len(unique_channel_names):
            message = (
                'Invalid channels! '
                'channels must contain unique names.'
            )
            raise AviaryUserError(message)

    def _ref_channels(self) -> None:
        """References the tile in the channels."""
        for channel in self._channels:
            channel.ref_tile(tile=self)

    def _copy_channels(self) -> None:
        """Copies `channels`."""
        self._channels = copy.deepcopy(self._channels)

    def _validate_tile_size(self) -> None:
        """Validates `tile_size`.

        Raises:
            AviaryUserError: Invalid tile size (`tile_size` is negative or zero)
        """
        if self._tile_size <= 0:
            message = (
                'Invalid tile size! '
                'tile_size must be positive.'
            )
            raise AviaryUserError(message)

    @property
    def channels(self) -> Channels:
        """
        Returns:
            Channels
        """
        return self._channels

    @property
    def coordinates(self) -> Coordinates:
        """
        Returns:
            Coordinates (x_min, y_min) of the tile
        """
        return self._coordinates

    @property
    def tile_size(self) -> TileSize:
        """
        Returns:
            Tile size in meters
        """
        return self._tile_size

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
        x_min, y_min = self._coordinates
        x_max = x_min + self._tile_size
        y_max = y_min + self._tile_size
        return BoundingBox(
            x_min=x_min,
            y_min=y_min,
            x_max=x_max,
            y_max=y_max,
        )

    @property
    def channel_names(self) -> ChannelNameSet:
        """
        Returns:
            Channel names
        """
        return set(self._channel_dict.keys())

    @property
    def num_channels(self) -> int:
        """
        Returns:
            Number of channels
        """
        return len(self)

    @classmethod
    def from_composite_array(
        cls,
        data: npt.NDArray,
        channel_names: ChannelNames,
        coordinates: Coordinates,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
    ) -> Tile:
        """Creates a tile from a composite array.

        Parameters:
            data: Data
            channel_names: Channel names
            coordinates: Coordinates (x_min, y_min) of the tile
            tile_size: Tile size in meters
            buffer_size: Buffer size in meters

        Returns:
            Tile

        Raises:
            AviaryUserError: Invalid data (`data` is not an array of shape (n, n, c))
            AviaryUserError: Invalid channel names (the number of channel names is not equal to the number of channels)
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

        if data.shape[-1] != len(channel_names):
            message = (
                'Invalid channel names! '
                'The number of channel names must be equal to the number of channels.'
            )
            raise AviaryUserError(message)

        channel_names = [
            ChannelName(channel_name)
            if isinstance(channel_name, str) and channel_name in cls._built_in_channel_names else channel_name
            for channel_name in channel_names
        ]
        channels = [
            Channel(
                data=data[..., i],
                name=channel_name,
                buffer_size=buffer_size,
            )
            for i, channel_name in channel_names
        ]
        return cls(
            channels=channels,
            coordinates=coordinates,
            tile_size=tile_size,
        )

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        channels_repr = '\n'.join(
            f'        {channel.name}: {channel.data_type},'
            for channel in self
        )
        return (
            'Tile(\n'
            f'    channels=\n{channels_repr}\n'
            f'    coordinates={self._coordinates},\n'
            f'    tile_size={self._tile_size},\n'
            ')'
        )

    def __eq__(
        self,
        other: Tile,
    ) -> bool:
        """Compares the tiles.

        Parameters:
            other: Other tile

        Returns:
            True if the tiles are equal, false otherwise
        """
        if not isinstance(other, Tile):
            return False

        conditions = (
            self._channels == other._channels,
            self._coordinates == other._coordinates,
            self._tile_size == other._tile_size,
        )
        return all(conditions)

    def __len__(self) -> int:
        """Computes the number of channels.

        Returns:
            Number of channels
        """
        return len(self._channels)

    def __getattr__(
        self,
        channel_name: str,
    ) -> Channel:
        """Returns the channel.

        Parameters:
            channel_name: Channel name

        Returns:
            Channel

        Raises:
            AviaryUserError: Invalid channel name (the channel is not available)
        """
        if channel_name in self._built_in_channel_names:
            channel_name = ChannelName(channel_name)

        if channel_name not in self.channel_names:
            message = (
                'Invalid channel name! '
                f'The {channel_name} channel is not available.'
            )
            raise AviaryUserError(message)

        return self[channel_name]

    def __getitem__(
        self,
        channel_name: ChannelName | str,
    ) -> Channel:
        """Returns the channel.

        Parameters:
            channel_name: Channel name

        Returns:
            Channel

        Raises:
            AviaryUserError: Invalid channel name (the channel is not available)
        """
        if isinstance(channel_name, str) and channel_name in self._built_in_channel_names:
            channel_name = ChannelName(channel_name)

        if channel_name not in self.channel_names:
            message = (
                'Invalid channel name! '
                f'The {channel_name} channel is not available.'
            )
            raise AviaryUserError(message)

        return self._channel_dict[channel_name]

    def __iter__(self) -> Iterator[Channel]:
        """Iterates over the channels.

        Yields:
            Channel
        """
        yield from self._channels
