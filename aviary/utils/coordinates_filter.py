from typing import Protocol

import geopandas as gpd
import numpy as np
import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.utils.coordinates_filter import (
    composite_filter,
    duplicates_filter,
    geospatial_filter,
    mask_filter,
    set_filter,
)
from aviary.core.enums import (
    GeospatialFilterMode,
    SetFilterMode,
)
from aviary.core.type_aliases import (
    CoordinatesSet,
    TileSize,
)


class CoordinatesFilter(Protocol):
    """Protocol for coordinates filters

    Coordinates filters are callables that filter coordinates.

    Implemented coordinates filters:
        - `CompositeFilter`: Composes multiple coordinates filters
        - `DuplicatesFilter`: Removes duplicate coordinates
        - `GeospatialFilter`: Filters based on geospatial data
        - `MaskFilter`: Filters based on a boolean mask
        - `SetFilter`: Filters based on other coordinates
    """

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of each tile in meters

        Returns:
            Coordinates (x_min, y_min) of each tile in meters
        """
        ...


class CompositeFilter:
    """Coordinates filter that composes multiple coordinates filters

    Notes:
        - The coordinates filters are composed vertically, i.e., in sequence

    Implements the `CoordinatesFilter` protocol.
    """

    def __init__(
        self,
        coordinates_filters: list[CoordinatesFilter],
    ) -> None:
        """
        Parameters:
            coordinates_filters: Coordinates filters
        """
        self._coordinates_filters = coordinates_filters

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates with each coordinates filter.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of each tile in meters

        Returns:
            Coordinates (x_min, y_min) of each tile in meters
        """
        return composite_filter(
            coordinates=coordinates,
            coordinates_filters=self._coordinates_filters,
        )


class DuplicatesFilter:
    """Coordinates filter that removes duplicate coordinates

    Implements the `CoordinatesFilter` protocol.
    """

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates by removing duplicate coordinates.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of each tile in meters

        Returns:
            Coordinates (x_min, y_min) of each tile in meters
        """
        return duplicates_filter(
            coordinates=coordinates,
        )


class GeospatialFilter:
    """Coordinates filter that filters based on geospatial data

    Available modes:
        - `DIFFERENCE`: Removes coordinates of tiles that are within the polygons in the geodataframe
        - `INTERSECTION`: Removes coordinates of tiles that do not intersect with the polygons in the geodataframe

    Implements the `CoordinatesFilter` protocol.
    """

    def __init__(
        self,
        tile_size: TileSize,
        gdf: gpd.GeoDataFrame,
        mode: GeospatialFilterMode,
    ) -> None:
        """
        Parameters:
            tile_size: Tile size in meters
            gdf: Geodataframe
            mode: Geospatial filter mode (`DIFFERENCE` or `INTERSECTION`)
        """
        self._tile_size = tile_size
        self._gdf = gdf
        self._mode = mode

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates based on the polygons in the geodataframe.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of each tile in meters

        Returns:
            Coordinates (x_min, y_min) of each tile in meters
        """
        return geospatial_filter(
            coordinates=coordinates,
            tile_size=self._tile_size,
            gdf=self._gdf,
            mode=self._mode,
        )


class MaskFilter:
    """Coordinates filter that filters based on a boolean mask

    Implements the `CoordinatesFilter` protocol.
    """

    def __init__(
        self,
        mask: npt.NDArray[np.bool_],
    ) -> None:
        """
        Parameters:
            mask: Boolean mask
        """
        self._mask = mask

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates based on the boolean mask.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of each tile in meters

        Returns:
            Coordinates (x_min, y_min) of each tile in meters
        """
        return mask_filter(
            coordinates=coordinates,
            mask=self._mask,
        )


class SetFilter:
    """Coordinates filter that filters based on other coordinates

    Available modes:
        - `DIFFERENCE`: Removes coordinates that are in the other coordinates
        - `INTERSECTION`: Removes coordinates that are not in the other coordinates
        - `UNION`: Combines the coordinates with the other coordinates and removes duplicate coordinates

    Implements the `CoordinatesFilter` protocol.
    """

    def __init__(
        self,
        other: CoordinatesSet,
        mode: SetFilterMode,
    ) -> None:
        """
        Parameters:
            other: Other coordinates (x_min, y_min) of each tile in meters
            mode: Set filter mode (`DIFFERENCE`, `INTERSECTION`, or `UNION`)
        """
        self._other = other
        self._mode = mode

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates based on the other coordinates.

        Parameters:
            coordinates: Coordinates (x_min, y_min) of each tile in meters

        Returns:
            Coordinates (x_min, y_min) of each tile in meters
        """
        return set_filter(
            coordinates=coordinates,
            other=self._other,
            mode=self._mode,
        )
