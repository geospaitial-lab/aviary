from abc import ABC, abstractmethod

import geopandas as gpd

from .._functional.geodata.geodata_postprocessor import (
    clip_postprocessor,
    composite_postprocessor,
    field_name_postprocessor,
    fill_postprocessor,
    sieve_postprocessor,
    simplify_postprocessor,
    value_postprocessor,
)


class GeodataPostprocessor(ABC):
    """Abstract class for geodata postprocessors

    Geodata postprocessors are callables that postprocess geodata.
    The geodata postprocessor is used by the pipeline to postprocess the resulting geodata,
    which is the vectorized output of the model's inference.

    Currently implemented geodata postprocessors:
        - ClipPostprocessor: Clips the polygons based on the mask extent
        - CompositePostprocessor: Composes multiple geodata postprocessors
        - FieldNamePostprocessor: Renames the fields
        - FillPostprocessor: Fills holes in the polygons
        - SievePostprocessor: Sieves the polygons
        - SimplifyPostprocessor: Simplifies the polygons by applying the Douglas-Peucker algorithm
        - ValuePostprocessor: Maps the values of a field
    """

    @abstractmethod
    def __call__(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Postprocesses the geodata.

        Parameters:
            gdf: geodataframe

        Returns:
            postprocessed geodataframe
        """
        pass


class ClipPostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that clips the polygons based on the mask extent"""

    def __init__(
        self,
        mask: gpd.GeoDataFrame,
    ) -> None:
        """
        Parameters:
            mask: geodataframe of the mask (may contain multiple polygons)
        """
        self.mask = mask

    def __call__(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Postprocesses the geodata by clipping the polygons based on the mask extent.

        Parameters:
            gdf: geodataframe

        Returns:
            postprocessed geodataframe
        """
        return clip_postprocessor(
            gdf=gdf,
            mask=self.mask,
        )


class CompositePostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that composes multiple geodata postprocessors"""

    def __init__(
        self,
        geodata_postprocessors: list[GeodataPostprocessor],
    ) -> None:
        """
        Parameters:
            geodata_postprocessors: geodata postprocessors
        """
        self.geodata_postprocessors = geodata_postprocessors

    def __call__(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Postprocesses the geodata with each geodata postprocessor.

        Parameters:
            gdf: geodataframe

        Returns:
            postprocessed geodataframe
        """
        return composite_postprocessor(
            gdf=gdf,
            geodata_postprocessors=self.geodata_postprocessors,
        )


class FieldNamePostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that renames the fields"""

    def __init__(
        self,
        mapping: dict,
    ) -> None:
        """
        Parameters:
            mapping: mapping of the field names (old field name: new field name)
        """
        self.mapping = mapping

    def __call__(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Postprocesses the geodata by renaming the fields.

        Parameters:
            gdf: geodataframe

        Returns:
            postprocessed geodataframe
        """
        return field_name_postprocessor(
            gdf=gdf,
            mapping=self.mapping,
        )


class FillPostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that fills holes in the polygons"""

    def __init__(
        self,
        max_area: float,
    ) -> None:
        """
        Parameters:
            max_area: maximum area of the holes to fill in square meters
        """
        self.max_area = max_area

    def __call__(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Postprocesses the geodata by filling holes in the polygons.

        Parameters:
            gdf: geodataframe

        Returns:
            postprocessed geodataframe
        """
        return fill_postprocessor(
            gdf=gdf,
            max_area=self.max_area,
        )


class SievePostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that sieves the polygons"""

    def __init__(
        self,
        min_area: float,
    ) -> None:
        """
        Parameters:
            min_area: minimum area of the polygons to retain in square meters
        """
        self.min_area = min_area

    def __call__(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Postprocesses the geodata by sieving the polygons.

        Parameters:
            gdf: geodataframe

        Returns:
            postprocessed geodataframe
        """
        return sieve_postprocessor(
            gdf=gdf,
            min_area=self.min_area,
        )


class SimplifyPostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that simplifies the polygons by applying the Douglas-Peucker algorithm"""

    def __init__(
        self,
        tolerance: float,
    ) -> None:
        """
        Parameters:
            tolerance: tolerance of the Douglas-Peucker algorithm in meters (a lower value will result
                in less simplification, a higher value will result in more simplification,
                a value equal to the ground sampling distance is recommended)
        """
        self.tolerance = tolerance

    def __call__(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Postprocesses the geodata by simplifying the polygons.

        Parameters:
            gdf: geodataframe

        Returns:
            postprocessed geodataframe
        """
        return simplify_postprocessor(
            gdf=gdf,
            tolerance=self.tolerance,
        )


class ValuePostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that maps the values of a field"""

    def __init__(
        self,
        mapping: dict,
        field_name: str = 'class',
    ) -> None:
        """
        Parameters:
            mapping: mapping of the values (old value: new value)
            field_name: name of the field
        """
        self.mapping = mapping
        self.field_name = field_name

    def __call__(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Postprocesses the geodata by mapping the values of a field.

        Parameters:
            gdf: geodataframe

        Returns:
            postprocessed geodataframe
        """
        return value_postprocessor(
            gdf=gdf,
            mapping=self.mapping,
            field_name=self.field_name,
        )
