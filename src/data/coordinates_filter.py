from abc import ABC, abstractmethod

import geopandas as gpd
import numpy as np
import numpy.typing as npt

from src.functional.data.coordinates_filter import (
    composite_filter,
    duplicates_filter,
    geospatial_filter,
    mask_filter,
    set_filter,
)
from src.utils.types import (
    Coordinates,
    EPSGCode,
    GeospatialFilterMode,
    SetFilterMode,
    TileSize,
)


class CoordinatesFilter(ABC):

    @abstractmethod
    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Coordinates:
        """
        | Filters the coordinates.

        :param coordinates: coordinates (x_min, y_min) of each tile
        :return: filtered coordinates (x_min, y_min) of each tile
        """
        pass


class CompositeFilter(CoordinatesFilter):

    def __init__(
        self,
        coordinates_filters: list[CoordinatesFilter],
    ) -> None:
        """
        :param coordinates_filters: coordinates filters
        """
        self.coordinates_filters = coordinates_filters

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Coordinates:
        """
        | Filters the coordinates with each coordinates filter.

        :param coordinates: coordinates (x_min, y_min) of each tile
        :return: filtered coordinates (x_min, y_min) of each tile
        """
        return composite_filter(
            coordinates=coordinates,
            coordinates_filters=self.coordinates_filters,
        )


class DuplicatesFilter(CoordinatesFilter):

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Coordinates:
        """
        | Filters the coordinates by removing duplicates.

        :param coordinates: coordinates (x_min, y_min) of each tile
        :return: filtered coordinates (x_min, y_min) of each tile
        """
        return duplicates_filter(
            coordinates=coordinates,
        )


class GeospatialFilter(CoordinatesFilter):

    def __init__(
        self,
        tile_size: TileSize,
        epsg_code: EPSGCode,
        gdf: gpd.GeoDataFrame,
        mode: GeospatialFilterMode,
    ) -> None:
        """
        :param tile_size: tile size in meters
        :param epsg_code: EPSG code
        :param gdf: geodataframe
        :param mode: geospatial filter mode (GeospatialFilterMode.DIFFERENCE or GeospatialFilterMode.INTERSECTION)
        """
        self.tile_size = tile_size
        self.epsg_code = epsg_code
        self.gdf = gdf
        self.mode = mode

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Coordinates:
        """
        | Filters the coordinates based on the polygons in the geodataframe.

        :param coordinates: coordinates (x_min, y_min) of each tile
        :return: filtered coordinates (x_min, y_min) of each tile
        """
        return geospatial_filter(
            coordinates=coordinates,
            tile_size=self.tile_size,
            epsg_code=self.epsg_code,
            gdf=self.gdf,
            mode=self.mode,
        )


class MaskFilter(CoordinatesFilter):

    def __init__(
        self,
        mask: npt.NDArray[np.bool_],
    ) -> None:
        """
        :param mask: boolean mask
        """
        self.mask = mask

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Coordinates:
        """
        | Filters the coordinates based on the boolean mask.

        :param coordinates: coordinates (x_min, y_min) of each tile
        :return: filtered coordinates (x_min, y_min) of each tile
        """
        return mask_filter(
            coordinates=coordinates,
            mask=self.mask,
        )


class SetFilter(CoordinatesFilter):

    def __init__(
        self,
        additional_coordinates: Coordinates,
        mode: SetFilterMode,
    ) -> None:
        """
        :param additional_coordinates: additional coordinates (x_min, y_min) of each tile
        :param mode: set filter mode (SetFilterMode.DIFFERENCE, SetFilterMode.INTERSECTION or SetFilterMode.UNION)
        """
        self.additional_coordinates = additional_coordinates
        self.mode = mode

    def __call__(
        self,
        coordinates: Coordinates,
    ) -> Coordinates:
        """
        | Filters the coordinates based on the additional coordinates.

        :param coordinates: coordinates (x_min, y_min) of each tile
        :return: filtered coordinates (x_min, y_min) of each tile
        """
        return set_filter(
            coordinates=coordinates,
            additional_coordinates=self.additional_coordinates,
            mode=self.mode,
        )
