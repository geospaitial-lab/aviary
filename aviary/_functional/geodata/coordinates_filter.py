from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import numpy as np
from numpy import typing as npt

from aviary._functional.geodata.grid_generator import _generate_tiles
from aviary.core.enums import (
    GeospatialFilterMode,
    SetFilterMode,
)
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        CoordinatesSet,
        EPSGCode,
        TileSize,
    )
    from aviary.geodata.coordinates_filter import CoordinatesFilter


def composite_filter(
    coordinates: CoordinatesSet,
    coordinates_filters: list[CoordinatesFilter],
) -> CoordinatesSet:
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
    coordinates: CoordinatesSet,
) -> CoordinatesSet:
    """Filters the coordinates by removing duplicates.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    _, index = np.unique(coordinates, axis=0, return_index=True)
    return coordinates[np.sort(index)]


def geospatial_filter(
    coordinates: CoordinatesSet,
    tile_size: TileSize,
    gdf: gpd.GeoDataFrame,
    mode: GeospatialFilterMode,
) -> CoordinatesSet:
    """Filters the coordinates based on the polygons in the geodataframe.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        tile_size: tile size in meters
        gdf: geodataframe
        mode: geospatial filter mode (`DIFFERENCE` or `INTERSECTION`)

    Returns:
        filtered coordinates (x_min, y_min) of each tile

    Raises:
        AviaryUserError: Invalid geospatial filter mode
    """
    epsg_code = gdf.crs.to_epsg()
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

    message = 'Invalid geospatial filter mode!'
    raise AviaryUserError(message)


def _generate_grid(
    coordinates: CoordinatesSet,
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
    coordinates: CoordinatesSet,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
) -> CoordinatesSet:
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
    coordinates: CoordinatesSet,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
) -> CoordinatesSet:
    """Filters the coordinates based on the polygons in the geodataframe.

    The coordinates of tiles that don't intersect with the polygons are removed.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        grid: grid
        gdf: geodataframe

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    intersecting_tiles = gpd.sjoin(
        left_df=grid,
        right_df=gdf,
        how='inner',
        predicate='intersects',
        rsuffix='right_intersects',
    )
    touching_tiles = gpd.sjoin(
        left_df=intersecting_tiles,
        right_df=gdf,
        how='inner',
        predicate='touches',
        rsuffix='right_touches',
    )
    valid_tiles = intersecting_tiles[~intersecting_tiles.index.isin(touching_tiles.index)]
    return coordinates[grid.index.isin(valid_tiles.index)]


def mask_filter(
    coordinates: CoordinatesSet,
    mask: npt.NDArray[np.bool_],
) -> CoordinatesSet:
    """Filters the coordinates based on the boolean mask.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        mask: boolean mask

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    return coordinates[mask]


def set_filter(
    coordinates: CoordinatesSet,
    other: CoordinatesSet,
    mode: SetFilterMode,
) -> CoordinatesSet:
    """Filters the coordinates based on the other coordinates.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        other: other coordinates (x_min, y_min) of each tile
        mode: set filter mode (`DIFFERENCE`, `INTERSECTION` or `UNION`)

    Returns:
        filtered coordinates (x_min, y_min) of each tile

    Raises:
        AviaryUserError: Invalid set filter mode
    """
    if mode == SetFilterMode.DIFFERENCE:
        return _set_filter_difference(
            coordinates=coordinates,
            other=other,
        )

    if mode == SetFilterMode.INTERSECTION:
        return _set_filter_intersection(
            coordinates=coordinates,
            other=other,
        )

    if mode == SetFilterMode.UNION:
        return _set_filter_union(
            coordinates=coordinates,
            other=other,
        )

    message = 'Invalid set filter mode!'
    raise AviaryUserError(message)


def _set_filter_difference(
    coordinates: CoordinatesSet,
    other: CoordinatesSet,
) -> CoordinatesSet:
    """Filters the coordinates based on the other coordinates.

    The coordinates that are in the other coordinates are removed.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        other: other coordinates (x_min, y_min) of each tile

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    # noinspection PyUnresolvedReferences
    mask = ~(coordinates[:, np.newaxis] == other).all(axis=-1).any(axis=-1)
    return coordinates[mask]


def _set_filter_intersection(
    coordinates: CoordinatesSet,
    other: CoordinatesSet,
) -> CoordinatesSet:
    """Filters the coordinates based on the other coordinates.

    The coordinates that are not in the other coordinates are removed.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        other: other coordinates (x_min, y_min) of each tile

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    # noinspection PyUnresolvedReferences
    mask = (coordinates[:, np.newaxis] == other).all(axis=-1).any(axis=-1)
    return coordinates[mask]


def _set_filter_union(
    coordinates: CoordinatesSet,
    other: CoordinatesSet,
) -> CoordinatesSet:
    """Filters the coordinates based on the other coordinates.

    The coordinates are combined with the other coordinates and duplicates are removed.

    Parameters:
        coordinates: coordinates (x_min, y_min) of each tile
        other: other coordinates (x_min, y_min) of each tile

    Returns:
        filtered coordinates (x_min, y_min) of each tile
    """
    coordinates = np.concatenate([coordinates, other], axis=0)
    return duplicates_filter(coordinates)
