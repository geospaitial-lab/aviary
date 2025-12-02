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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import geopandas as gpd
import pandas as pd

from aviary.core.grid import Grid

if TYPE_CHECKING:
    from aviary.core.channel import VectorChannel
    from aviary.core.enums import ChannelName
    from aviary.core.tiles import Tiles
    from aviary.core.type_aliases import EPSGCode


def grid_exporter(
    tiles: Tiles,
    path: Path,
) -> Tiles:
    """Exports the grid of the tiles.

    Parameters:
        tiles: Tiles
        path: Path to the JSON file (.json file)

    Returns:
        Tiles
    """
    coordinates = tiles.coordinates
    tile_size = tiles.tile_size

    try:
        with path.open() as file:
            json_string = file.read()

        grid = Grid.from_json(json_string=json_string)
    except FileNotFoundError:
        grid = Grid(
            coordinates=None,
            tile_size=tile_size,
        )

    grid = grid.append(coordinates=coordinates)
    json_string = grid.to_json()

    with path.open('w') as file:
        file.write(json_string)

    return tiles


def vector_exporter(
    tiles: Tiles,
    channel_name: ChannelName | str,
    epsg_code: EPSGCode | None,
    path: Path,
    remove_channel: bool = True,
) -> Tiles:
    """Exports the vector channel.

    Parameters:
        tiles: Tiles
        channel_name: Channel name
        epsg_code: EPSG code
        path: Path to the geopackage (.gpkg file)
        remove_channel: If True, the channel is removed

    Returns:
        Tiles
    """
    channel: VectorChannel = tiles[channel_name]
    coordinates = tiles.coordinates
    tile_size = tiles.tile_size
    data = channel.to_denormalized_data(
        coordinates=coordinates,
        tile_size=tile_size,
    )

    data = pd.concat(
        data,
        ignore_index=True,
        copy=False,
    )
    epsg_code = f'EPSG:{epsg_code}' if epsg_code is not None else None
    gdf = gpd.GeoDataFrame(data=data)

    if not gdf.empty:
        gdf = gdf.set_crs(
            crs=epsg_code,
            inplace=True,
        )

        gdf.to_file(
            path,
            driver='GPKG',
            mode='a',
        )

    if remove_channel:
        tiles = tiles.remove(
            channel_names=channel_name,
            inplace=True,
        )

    return tiles
