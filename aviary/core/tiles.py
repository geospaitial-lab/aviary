from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
)
from typing import (
    TYPE_CHECKING,
    TypeAlias,
)

import numpy as np

if TYPE_CHECKING:
    import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.utils.coordinates_filter import duplicates_filter
from aviary.core.channel import (
    Channel,
    RasterChannel,
    _parse_channel_name,
)
from aviary.core.exceptions import AviaryUserError
from aviary.core.grid import Grid
from aviary.core.type_aliases import (
    ChannelKey,
    ChannelNameSet,
    CoordinatesSet,
    _parse_channel_key,
    _parse_channel_keys,
)

if TYPE_CHECKING:
    from aviary.core.enums import ChannelName
    from aviary.core.type_aliases import (
        BufferSize,
        ChannelKeySet,
        ChannelNameKeySet,
        Coordinates,
        TileSize,
        TimeStep,
    )


class Tiles(Iterable[Channel]):
    """The tiles specify the channels and their spatial extent.

    Notes:
        - The type alias `Tile` can be used for semantic consistency if it specifies a single tile
            instead of a batch of tiles
        - The `channels` property returns a reference to the channels
        - The dunder methods `__getattr__`, `__getitem__`, and `__iter__` return or yield a reference to a channel
    """
    _coordinates: CoordinatesSet

    def __init__(
        self,
        channels: list[Channel],
        coordinates: Coordinates | CoordinatesSet,
        tile_size: TileSize,
        copy: bool = False,
    ) -> None:
        """
        Parameters:
            channels: Channels
            coordinates: Coordinates (x_min, y_min) of the tile or of each tile in meters
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
        """Validates the tiles."""
        self._validate_channels()
        self._parse_coordinates()
        self._validate_coordinates()
        self._validate_tile_size()

    def _validate_channels(self) -> None:
        """Validates `channels`.

        Raises:
            AviaryUserError: Invalid `channels` (the channels contain no channels)
            AviaryUserError: Invalid `channels` (the channels contain duplicate channel name and time step combinations)
            AviaryUserError: Invalid `channels` (the batch sizes of the channels are not equal)
        """
        if not self._channels:
            message = (
                'Invalid channels! '
                'The channels must contain at least one channel.'
            )
            raise AviaryUserError(message)

        channel_keys = [channel.key for channel in self]
        unique_channel_keys = set(channel_keys)

        if len(channel_keys) != len(unique_channel_keys):
            message = (
                'Invalid channels! '
                'The channels must contain unique channel name and time step combinations.'
            )
            raise AviaryUserError(message)

        batch_sizes = {channel.batch_size for channel in self}

        if len(batch_sizes) > 1:
            message = (
                'Invalid channels! '
                'The batch sizes of the channels must be equal.'
            )
            raise AviaryUserError(message)

    def _copy_channels(self) -> None:
        """Copies `channels`."""
        self._channels = [channel.copy() for channel in self]

    def _mark_as_copied(self) -> None:
        """Sets `_copy` to True if the channels are copied before the initialization."""
        self._copy = True

    def _parse_coordinates(self) -> None:
        """Parses `coordinates`."""
        if not isinstance(self._coordinates, np.ndarray):
            self._coordinates = np.array([self._coordinates], dtype=np.int32)

    def _validate_coordinates(self) -> None:
        """Validates `coordinates`.

        Raises:
            AviaryUserError: Invalid `coordinates` (the coordinates are not in shape (n, 2) and data type int32)
            AviaryUserError: Invalid `coordinates` (the coordinates contain duplicate coordinates)
            AviaryUserError: Invalid `coordinates` (the number of coordinates is not equal to the batch size
                of the channels)
        """
        if self._coordinates.ndim != 2:  # noqa: PLR2004
            message = (
                'Invalid coordinates! '
                'The coordinates must be in shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        conditions = [
            self._coordinates.shape[1] != 2,  # noqa: PLR2004
            self._coordinates.dtype != np.int32,
        ]

        if any(conditions):
            message = (
                'Invalid coordinates! '
                'The coordinates must be in shape (n, 2) and data type int32.'
            )
            raise AviaryUserError(message)

        unique_coordinates = duplicates_filter(coordinates=self._coordinates)

        if len(self._coordinates) != len(unique_coordinates):
            message = (
                'Invalid coordinates! '
                'The coordinates must contain unique coordinates.'
            )
            raise AviaryUserError(message)

        first_channel = self._channels[0]

        if len(self._coordinates) != first_channel.batch_size:
            message = (
                'Invalid coordinates! '
                'The number of coordinates must be equal to the batch size of the channels.'
            )
            raise AviaryUserError(message)

        self._coordinates = self._coordinates.copy()

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

    @property
    def channels(self) -> list[Channel]:
        """
        Returns:
            Channels
        """
        return self._channels

    @property
    def coordinates(self) -> Coordinates | CoordinatesSet:
        """
        Returns:
            Coordinates (x_min, y_min) of the tile or of each tile in meters
        """
        if self.batch_size == 1:
            x_min, y_min = self._coordinates[0]
            return int(x_min), int(y_min)

        return self._coordinates.copy()

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
        return self.grid.area

    @property
    def batch_size(self) -> int:
        """
        Returns:
            Batch size
        """
        return len(self._coordinates)

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
    def grid(self) -> Grid:
        """
        Returns:
            Grid
        """
        return Grid(
            coordinates=self._coordinates,
            tile_size=self._tile_size,
        )

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
        channel_names: list[ChannelName | str | None],
        coordinates: Coordinates,
        tile_size: TileSize,
        buffer_size: BufferSize = 0,
        time_step: TimeStep | None = None,
        copy: bool = False,
    ) -> Tiles:
        """Creates tiles from composite raster data.

        Parameters:
            data: Data
            channel_names: Channel names (if None, the channel is ignored)
            coordinates: Coordinates (x_min, y_min) of the tile in meters
            tile_size: Tile size in meters
            buffer_size: Buffer size in meters
            time_step: Time step
            copy: If True, the channels are copied during initialization

        Returns:
            Tiles

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

        channel_names = [
            _parse_channel_name(channel_name=channel_name)
            for channel_name in channel_names
        ]
        channels_dict = {}
        buffer_size = buffer_size / tile_size

        for i, channel_name in enumerate(channel_names):
            if channel_name is None:
                continue

            if channel_name in channels_dict:
                continue

            channels_dict[channel_name] = RasterChannel(
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
        tiles: list[Tiles],
        copy: bool = False,
    ) -> Tiles:
        """Creates tiles from tiles.

        Parameters:
            tiles: Tiles
            copy: If True, the channels are copied during initialization

        Returns:
            Tiles

        Raises:
            AviaryUserError: Invalid `tiles` (the tiles contain no tiles)
            AviaryUserError: Invalid `tiles` (the tile sizes of the tiles are not equal)
            AviaryUserError: Invalid `tiles` (the channel name and time step combinations of the tiles are not equal)
            AviaryUserError: Invalid `tiles` (the coordinates of the tiles do not contain equal or unique coordinates)
        """
        if not tiles:
            message = (
                'Invalid tiles! '
                'The tiles must contain at least one tile.'
            )
            raise AviaryUserError(message)

        tile_sizes = {tile.tile_size for tile in tiles}

        if len(tile_sizes) > 1:
            message = (
                'Invalid tiles! '
                'The tile sizes of the tiles must be equal.'
            )
            raise AviaryUserError(message)

        first_tile = tiles[0]

        coordinates_equal = all(
            np.array_equal(tile._coordinates, first_tile._coordinates)  # noqa: SLF001
            for tile in tiles
        )

        if coordinates_equal:
            channels = [channel for tile in tiles for channel in tile]
            coordinates = first_tile._coordinates  # noqa: SLF001
            tile_size = first_tile.tile_size
            return cls(
                channels=channels,
                coordinates=coordinates,
                tile_size=tile_size,
                copy=copy,
            )

        coordinates = np.concatenate([tile._coordinates for tile in tiles], axis=0)  # noqa: SLF001
        unique_coordinates = duplicates_filter(coordinates=coordinates)
        coordinates_unique = len(coordinates) == len(unique_coordinates)

        if coordinates_unique:
            channel_keys_equal = all(
                tile.channel_keys == first_tile.channel_keys
                for tile in tiles
            )

            if not channel_keys_equal:
                message = (
                    'Invalid tiles! '
                    'The channel name and time step combinations of the tiles must be equal.'
                )
                raise AviaryUserError(message)

            channels = [
                first_tile[channel_key].__class__.from_channels(
                    channels=[tile[channel_key] for tile in tiles],
                    copy=False,
                )
                for channel_key in first_tile.channel_keys
            ]
            tile_size = first_tile.tile_size
            return cls(
                channels=channels,
                coordinates=coordinates,
                tile_size=tile_size,
                copy=copy,
            )

        message = (
            'Invalid tiles! '
            'The coordinates of the tiles must contain equal or unique coordinates.'
        )
        raise AviaryUserError(message)

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            String representation
        """
        channels_repr = '\n'.join(
            f'        {channel.key}: {type(channel).__name__},'
            for channel in self
        )
        channels_repr = '\n' + channels_repr
        coordinates_repr = len(self._coordinates)
        return (
            'Tiles(\n'
            f'    channels={channels_repr}\n'
            f'    coordinates={coordinates_repr},\n'
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
        other: object,
    ) -> bool:
        """Compares the tiles.

        Parameters:
            other: Other tiles

        Returns:
            True if the tiles are equal, False otherwise
        """
        if not isinstance(other, Tiles):
            return False

        conditions = (
            self._channels == other.channels,
            np.array_equal(self._coordinates, other._coordinates),
            self._tile_size == other.tile_size,
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
        """Checks if the channel is in the tiles.

        Notes:
            - Accessing a channel by its name assumes the time step is None

        Parameters:
            channel_key: Channel name or channel name and time step combination

        Returns:
            True if the channel is in the tiles, False otherwise
        """
        channel_key = _parse_channel_key(channel_key=channel_key)
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
        except KeyError as error:
            raise AttributeError from error

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
        channel_key = _parse_channel_key(channel_key=channel_key)
        return self._channels_dict[channel_key]

    def __iter__(self) -> Iterator[Channel]:
        """Iterates over the channels.

        Yields:
            Channel
        """
        yield from self._channels

    def __add__(
        self,
        other: Tiles,
    ) -> Tiles:
        """Adds the tiles.

        Parameters:
            other: Other tiles

        Returns:
            Tiles

        Raises:
            AviaryUserError: Invalid `other` (the tile sizes of the tiles are not equal)
            AviaryUserError: Invalid `other` (the channel name and time step combinations of the tiles are not equal)
            AviaryUserError: Invalid `other` (the coordinates of the tiles do not contain equal or unique coordinates)
        """
        if self._tile_size != other.tile_size:
            message = (
                'Invalid other! '
                'The tile sizes of the tiles must be equal.'
            )
            raise AviaryUserError(message)

        coordinates_equal = np.array_equal(self._coordinates, other._coordinates)

        if coordinates_equal:
            channels = self._channels + other.channels
            return Tiles(
                channels=channels,
                coordinates=self._coordinates,
                tile_size=self._tile_size,
                copy=True,
            )

        coordinates = np.concatenate([self._coordinates, other._coordinates], axis=0)
        unique_coordinates = duplicates_filter(coordinates=coordinates)
        coordinates_unique = len(coordinates) == len(unique_coordinates)

        if coordinates_unique:
            if self.channel_keys != other.channel_keys:
                message = (
                    'Invalid other! '
                    'The channel name and time step combinations of the tiles must be equal.'
                )
                raise AviaryUserError(message)

            channels = [
                self[channel_key] + other[channel_key]
                for channel_key in self.channel_keys
            ]
            tiles = Tiles(
                channels=channels,
                coordinates=coordinates,
                tile_size=self._tile_size,
                copy=False,
            )
            tiles._mark_as_copied()
            return tiles

        message = (
            'Invalid other! '
            'The coordinates of the tiles must contain equal or unique coordinates.'
        )
        raise AviaryUserError(message)

    def append(
        self,
        channels: Channel | list[Channel],
        inplace: bool = False,
    ) -> Tiles:
        """Appends the channels.

        Parameters:
            channels: Channels
            inplace: If True, the channels are appended inplace

        Returns:
            Tiles
        """
        if not isinstance(channels, list):
            channels = [channels]

        if inplace:
            self._channels.extend(channels)
            self._validate()
            self._channels_dict = self._compute_channels_dict()
            return self

        channels = self._channels + channels
        return Tiles(
            channels=channels,
            coordinates=self._coordinates,
            tile_size=self._tile_size,
            copy=True,
        )

    def copy(self) -> Tiles:
        """Copies the tiles.

        Returns:
            Tiles
        """
        return Tiles(
            channels=self._channels,
            coordinates=self._coordinates,
            tile_size=self._tile_size,
            copy=True,
        )

    def remove(
        self,
        channel_keys:
            ChannelName | str |
            ChannelKey |
            ChannelNameSet | ChannelKeySet | ChannelNameKeySet,
        inplace: bool = False,
    ) -> Tiles:
        """Removes the channels.

        Notes:
            - Removing a channel by its name assumes the time step is None

        Parameters:
            channel_keys: Channel name, channel name and time step combination, channel names,
                or channel name and time step combinations
            inplace: If True, the channels are removed inplace

        Returns:
            Tiles
        """
        channel_keys = _parse_channel_keys(channel_keys=channel_keys)

        if inplace:
            self._channels = [channel for channel in self if channel.key not in channel_keys]
            self._validate()
            self._channels_dict = self._compute_channels_dict()
            return self

        tiles = self.copy()
        tiles._channels = [channel for channel in tiles if channel.key not in channel_keys]  # noqa: SLF001
        tiles._validate()  # noqa: SLF001
        tiles._channels_dict = tiles._compute_channels_dict()  # noqa: SLF001
        return tiles

    def remove_buffer(
        self,
        ignore_channel_keys:
            ChannelName | str |
            ChannelKey |
            ChannelNameSet | ChannelKeySet | ChannelNameKeySet |
            None = None,
        inplace: bool = False,
    ) -> Tiles:
        """Removes the buffer.

        Notes:
            - Ignoring a channel by its name assumes the time step is None

        Parameters:
            ignore_channel_keys: Channel name, channel name and time step combination, channel names,
                or channel name and time step combinations to ignore
            inplace: If True, the buffer is removed inplace

        Returns:
            Tiles
        """
        ignore_channel_keys = _parse_channel_keys(channel_keys=ignore_channel_keys)

        if inplace:
            for channel in self:
                if channel.key not in ignore_channel_keys:
                    channel.remove_buffer(inplace=True)

            self._validate()
            return self

        tiles = self.copy()

        for channel in tiles:
            if channel.key not in ignore_channel_keys:
                channel.remove_buffer(inplace=True)

        tiles._validate()  # noqa: SLF001
        return tiles


Tile: TypeAlias = Tiles
