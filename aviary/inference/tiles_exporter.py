from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pydantic

# noinspection PyProtectedMember
from aviary._functional.inference.tiles_exporter import (
    grid_exporter,
    vector_exporter,
)
from aviary.core.enums import ChannelName
from aviary.core.type_aliases import (
    ChannelKey,
)

if TYPE_CHECKING:
    from aviary.core.tiles import Tiles


class GridExporter:
    """Tiles processor that exports the grid of the tiles

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        dir_path: Path,
        json_name: str,
    ) -> None:
        """
        Parameters:
            dir_path: Path to the directory
            json_name: Name of the JSON file (.json file)
        """
        self._dir_path = dir_path
        self._json_name = json_name

    @classmethod
    def from_config(
        cls,
        config: GridExporterConfig,
    ) -> GridExporter:
        """Creates a grid exporter from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Grid exporter
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Exports the grid of the tiles.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return grid_exporter(
            tiles=tiles,
            dir_path=self._dir_path,
            json_name=self._json_name,
        )


class GridExporterConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `GridExporter`

    Attributes:
        dir_path: Path to the directory
        json_name: Name of the JSON file (.json file)
    """
    dir_path: Path
    json_name: str


class VectorExporter:
    """Tiles processor that exports a vector channel

    The vector data is exported to a geopackage.

    Notes:
        - Exporting a channel by its name assumes the time step is None
        - Requires a vector channel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_key: ChannelName | str | ChannelKey,
        dir_path: Path,
        gpkg_name: str,
        remove_channel: bool = True,
    ) -> None:
        """
        Parameters:
            channel_key: Channel name or channel name and time step combination
            dir_path: Path to the directory
            gpkg_name: Name of the geopackage (.gpkg file)
            remove_channel: If True, the channel is removed
        """
        self._channel_key = channel_key
        self._dir_path = dir_path
        self._gpkg_name = gpkg_name
        self._remove_channel = remove_channel

    @classmethod
    def from_config(
        cls,
        config: VectorExporterConfig,
    ) -> VectorExporter:
        """Creates a vector exporter from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Vector exporter
        """
        config = config.model_dump()
        return cls(**config)

    def __call__(
        self,
        tiles: Tiles,
    ) -> Tiles:
        """Exports the vector channel.

        Parameters:
            tiles: Tiles

        Returns:
            Tiles
        """
        return vector_exporter(
            tiles=tiles,
            channel_key=self._channel_key,
            dir_path=self._dir_path,
            gpkg_name=self._gpkg_name,
            remove_channel=self._remove_channel,
        )


class VectorExporterConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VectorExporter`

    Attributes:
        channel_key: Channel name or channel name and time step combination
        dir_path: Path to the directory
        gpkg_name: Name of the geopackage (.gpkg file)
        remove_channel: If True, the channel is removed -
            defaults to True
    """
    channel_key: ChannelName | str | ChannelKey
    dir_path: Path
    gpkg_name: str
    remove_channel: bool = True
