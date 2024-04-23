from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import numpy as np
from numpy import typing as npt

if TYPE_CHECKING:
    from src.data.coordinates_filter import CoordinatesFilter
from src.functional.data.grid_generator import _generate_polygons
from src.utils.types import (
    Coordinates,
    EPSGCode,
    GeospatialFilterMode,
    SetFilterMode,
    TileSize,
)


def composite_filter(
    coordinates: Coordinates,
    coordinates_filters: list[CoordinatesFilter],
) -> Coordinates:
    """
    | Filters the coordinates with each coordinates filter.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param coordinates_filters: coordinates filters
    :return: filtered coordinates (x_min, y_min) of each tile
    """
    for coordinates_filter in coordinates_filters:
        coordinates = coordinates_filter(coordinates)
    return coordinates


def duplicates_filter(
    coordinates: Coordinates,
) -> Coordinates:
    """
    | Filters the coordinates by removing duplicates.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :return: filtered coordinates (x_min, y_min) of each tile
    """
    return np.unique(coordinates, axis=0)


def geospatial_filter(
    coordinates: Coordinates,
    tile_size: TileSize,
    epsg_code: EPSGCode,
    gdf: gpd.GeoDataFrame,
    mode: GeospatialFilterMode,
) -> Coordinates:
    """
    | Filters the coordinates based on the polygons in the geodataframe.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param tile_size: tile size in meters
    :param epsg_code: EPSG code
    :param gdf: geodataframe
    :param mode: geospatial filter mode (GeospatialFilterMode.DIFFERENCE or GeospatialFilterMode.INTERSECTION)
    :return: filtered coordinates (x_min, y_min) of each tile
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

    raise ValueError('Invalid GeospatialFilterMode!')


def _generate_grid(
    coordinates: Coordinates,
    tile_size: TileSize,
    epsg_code: EPSGCode,
) -> gpd.GeoDataFrame:
    """
    | Generates a geodataframe of the grid.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param tile_size: tile size in meters
    :param epsg_code: EPSG code
    :return: grid
    """
    polygons = _generate_polygons(
        coordinates=coordinates,
        tile_size=tile_size,
    )
    return gpd.GeoDataFrame(
        geometry=polygons,
        crs=f'EPSG:{epsg_code}',
    )


def _geospatial_filter_difference(
    coordinates: Coordinates,
    grid: gpd.GeoDataFrame,
    gdf: gpd.GeoDataFrame,
) -> Coordinates:
    """
    | Filters the coordinates based on the polygons in the geodataframe.
    | The coordinates of tiles that are within the polygons are removed.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param grid: grid
    :param gdf: geodataframe
    :return: filtered coordinates (x_min, y_min) of each tile
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
    """
    | Filters the coordinates based on the polygons in the geodataframe.
    | The coordinates of tiles that do not intersect with the polygons are removed.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param grid: grid
    :param gdf: geodataframe
    :return: filtered coordinates (x_min, y_min) of each tile
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
    """
    | Filters the coordinates based on the boolean mask.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param mask: boolean mask
    :return: filtered coordinates (x_min, y_min) of each tile
    """
    return coordinates[mask]


def set_filter(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
    mode: SetFilterMode,
) -> Coordinates:
    """
    | Filters the coordinates based on the additional coordinates.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param additional_coordinates: additional coordinates (x_min, y_min) of each tile
    :param mode: set filter mode (SetFilterMode.DIFFERENCE, SetFilterMode.INTERSECTION or SetFilterMode.UNION)
    :return: filtered coordinates (x_min, y_min) of each tile
    """
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

    raise ValueError('Invalid SetFilterMode!')


def _set_filter_difference(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
) -> Coordinates:
    """
    | Filters the coordinates based on the additional coordinates.
    | The coordinates that are in the additional coordinates are removed.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param additional_coordinates: additional coordinates (x_min, y_min) of each tile
    :return: filtered coordinates (x_min, y_min) of each tile
    """
    mask = np.isin(coordinates, additional_coordinates, invert=True).all(axis=-1)
    return coordinates[mask]


def _set_filter_intersection(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
) -> Coordinates:
    """
    | Filters the coordinates based on the additional coordinates.
    | The coordinates that are not in the additional coordinates are removed.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param additional_coordinates: additional coordinates (x_min, y_min) of each tile
    :return: filtered coordinates (x_min, y_min) of each tile
    """
    mask = np.isin(coordinates, additional_coordinates).all(axis=-1)
    return coordinates[mask]


def _set_filter_union(
    coordinates: Coordinates,
    additional_coordinates: Coordinates,
) -> Coordinates:
    """
    | Filters the coordinates based on the additional coordinates.
    | The coordinates are combined with the additional coordinates and duplicates are removed.

    :param coordinates: coordinates (x_min, y_min) of each tile
    :param additional_coordinates: additional coordinates (x_min, y_min) of each tile
    :return: filtered coordinates (x_min, y_min) of each tile
    """
    coordinates = np.concatenate([coordinates, additional_coordinates], axis=0)
    coordinates = np.unique(coordinates, axis=0)
    return coordinates
