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
from aviary.core.type_aliases import (
    ChannelKey,
    ChannelNameSet,
    _is_channel_key,
)

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        BufferSize,
        ChannelKeySet,
        ChannelNameKeySet,
        ChannelNames,
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
            copy: If True, the channels are copied during initialization
        """
        self._channels = channels
        self._coordinates = coordinates
        self._tile_size = tile_size
        self._copy = copy

        self._validate()

        if self._copy:
            self._copy_channels()

        self._channels_dict = self._compute_channels_dict()

    def _validate(self) -> None:
        """Validates the tile."""
        self._validate_channels()
        self._validate_tile_size()

    def _validate_channels(self) -> None:
        """Validates `channels`.

        Raises:
            AviaryUserError: Invalid `channels` (the channels contain duplicate channel name and time step combinations)
        """
        channel_keys = [channel.key for channel in self._channels]
        unique_channel_keys = set(channel_keys)

        if len(channel_keys) != len(unique_channel_keys):
            message = (
                'Invalid channels! '
                'The channels must contain unique channel name and time step combinations.'
            )
            raise AviaryUserError(message)

    def _copy_channels(self) -> None:
        """Copies `channels`."""
        self._channels = [channel.copy() for channel in self._channels]

    def _mark_as_copied(self) -> None:
        """Sets `_copy` to True if the channels are copied before the initialization."""
        self._copy = True

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

    def _compute_channels_dict(self) -> dict[ChannelKey, Channel]:
        """Computes the channels dictionary.

        Returns:
            Channels dictionary
        """
        return {channel.key: channel for channel in self._channels}

    def _parse_channel_name(
        self,
        channel_name: ChannelName | str,
    ) -> ChannelName:
        """Parses `channel_name` to `ChannelName`.

        Parameters:
            channel_name: Channel name

        Returns:
            Channel name
        """
        if isinstance(channel_name, str) and channel_name in self._built_in_channel_names:
            return ChannelName(channel_name)
        return channel_name

    def _parse_channel_key(
        self,
        channel_key: ChannelName | str | ChannelKey,
    ) -> ChannelKey:
        """Parses `channel_key` to `ChannelKey`.

        Parameters:
            channel_key: Channel name or channel name and time step combination

        Returns:
            Channel name and time step combination
        """
        if _is_channel_key(channel_key):
            channel_name, time_step = channel_key
        else:
            channel_name = channel_key
            time_step = None

        channel_name = self._parse_channel_name(channel_name=channel_name)
        return channel_name, time_step

    def _parse_channel_keys(
        self,
        channel_keys:
            ChannelName | str |
            ChannelKey |
            ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
            None,
    ) -> ChannelKeySet:
        """Parses `channel_keys` to `ChannelKeySet`.

        Parameters:
            channel_keys: Channel name, channel name and time step combination, channel names,
                or channel name and time step combinations to ignore

        Returns:
            Channel name and time step combinations
        """
        if channel_keys is None:
            return set()

        if isinstance(channel_keys, (ChannelName | str)) or _is_channel_key(channel_keys):
            return set(self._parse_channel_key(channel_key=channel_keys))

        return {
            self._parse_channel_key(channel_key=channel_key)
            for channel_key in channel_keys
        }

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
    def is_copied(self) -> bool:
        """
        Returns:
            If True, the channels are copied during initialization
        """
        return self._copy

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
    def channel_keys(self) -> ChannelKeySet:
        """
        Returns:
            Channel name and time step combinations
        """
        return {channel.key for channel in self}

    @property
    def channel_names(self) -> ChannelNameSet:
        """
        Returns:
            Channel names
        """
        return {channel.name for channel in self}

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
            copy: If True, the channels are copied during initialization

        Returns:
            Tile

        Raises:
            AviaryUserError: Invalid `data` (the data is not in shape (n, n, c))
            AviaryUserError: Invalid `channel_names` (the number of channel names is not equal to
                the number of channels)
        """
        if data.ndim == 2:  # noqa: PLR2004
            data = data[..., np.newaxis]

        if data.ndim != 3:  # noqa: PLR2004
            message = (
                'Invalid data! '
                'The data must be in shape (n, n, c).'
            )
            raise AviaryUserError(message)

        if data.shape[0] != data.shape[1]:
            message = (
                'Invalid data! '
                'The data must be in shape (n, n, c).'
            )
            raise AviaryUserError(message)

        if len(channel_names) != data.shape[-1]:
            message = (
                'Invalid channel_names! '
                'The number of channel names must be equal to the number of channels.'
            )
            raise AviaryUserError(message)

        if copy:
            data = data.copy()

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
        tile = cls(
            channels=channels,
            coordinates=coordinates,
            tile_size=tile_size,
            copy=False,
        )

        if copy:
            tile._mark_as_copied()  # noqa: SLF001

        return tile

    @classmethod
    def from_tiles(
        cls,
        tiles: list[Tile],
        copy: bool = False,
    ) -> Tile:
        """Creates a tile from tiles that specify the same spatial extent.

        Parameters:
            tiles: Tiles
            copy: If True, the channels are copied during initialization

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
                f'        {channel.key}: {type(channel).__name__},'
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

    def __getstate__(self) -> dict:
        """Gets the state for pickling.

        Returns:
            State
        """
        return self.__dict__

    def __setstate__(
        self,
        state: dict,
    ) -> None:
        """Sets the state for unpickling.

        Parameters:
            state: State
        """
        self.__dict__ = state

    def __eq__(
        self,
        other: Tile,
    ) -> bool:
        """Compares the tiles.

        Parameters:
            other: Other tile

        Returns:
            True if the tiles are equal, False otherwise
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

    def __contains__(
        self,
        channel_key: ChannelName | str | ChannelKey,
    ) -> bool:
        """Checks if the channel is in the tile.

        Notes:
            - Accessing a channel by its name assumes the time step is None

        Parameters:
            channel_key: Channel name or channel name and time step combination

        Returns:
            True if the channel is in the tile, False otherwise
        """
        channel_key = self._parse_channel_key(channel_key=channel_key)
        return channel_key in self.channel_keys

    def __getattr__(
        self,
        channel_name: str,
    ) -> Channel:
        """Returns the channel.

        Notes:
            - Accessing a channel by its name assumes the time step is None

        Parameters:
            channel_name: Channel name

        Returns:
            Channel
        """
        try:
            return self[channel_name]
        except KeyError:
            # noinspection PyUnresolvedReferences
            return super().__getattr__(channel_name)

    def __getitem__(
        self,
        channel_key: ChannelName | str | ChannelKey,
    ) -> Channel:
        """Returns the channel.

        Notes:
            - Accessing a channel by its name assumes the time step is None

        Parameters:
            channel_key: Channel name or channel name and time step combination

        Returns:
            Channel
        """
        channel_key = self._parse_channel_key(channel_key=channel_key)
        return self._channels_dict[channel_key]

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

    def remove_buffer(
        self,
        ignore_channel_keys:
            ChannelName | str |
            ChannelKey |
            ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
            None = None,
        inplace: bool = False,
    ) -> Tile:
        """Removes the buffer.

        Notes:
            - Ignoring a channel by its name assumes the time step is None

        Parameters:
            ignore_channel_keys: Channel name, channel name and time step combination, channel names,
                or channel name and time step combinations to ignore
            inplace: If True, the buffer is removed inplace

        Returns:
            Tile
        """
        ignore_channel_keys = self._parse_channel_keys(channel_keys=ignore_channel_keys)

        if inplace:
            for channel in self:
                if channel.key not in ignore_channel_keys:
                    channel.remove_buffer(inplace=True)

            self._validate()
            return self

        tile = self.copy()

        for channel in tile:
            if channel.key not in ignore_channel_keys:
                channel.remove_buffer(inplace=True)

        return tile
