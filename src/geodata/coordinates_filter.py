from abc import ABC, abstractmethod

import geopandas as gpd
import numpy as np
import numpy.typing as npt

from ..functional.geodata.coordinates_filter import (
    composite_filter,
    duplicates_filter,
    geospatial_filter,
    mask_filter,
    set_filter,
)
from ..utils.types import (
    Coordinates,
    EPSGCode,
    GeospatialFilterMode,
    SetFilterMode,
    TileSize,
)


class CoordinatesFilter(ABC):
    """Abstract class for coordinates filters

    Coordinates filters are callables that filter coordinates.
    The coordinates filter can be used to filter the coordinates of the bottom left corner of each tile.
    E.g., to remove tiles that do not intersect with a region of interest or tiles that are already processed.

    Currently implemented coordinates filters:
        - CompositeFilter: Composes multiple coordinates filters
        - DuplicatesFilter: Removes duplicates
        - GeospatialFilter: Filters based on geospatial data
        - MaskFilter: Filters based on a boolean mask
        - SetFilter: Filters based on additional coordinates
    """

    @abstractmethod
    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Coordinates:
        """Filters the coordinates.

        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Returns:
            filtered coordinates (x_min, y_min) of each tile
        """
        pass


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
        coordinates: Coordinates,
    ) -> Coordinates:
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
        coordinates: Coordinates,
    ) -> Coordinates:
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
        - `INTERSECTION`: Removes coordinates of tiles that do not intersect with the polygons in the geodataframe
    """

    def __init__(
        self,
        tile_size: TileSize,
        epsg_code: EPSGCode,
        gdf: gpd.GeoDataFrame,
        mode: GeospatialFilterMode,
    ) -> None:
        """
        Parameters:
            tile_size: tile size in meters
            epsg_code: EPSG code
            gdf: geodataframe
            mode: geospatial filter mode (`DIFFERENCE` or `INTERSECTION`)
        """
        self.tile_size = tile_size
        self.epsg_code = epsg_code
        self.gdf = gdf
        self.mode = mode

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Coordinates:
        """Filters the coordinates based on the polygons in the geodataframe.

        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Returns:
            filtered coordinates (x_min, y_min) of each tile

        Raises:
            ValueError: Invalid geospatial filter mode
        """
        return geospatial_filter(
            coordinates=coordinates,
            tile_size=self.tile_size,
            epsg_code=self.epsg_code,
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
        coordinates: Coordinates,
    ) -> Coordinates:
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
    """Coordinates filter that filters based on additional coordinates

    Available modes:
        - `DIFFERENCE`: Removes coordinates that are in the additional coordinates
        - `INTERSECTION`: Removes coordinates that are not in the additional coordinates
        - `UNION`: Combines the coordinates with the additional coordinates and removes duplicates
    """

    def __init__(
        self,
        additional_coordinates: Coordinates,
        mode: SetFilterMode,
    ) -> None:
        """
        Parameters:
            additional_coordinates: additional coordinates (x_min, y_min) of each tile
            mode: set filter mode (`DIFFERENCE`, `INTERSECTION` or `UNION`)
        """
        self.additional_coordinates = additional_coordinates
        self.mode = mode

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Coordinates:
        """Filters the coordinates based on the additional coordinates.

        Parameters:
            coordinates: coordinates (x_min, y_min) of each tile

        Returns:
            filtered coordinates (x_min, y_min) of each tile

        Raises:
            ValueError: Invalid set filter mode
        """
        return set_filter(
            coordinates=coordinates,
            additional_coordinates=self.additional_coordinates,
            mode=self.mode,
        )
