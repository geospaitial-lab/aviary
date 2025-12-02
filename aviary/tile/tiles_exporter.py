#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pydantic

from aviary._functional.tile.tiles_exporter import (
    grid_exporter,
    vector_exporter,
)
from aviary.core.enums import ChannelName
from aviary.core.type_aliases import EPSGCode
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
        path: Path,
    ) -> None:
        """
        Parameters:
            path: Path to the JSON file (.json file)
        """
        self._path = path

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
            path=self._path,
        )


class GridExporterConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `GridExporter`

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'GridExporter'
        config:
          path: 'path/to/my_processed_grid.json'
        ```

    Attributes:
        path: Path to the JSON file (.json file)
    """
    path: Path


_TilesProcessorFactory.register(
    tiles_processor_class=GridExporter,
    config_class=GridExporterConfig,
    package=_PACKAGE,
)


class VectorExporter:
    """Tiles processor that exports a vector channel

    The vector data is exported to a geopackage.

    Notes:
        - Requires a vector channel

    Implements the `TilesProcessor` protocol.
    """

    def __init__(
        self,
        channel_name: ChannelName | str,
        epsg_code: EPSGCode,
        path: Path,
        remove_channel: bool = True,
    ) -> None:
        """
        Parameters:
            channel_name: Channel name
            epsg_code: EPSG code
            path: Path to the geopackage (.gpkg file)
            remove_channel: If True, the channel is removed
        """
        self._channel_name = channel_name
        self._epsg_code = epsg_code
        self._path = path
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
            channel_name=self._channel_name,
            epsg_code=self._epsg_code,
            path=self._path,
            remove_channel=self._remove_channel,
        )


class VectorExporterConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VectorExporter`

    Create the configuration from a config file:
        - Use false or true instead of False or True

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'VectorExporter'
        config:
          channel_name: 'my_channel'
          epsg_code: 25832
          path: 'path/to/my_channel.gpkg'
          remove_channel: true
        ```

    Attributes:
        channel_name: Channel name
        epsg_code: EPSG code
        path: Path to the geopackage (.gpkg file)
        remove_channel: If True, the channel is removed -
            defaults to True
    """
    channel_name: ChannelName | str
    epsg_code: EPSGCode
    path: Path
    remove_channel: bool = True


_TilesProcessorFactory.register(
    tiles_processor_class=VectorExporter,
    config_class=VectorExporterConfig,
    package=_PACKAGE,
)
