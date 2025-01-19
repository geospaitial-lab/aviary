from abc import ABC, abstractmethod

import geopandas as gpd
import numpy as np
import numpy.typing as npt

# noinspection PyProtectedMember
from aviary._functional.geodata.coordinates_filter import (
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


class CoordinatesFilter(ABC):
    """Abstract class for coordinates filters

    Coordinates filters are callables that filter coordinates.
    The coordinates filter can be used to filter the coordinates of the bottom left corner of each tile.
    E.g., to remove tiles that don't intersect with an area of interest or tiles that are already processed.

    Currently implemented coordinates filters:
        - `CompositeFilter`: Composes multiple coordinates filters
        - `DuplicatesFilter`: Removes duplicates
        - `GeospatialFilter`: Filters based on geospatial data
        - `MaskFilter`: Filters based on a boolean mask
        - `SetFilter`: Filters based on other coordinates
    """

    @abstractmethod
    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates.

        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Returns:
            filtered coordinates (x_min, y_min) of each tile
        """


class CompositeFilter(CoordinatesFilter):
    """Coordinates filter that composes multiple coordinates filters"""

    def __init__(
        self,
        coordinates_filters: list[CoordinatesFilter],
    ) -> None:
        """
        Parameters:
            coordinates_filters: coordinates filters
        """
        self.coordinates_filters = coordinates_filters

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates with each coordinates filter.

        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Returns:
            filtered coordinates (x_min, y_min) of each tile
        """
        return composite_filter(
            coordinates=coordinates,
            coordinates_filters=self.coordinates_filters,
        )


class DuplicatesFilter(CoordinatesFilter):
    """Coordinates filter that removes duplicates"""

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates by removing duplicates.

        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Returns:
            filtered coordinates (x_min, y_min) of each tile
        """
        return duplicates_filter(
            coordinates=coordinates,
        )


class GeospatialFilter(CoordinatesFilter):
    """Coordinates filter that filters based on geospatial data

    Available modes:
        - `DIFFERENCE`: Removes coordinates of tiles that are within the polygons in the geodataframe
        - `INTERSECTION`: Removes coordinates of tiles that don't intersect with the polygons in the geodataframe
    """

    def __init__(
        self,
        tile_size: TileSize,
        gdf: gpd.GeoDataFrame,
        mode: GeospatialFilterMode,
    ) -> None:
        """
        Parameters:
            tile_size: tile size in meters
            gdf: geodataframe
            mode: geospatial filter mode (`DIFFERENCE` or `INTERSECTION`)
        """
        self.tile_size = tile_size
        self.gdf = gdf
        self.mode = mode

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates based on the polygons in the geodataframe.

        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Returns:
            filtered coordinates (x_min, y_min) of each tile
        """
        return geospatial_filter(
            coordinates=coordinates,
            tile_size=self.tile_size,
            gdf=self.gdf,
            mode=self.mode,
        )


class MaskFilter(CoordinatesFilter):
    """Coordinates filter that filters based on a boolean mask"""

    def __init__(
        self,
        mask: npt.NDArray[np.bool_],
    ) -> None:
        """
        Parameters:
            mask: boolean mask
        """
        self.mask = mask

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates based on the boolean mask.

        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Returns:
            filtered coordinates (x_min, y_min) of each tile
        """
        return mask_filter(
            coordinates=coordinates,
            mask=self.mask,
        )


class SetFilter(CoordinatesFilter):
    """Coordinates filter that filters based on other coordinates

    Available modes:
        - `DIFFERENCE`: Removes coordinates that are in the other coordinates
        - `INTERSECTION`: Removes coordinates that are not in the other coordinates
        - `UNION`: Combines the coordinates with the other coordinates and removes duplicates
    """

    def __init__(
        self,
        other: CoordinatesSet,
        mode: SetFilterMode,
    ) -> None:
        """
        Parameters:
            other: other coordinates (x_min, y_min) of each tile
            mode: set filter mode (`DIFFERENCE`, `INTERSECTION` or `UNION`)
        """
        self.other = other
        self.mode = mode

    def __call__(
        self,
        coordinates: CoordinatesSet,
    ) -> CoordinatesSet:
        """Filters the coordinates based on the other coordinates.

        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Returns:
            filtered coordinates (x_min, y_min) of each tile
        """
        return set_filter(
            coordinates=coordinates,
            other=self.other,
            mode=self.mode,
        )
