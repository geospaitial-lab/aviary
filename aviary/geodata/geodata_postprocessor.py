from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path  # noqa: TCH003

import geopandas as gpd
import pydantic

# noinspection PyProtectedMember
from aviary._functional.geodata.geodata_postprocessor import (
    clip_postprocessor,
    composite_postprocessor,
    field_name_postprocessor,
    fill_postprocessor,
    sieve_postprocessor,
    simplify_postprocessor,
    value_postprocessor,
)

# noinspection PyProtectedMember
from aviary._utils.mixins import FromConfigMixin


class GeodataPostprocessor(ABC, FromConfigMixin):
    """Abstract class for geodata postprocessors

    Geodata postprocessors are callables that postprocess geodata.
    The geodata postprocessor is used by the pipeline to postprocess the resulting geodata,
    which is the vectorized output of the model's inference.

    Currently implemented geodata postprocessors:
        - `ClipPostprocessor`: Clips the polygons based on the mask extent
        - `CompositePostprocessor`: Composes multiple geodata postprocessors
        - `FieldNamePostprocessor`: Renames the fields
        - `FillPostprocessor`: Fills holes in the polygons
        - `SievePostprocessor`: Sieves the polygons
        - `SimplifyPostprocessor`: Simplifies the polygons by applying the Douglas-Peucker algorithm
        - `ValuePostprocessor`: Maps the values of a field
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

    @classmethod
    def from_config(
        cls,
        config: ClipPostprocessorConfig,
    ) -> ClipPostprocessor:
        """Creates a clip postprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            clip postprocessor
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

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


class ClipPostprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `ClipPostprocessor`

    Attributes:
        mask: path to the geodataframe of the mask (may contain multiple polygons)
    """
    mask: Path

    # noinspection PyNestedDecorators
    @pydantic.field_validator('mask')
    @classmethod
    def parse_mask(
        cls,
        mask: Path,
    ) -> gpd.GeoDataFrame:
        """Parses the geodataframe of the mask."""
        return gpd.read_file(mask)


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

    @classmethod
    def from_config(
        cls,
        config: CompositePostprocessorConfig,
    ) -> CompositePostprocessor:
        """Creates a composite postprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            composite postprocessor
        """
        geodata_postprocessors = []

        for geodata_postprocessor_config in config.geodata_postprocessors_configs:
            geodata_postprocessor_class = globals()[geodata_postprocessor_config.name]
            geodata_postprocessor = geodata_postprocessor_class.from_config(geodata_postprocessor_config.config)
            geodata_postprocessors.append(geodata_postprocessor)

        return cls(
            geodata_postprocessors=geodata_postprocessors,
        )

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


class CompositePostprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `CompositePostprocessor`

    Attributes:
        geodata_postprocessors_configs: configurations of the geodata postprocessors
    """
    geodata_postprocessors_configs: list[GeodataPostprocessorConfig]


class GeodataPostprocessorConfig(pydantic.BaseModel):
    """Configuration for geodata postprocessors

    Attributes:
        name: name of the geodata postprocessor
        config: configuration of the geodata postprocessor
    """
    name: str
    config: (
        ClipPostprocessorConfig |
        FieldNamePostprocessorConfig |
        FillPostprocessorConfig |
        SievePostprocessorConfig |
        SimplifyPostprocessorConfig |
        ValuePostprocessorConfig
    )


class FieldNamePostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that renames the fields

    Examples:
        Assume the geodataframe has the field 'class'.

        You can rename the field 'class' to 'type'.

        >>> field_name_postprocessor = FieldNamePostprocessor(
        ...     mapping={
        ...         'class': 'type',
        ...     },
        ... )
        ...
        >>> gdf = field_name_postprocessor(gdf)
    """

    def __init__(
        self,
        mapping: dict,
    ) -> None:
        """
        Parameters:
            mapping: mapping of the field names (old field name: new field name)
        """
        self.mapping = mapping

    @classmethod
    def from_config(
        cls,
        config: FieldNamePostprocessorConfig,
    ) -> FieldNamePostprocessor:
        """Creates a field name postprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            field name postprocessor
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

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


class FieldNamePostprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `FieldNamePostprocessor`

    Attributes:
        mapping: mapping of the field names (old field name: new field name)
    """
    mapping: dict


class FillPostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that fills holes in the polygons"""

    def __init__(
        self,
        max_area: float,
    ) -> None:
        """
        Parameters:
            max_area: maximum area of the holes to retain in square meters
        """
        self.max_area = max_area

    @classmethod
    def from_config(
        cls,
        config: FillPostprocessorConfig,
    ) -> FillPostprocessor:
        """Creates a fill postprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            fill postprocessor
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

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


class FillPostprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `FillPostprocessor`

    Attributes:
        max_area: maximum area of the holes to retain in square meters
    """
    max_area: float


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

    @classmethod
    def from_config(
        cls,
        config: SievePostprocessorConfig,
    ) -> SievePostprocessor:
        """Creates a sieve postprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            sieve postprocessor
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

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


class SievePostprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SievePostprocessor`

    Attributes:
        min_area: minimum area of the polygons to retain in square meters
    """
    min_area: float


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

    @classmethod
    def from_config(
        cls,
        config: SimplifyPostprocessorConfig,
    ) -> SimplifyPostprocessor:
        """Creates a simplify postprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            simplify postprocessor
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

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


class SimplifyPostprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `SimplifyPostprocessor`

    Attributes:
        tolerance: tolerance of the Douglas-Peucker algorithm in meters (a lower value will result
            in less simplification, a higher value will result in more simplification,
            a value equal to the ground sampling distance is recommended)
    """
    tolerance: float


class ValuePostprocessor(GeodataPostprocessor):
    """Geodata postprocessor that maps the values of a field

    Examples:
        Assume the geodataframe has the values 0, 1 and 2 in the field 'class'.

        You can map the values 0, 1 and 2 to 'class_1', 'class_2' and 'class_3'.

        >>> value_postprocessor = ValuePostprocessor(
        ...     mapping={
        ...         0: 'class_1',
        ...         1: 'class_2',
        ...         2: 'class_3',
        ...     },
        ...     field_name='class',
        ... )
        ...
        >>> gdf = value_postprocessor(gdf)
    """

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

    @classmethod
    def from_config(
        cls,
        config: ValuePostprocessorConfig,
    ) -> ValuePostprocessor:
        """Creates a value postprocessor from the configuration.

        Parameters:
            config: configuration

        Returns:
            value postprocessor
        """
        # noinspection PyTypeChecker
        return super().from_config(config)

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


class ValuePostprocessorConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `ValuePostprocessor`

    Attributes:
        mapping: mapping of the values (old value: new value)
        field_name: name of the field
    """
    mapping: dict
    field_name: str
