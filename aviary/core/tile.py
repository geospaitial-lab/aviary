from __future__ import annotations

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
        TimeStep,
    )


class Tile(Iterable[Channel]):
    """A tile specifies the channels and the spatial extent of a tile.

    Notes:
        - The `channels` property returns a reference to the channels
        - The dunder methods `__getattr__`, `__getitem__`, and `__iter__` return or yield a reference to a channel
    """
    _built_in_channel_names = frozenset(channel_name.value for channel_name in ChannelName)

    def __init__(
        self,
        channels: Channels,
        coordinates: Coordinates,
        tile_size: TileSize,
        copy: bool = False,
    ) -> None:
        """
        Parameters:
            channels: Channels
            coordinates: Coordinates (x_min, y_min) of the tile in meters
            tile_size: Tile size in meters
            copy: If true, the channels are copied during initialization
        """
        self._channels = channels
        self._coordinates = coordinates
        self._tile_size = tile_size
        self._copy = copy

        self._validate()

        if self._copy:
            self._copy_channels()

        self._channels_dict = {channel.name: channel for channel in self._channels}

    def _validate(self) -> None:
        """Validates the tile."""
        self._validate_channels()
        self._validate_tile_size()

    def _validate_channels(self) -> None:
        """Validates `channels`.

        Raises:
            AviaryUserError: Invalid `channels` (the channels contain duplicate names)
        """
        channel_names = [channel.name for channel in self._channels]
        unique_channel_names = set(channel_names)

        if len(channel_names) != len(unique_channel_names):
            message = (
                'Invalid channels! '
                'The channels must contain unique names.'
            )
            raise AviaryUserError(message)

    def _copy_channels(self) -> None:
        """Copies `channels`."""
        self._channels = [channel.copy() for channel in self._channels]

    def _validate_tile_size(self) -> None:
        """Validates `tile_size`.

        Raises:
            AviaryUserError: Invalid `tile_size` (the tile size is negative or zero)
        """
        if self._tile_size <= 0:
            message = (
                'Invalid tile_size! '
                'The tile size must be positive.'
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
            Coordinates (x_min, y_min) of the tile in meters
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
        return set(self._channels_dict.keys())

    @property
    def num_channels(self) -> int:
        """
        Returns:
            Number of channels
        """
        return len(self)

    @classmethod
    def from_composite_raster(
        cls,
        data: npt.NDArray,
        channel_names: ChannelNames,
        coordinates: Coordinates,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
        time_step: TimeStep | None = None,
        copy: bool = False,
    ) -> Tile:
        """Creates a tile from composite raster data.

        Parameters:
            data: Data
            channel_names: Channel names
            coordinates: Coordinates (x_min, y_min) of the tile in meters
            tile_size: Tile size in meters
            buffer_size: Buffer size in meters
            time_step: Time step
            copy: If true, the channels are copied during initialization

        Returns:
            Tile

        Raises:
            AviaryUserError: Invalid `data` (the data is not in shape (n, n, c))
            AviaryUserError: Invalid `channel_names` (the number of channel names is not equal to
                the number of channels)
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
                'The data must be in shape (n, n, c).'
            )
            raise AviaryUserError(message)

        if data.shape[-1] != len(channel_names):
            message = (
                'Invalid channel_names! '
                'The number of channel names must be equal to the number of channels.'
            )
            raise AviaryUserError(message)

        channel_names = [
            ChannelName(channel_name)
            if isinstance(channel_name, str) and channel_name in cls._built_in_channel_names else channel_name
            for channel_name in channel_names
        ]

        channels_dict = {}

        buffer_size = buffer_size / tile_size

        for i, channel_name in enumerate(channel_names):
            if channel_name not in channels_dict:
                channels_dict[channel_name] = Channel(
                    data=data[..., i],
                    name=channel_name,
                    buffer_size=buffer_size,
                    time_step=time_step,
                    copy=False,
                )

        channels = list(channels_dict.values())
        return cls(
            channels=channels,
            coordinates=coordinates,
            tile_size=tile_size,
            copy=copy,
        )

    @classmethod
    def from_tiles(
        cls,
        tiles: list[Tile],
        copy: bool = False,
    ) -> Tile:
        """Creates a tile from tiles.

        Parameters:
            tiles: Tiles
            copy: If true, the channels are copied during initialization

        Returns:
            Tile

        Raises:
            AviaryUserError: Invalid `tiles` (the tiles are empty)
            AviaryUserError: Invalid `tiles` (the coordinates and tile sizes of the tiles are not equal)
        """
        if not tiles:
            message = (
                'Invalid tiles! '
                'The tiles must contain at least one tile.'
            )
            raise AviaryUserError(message)

        first_tile = tiles[0]
        coordinates = first_tile.coordinates
        tile_size = first_tile.tile_size

        for tile in tiles:
            conditions = [
                tile.coordinates != coordinates,
                tile.tile_size != tile_size,
            ]

            if any(conditions):
                message = (
                    'Invalid tiles! '
                    'The coordinates and tile sizes of the tiles must be equal.'
                )
                raise AviaryUserError(message)

        channels = [channel for tile in tiles for channel in tile]
        return cls(
            channels=channels,
            coordinates=coordinates,
            tile_size=tile_size,
            copy=copy,
        )

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        if self.channels:
            channels_repr = '\n'.join(
                f'        {channel.name}: {type(channel).__name__},'
                for channel in self
            )
            channels_repr = '\n' + channels_repr
        else:
            channels_repr = ','
        return (
            'Tile(\n'
            f'    channels={channels_repr}\n'
            f'    coordinates={self._coordinates},\n'
            f'    tile_size={self._tile_size},\n'
            f'    copy={self._copy},\n'
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
        """
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
            AviaryUserError: Invalid `channel_name` (the channel is not available)
        """
        if isinstance(channel_name, str) and channel_name in self._built_in_channel_names:
            channel_name = ChannelName(channel_name)

        if channel_name not in self.channel_names:
            message = (
                'Invalid channel_name! '
                f'The {channel_name} channel is not available.'
            )
            raise AviaryUserError(message)

        return self._channels_dict[channel_name]

    def __iter__(self) -> Iterator[Channel]:
        """Iterates over the channels.

        Yields:
            Channel
        """
        yield from self._channels

    def copy(self) -> Tile:
        """Copies the tile.

        Returns:
            Tile
        """
        return Tile(
            channels=self._channels,
            coordinates=self._coordinates,
            tile_size=self._tile_size,
            copy=True,
        )
