from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import numpy as np
from numpy import typing as npt

from ..._utils.exceptions import AviaryUserError
if TYPE_CHECKING:
    from ..._utils.types import (
        Coordinates,
        EPSGCode,
        GeospatialFilterMode,
        SetFilterMode,
        TileSize,
    )
    from ...geodata import CoordinatesFilter
from .grid_generator import _generate_tiles


def composite_filter(
    coordinates: Coordinates,
    coordinates_filters: list[CoordinatesFilter],
) -> Coordinates:
    """Filters the coordinates with each coordinates filter.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        coordinates_filters: coordinates filters

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    for coordinates_filter in coordinates_filters:
        coordinates = coordinates_filter(coordinates)
    return coordinates


def duplicates_filter(
    coordinates: Coordinates,
) -> Coordinates:
    """Filters the coordinates by removing duplicates.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    _, index = np.unique(coordinates, axis=0, return_index=True)
    return coordinates[np.sort(index)]


def geospatial_filter(
    coordinates: Coordinates,
    tile_size: TileSize,
    epsg_code: EPSGCode,
    gdf: gpd.GeoDataFrame,
    mode: GeospatialFilterMode,
) -> Coordinates:
    """Filters the coordinates based on the polygons in the geodataframe.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        tile_size: tile size in meters
        epsg_code: EPSG code
        gdf: geodataframe
        mode: geospatial filter mode (`DIFFERENCE` or `INTERSECTION`)

    Returns:
        filtered coordinates (x_min, y_min) of each tile

    Raises:
        AviaryUserError: Invalid geospatial filter mode
    """
    grid = _generate_grid(
        coordinates=coordinates,
        tile_size=tile_size,
        epsg_code=epsg_code,
    )

    if mode == GeospatialFilterMode.DIFFERENCE:
        return _geospatial_filter_difference(
            coordinates=coordinates,
            grid=grid,
            gdf=gdf,
        )

    if mode == GeospatialFilterMode.INTERSECTION:
        return _geospatial_filter_intersection(
            coordinates=coordinates,
            grid=grid,
            gdf=gdf,
        )

    raise AviaryUserError('Invalid geospatial filter mode!')


def _generate_grid(
    coordinates: Coordinates,
    tile_size: TileSize,
    epsg_code: EPSGCode,
) -> gpd.GeoDataFrame:
    """Generates a geodataframe of the grid.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        tile_size: tile size in meters
        epsg_code: EPSG code

    Returns:
        grid
    """
    tiles = _generate_tiles(
        coordinates=coordinates,
        tile_size=tile_size,
    )
    return gpd.GeoDataFrame(
        geometry=tiles,
        crs=f'EPSG:{epsg_code}',
    )


def _geospatial_filter_difference(
    coordinates: Coordinates,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
) -> Coordinates:
    """Filters the coordinates based on the polygons in the geodataframe.

    The coordinates of tiles that are within the polygons are removed.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        grid: grid
        gdf: geodataframe

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    invalid_tiles = gpd.sjoin(
        left_df=grid,
        right_df=gdf,
        how='inner',
        predicate='within',
    )
    return coordinates[~grid.index.isin(invalid_tiles.index)]


def _geospatial_filter_intersection(
    coordinates: Coordinates,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
) -> Coordinates:
    """Filters the coordinates based on the polygons in the geodataframe.

    The coordinates of tiles that do not intersect with the polygons are removed.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        grid: grid
        gdf: geodataframe

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    valid_tiles = gpd.sjoin(
        left_df=grid,
        right_df=gdf,
        how='inner',
        predicate='intersects',
    )
    return coordinates[grid.index.isin(valid_tiles.index)]


def mask_filter(
    coordinates: Coordinates,
    mask: npt.NDArray[np.bool_],
) -> Coordinates:
    """Filters the coordinates based on the boolean mask.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        mask: boolean mask

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    return coordinates[mask]


def set_filter(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
    mode: SetFilterMode,
) -> Coordinates:
    """Filters the coordinates based on the additional coordinates.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        additional_coordinates: additional coordinates (x_min, y_min) of each tile
        mode: set filter mode (`DIFFERENCE`, `INTERSECTION` or `UNION`)

    Returns:
        filtered coordinates (x_min, y_min) of each tile

    Raises:
        AviaryUserError: Invalid set filter mode
    """
    from ..._utils.types import SetFilterMode

    if mode == SetFilterMode.DIFFERENCE:
        return _set_filter_difference(
            coordinates=coordinates,
            additional_coordinates=additional_coordinates,
        )

    if mode == SetFilterMode.INTERSECTION:
        return _set_filter_intersection(
            coordinates=coordinates,
            additional_coordinates=additional_coordinates,
        )

    if mode == SetFilterMode.UNION:
        return _set_filter_union(
            coordinates=coordinates,
            additional_coordinates=additional_coordinates,
        )

    raise AviaryUserError('Invalid set filter mode!')


def _set_filter_difference(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
) -> Coordinates:
    """Filters the coordinates based on the additional coordinates.

    The coordinates that are in the additional coordinates are removed.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        additional_coordinates: additional coordinates (x_min, y_min) of each tile

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    # noinspection PyUnresolvedReferences
    mask = ~(coordinates[:, np.newaxis] == additional_coordinates).all(axis=-1).any(axis=-1)
    return coordinates[mask]


def _set_filter_intersection(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
) -> Coordinates:
    """Filters the coordinates based on the additional coordinates.

    The coordinates that are not in the additional coordinates are removed.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        additional_coordinates: additional coordinates (x_min, y_min) of each tile

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    # noinspection PyUnresolvedReferences
    mask = (coordinates[:, np.newaxis] == additional_coordinates).all(axis=-1).any(axis=-1)
    return coordinates[mask]


def _set_filter_union(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
) -> Coordinates:
    """Filters the coordinates based on the additional coordinates.

    The coordinates are combined with the additional coordinates and duplicates are removed.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        additional_coordinates: additional coordinates (x_min, y_min) of each tile

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    coordinates = np.concatenate([coordinates, additional_coordinates], axis=0)
    coordinates = duplicates_filter(coordinates)
    return coordinates
