from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pydantic

# noinspection PyProtectedMember
from aviary._functional.tile.tiles_exporter import (
    grid_exporter,
    vector_exporter,
)
from aviary.core.enums import ChannelName
from aviary.core.type_aliases import (
    ChannelKey,
    EPSGCode,
)
from aviary.tile.tiles_processor import _TilesProcessorFactory

if TYPE_CHECKING:
    from aviary.core.tiles import Tiles

_PACKAGE = 'aviary'


class GridExporter:
    """Tiles processor that exports the grid of the tiles

    The grid is exported to a JSON file. The JSON string contains a list of coordinates (x_min, y_min)
    of each tile and the tile size.

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

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        dir_path: 'path/to/my/directory'
        json_name: 'processed_grid.json'
        ```

    Attributes:
        dir_path: Path to the directory
        json_name: Name of the JSON file (.json file)
    """
    dir_path: Path
    json_name: str


_TilesProcessorFactory.register(
    tiles_processor_class=GridExporter,
    config_class=GridExporterConfig,
    package=_PACKAGE,
)


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
        epsg_code: EPSGCode | None,
        dir_path: Path,
        gpkg_name: str,
        remove_channel: bool = True,
    ) -> None:
        """
        Parameters:
            channel_key: Channel name or channel name and time step combination
            epsg_code: EPSG code
            dir_path: Path to the directory
            gpkg_name: Name of the geopackage (.gpkg file)
            remove_channel: If True, the channel is removed
        """
        self._channel_key = channel_key
        self._epsg_code = epsg_code
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
            epsg_code=self._epsg_code,
            dir_path=self._dir_path,
            gpkg_name=self._gpkg_name,
            remove_channel=self._remove_channel,
        )


class VectorExporterConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VectorExporter`

    Create the configuration from a config file:
        - Use null instead of None
        - Use false or true instead of False or True

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        channel_key: 'my_channel'
        epsg_code: 25832
        dir_path: 'path/to/my/directory'
        gpkg_name: 'my_channel.gpkg'
        remove_channel: true
        ```

    Attributes:
        channel_key: Channel name or channel name and time step combination
        epsg_code: EPSG code
        dir_path: Path to the directory
        gpkg_name: Name of the geopackage (.gpkg file)
        remove_channel: If True, the channel is removed -
            defaults to True
    """
    channel_key: ChannelName | str | ChannelKey
    epsg_code: EPSGCode | None
    dir_path: Path
    gpkg_name: str
    remove_channel: bool = True


_TilesProcessorFactory.register(
    tiles_processor_class=VectorExporter,
    config_class=VectorExporterConfig,
    package=_PACKAGE,
)
