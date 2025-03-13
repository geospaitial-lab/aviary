from pathlib import Path
from typing import TYPE_CHECKING

import geopandas as gpd
import pandas as pd

from aviary.core.enums import ChannelName
from aviary.core.grid import Grid
from aviary.core.tiles import Tiles
from aviary.core.type_aliases import (
    ChannelKey,
    EPSGCode,
)

if TYPE_CHECKING:
    from aviary.core.channel import VectorChannel


def grid_exporter(
    tiles: Tiles,
    dir_path: Path,
    json_name: str,
) -> Tiles:
    """Exports the grid of the tiles.

    Parameters:
        tiles: Tiles
        dir_path: Path to the directory
        json_name: Name of the JSON file (.json file)

    Returns:
        Tiles
    """
    coordinates = tiles.coordinates
    tile_size = tiles.tile_size

    json_path = dir_path / json_name

    try:
        with json_path.open() as file:
            json_string = file.read()

        grid = Grid.from_json(json_string=json_string)
    except FileNotFoundError:
        grid = Grid(
            coordinates=None,
            tile_size=tile_size,
        )

    grid = grid.append(coordinates=coordinates)
    json_string = grid.to_json()

    with json_path.open('w') as file:
        file.write(json_string)


def vector_exporter(
    tiles: Tiles,
    channel_key: ChannelName | str | ChannelKey,
    epsg_code: EPSGCode | None,
    dir_path: Path,
    gpkg_name: str,
    remove_channel: bool = True,
) -> Tiles:
    """Exports the vector channel.

    Parameters:
        tiles: Tiles
        channel_key: Channel name or channel name and time step combination
        epsg_code: EPSG code
        dir_path: Path to the directory
        gpkg_name: Name of the geopackage (.gpkg file)
        remove_channel: If True, the channel is removed

    Returns:
        Tiles
    """
    channel: VectorChannel = tiles[channel_key]
    coordinates = tiles.coordinates
    tile_size = tiles.tile_size
    data = channel.to_denormalized_data(
        coordinates=coordinates,
        tile_size=tile_size,
    )
    data = pd.concat(data, ignore_index=True)
    epsg_code = f'EPSG:{epsg_code}' if epsg_code is not None else None
    gdf = gpd.GeoDataFrame(
        data=data,
        crs=epsg_code,
    )

    gpkg_path = dir_path / gpkg_name

    gdf.to_file(
        gpkg_path,
        driver='GPKG',
        mode='a',
    )

    if remove_channel:
        tiles = tiles.remove(
            channel_keys=channel_key,
            inplace=True,
        )

    return tiles
