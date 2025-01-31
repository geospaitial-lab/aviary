from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
)
from typing import TYPE_CHECKING

from aviary.core.bounding_box import BoundingBox
from aviary.core.channel import Channel
from aviary.core.enums import ChannelName

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
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

        self._channel_dict = {channel.name: channel for channel in self._channels}

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

    def __repr__(self) -> str:
        """Returns the string representation.

        Returns:
            string representation
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

    def __len__(self) -> int:
        """Computes the number of channels.

        Returns:
            Number of channels
        """
        return len(self._channels)

    def __iter__(self) -> Iterator[Channel]:
        """Iterates over the channels.

        Yields:
            Channel
        """
        yield from self._channels
