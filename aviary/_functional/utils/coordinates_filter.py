from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import numpy as np
from numpy import typing as npt

from aviary.core.enums import (
    GeospatialFilterMode,
    SetFilterMode,
)
from aviary.core.exceptions import AviaryUserError

if TYPE_CHECKING:
    from aviary.core.type_aliases import (
        CoordinatesSet,
        TileSize,
    )
    from aviary.utils.coordinates_filter import CoordinatesFilter


def composite_filter(
    coordinates: CoordinatesSet,
    coordinates_filters: list[CoordinatesFilter],
) -> CoordinatesSet:
    """Filters the coordinates with each coordinates filter.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of each tile in meters
        coordinates_filters: Coordinates filters

    Returns:
        Coordinates (x_min, y_min) of each tile in meters
    """
    for coordinates_filter in coordinates_filters:
        coordinates = coordinates_filter(coordinates)

    return coordinates


def duplicates_filter(
    coordinates: CoordinatesSet,
) -> CoordinatesSet:
    """Filters the coordinates by removing duplicate coordinates.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of each tile in meters

    Returns:
        Coordinates (x_min, y_min) of each tile in meters
    """
    _, indices = np.unique(
        coordinates,
        axis=0,
        return_index=True,
    )
    return coordinates[np.sort(indices)]


def geospatial_filter(
    coordinates: CoordinatesSet,
    tile_size: TileSize,
    gdf: gpd.GeoDataFrame,
    mode: GeospatialFilterMode,
) -> CoordinatesSet:
    """Filters the coordinates based on the polygons in the geodataframe.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of each tile in meters
        tile_size: Tile size in meters
        gdf: Geodataframe
        mode: Geospatial filter mode (`DIFFERENCE` or `INTERSECTION`)

    Returns:
        Coordinates (x_min, y_min) of each tile in meters

    Raises:
        AviaryUserError: Invalid `mode`
    """
    from aviary.core.grid import Grid

    grid = Grid(
        coordinates=coordinates,
        tile_size=tile_size,
    )
    epsg_code = gdf.crs.to_epsg() if gdf.crs is not None else None
    grid = grid.to_gdf(epsg_code=epsg_code)

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

    message = 'Invalid mode!'
    raise AviaryUserError(message)


def _geospatial_filter_difference(
    coordinates: CoordinatesSet,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
) -> CoordinatesSet:
    """Filters the coordinates based on the polygons in the geodataframe.

    The coordinates of tiles that are within the polygons are removed.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of each tile in meters
        grid: Grid
        gdf: Geodataframe

    Returns:
        Coordinates (x_min, y_min) of each tile in meters
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

    The coordinates of tiles that do not intersect with the polygons are removed.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of each tile in meters
        grid: Grid
        gdf: Geodataframe

    Returns:
        Coordinates (x_min, y_min) of each tile in meters
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
        coordinates: Coordinates (x_min, y_min) of each tile in meters
        mask: Boolean mask

    Returns:
        Coordinates (x_min, y_min) of each tile in meters
    """
    return coordinates[mask]


def set_filter(
    coordinates: CoordinatesSet,
    other: CoordinatesSet,
    mode: SetFilterMode,
) -> CoordinatesSet:
    """Filters the coordinates based on the other coordinates.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of each tile in meters
        other: Other coordinates (x_min, y_min) of each tile in meters
        mode: Set filter mode (`DIFFERENCE`, `INTERSECTION`, or `UNION`)

    Returns:
        Coordinates (x_min, y_min) of each tile in meters

    Raises:
        AviaryUserError: Invalid `mode`
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

    message = 'Invalid mode!'
    raise AviaryUserError(message)


def _set_filter_difference(
    coordinates: CoordinatesSet,
    other: CoordinatesSet,
) -> CoordinatesSet:
    """Filters the coordinates based on the other coordinates.

    The coordinates that are in the other coordinates are removed.

    Parameters:
        coordinates: Coordinates (x_min, y_min) of each tile in meters
        other: Other coordinates (x_min, y_min) of each tile in meters

    Returns:
        Coordinates (x_min, y_min) of each tile in meters
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
        coordinates: Coordinates (x_min, y_min) of each tile in meters
        other: Other coordinates (x_min, y_min) of each tile in meters

    Returns:
        Coordinates (x_min, y_min) of each tile in meters
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
        coordinates: Coordinates (x_min, y_min) of each tile in meters
        other: Other coordinates (x_min, y_min) of each tile in meters

    Returns:
        Coordinates (x_min, y_min) of each tile in meters
    """
    coordinates = np.concatenate([coordinates, other], axis=0)
    return duplicates_filter(coordinates)
