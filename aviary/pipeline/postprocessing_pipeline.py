from __future__ import annotations

from pathlib import Path  # noqa: TCH003
from typing import TYPE_CHECKING, cast

import geopandas as gpd
import pydantic

from aviary.geodata.geodata_postprocessor import (  # noqa: F401,TCH001
    ClipPostprocessor,
    ClipPostprocessorConfig,
    CompositePostprocessor,
    CompositePostprocessorConfig,
    FieldNamePostprocessor,
    FieldNamePostprocessorConfig,
    FillPostprocessor,
    FillPostprocessorConfig,
    SievePostprocessor,
    SievePostprocessorConfig,
    SimplifyPostprocessor,
    SimplifyPostprocessorConfig,
    ValuePostprocessor,
    ValuePostprocessorConfig,
)

if TYPE_CHECKING:
    from aviary.geodata.geodata_postprocessor import GeodataPostprocessor


class PostprocessingPipeline:
    """Pre-built postprocessing pipeline"""

    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        geodata_postprocessor: GeodataPostprocessor,
        path: Path | None = None,
    ) -> None:
        """
        Parameters:
            gdf: geodataframe
            geodata_postprocessor: geodata postprocessor
            path: path to export the geodataframe (if None, the geodataframe is not exported)
        """
        self.gdf = gdf
        self.geodata_postprocessor = geodata_postprocessor
        self.path = path

    @classmethod
    def from_config(
        cls,
        config: PostprocessingPipelineConfig,
    ) -> PostprocessingPipeline:
        """Creates a postprocessing pipeline from the configuration.

        Parameters:
            config: configuration

        Returns:
            postprocessing pipeline
        """
        geodata_postprocessor_class = globals()[config.geodata_postprocessor_config.name]
        geodata_postprocessor = geodata_postprocessor_class.from_config(config.geodata_postprocessor_config.config)

        return cls(
            gdf=cast(gpd.GeoDataFrame, config.gdf),
            geodata_postprocessor=geodata_postprocessor,
            path=config.path,
        )

    def __call__(self) -> gpd.GeoDataFrame:  # pragma: no cover
        """Runs the postprocessing pipeline."""
        gdf = self.geodata_postprocessor(self.gdf)

        if self.path is not None:
            gdf.to_file(self.path, driver='GPKG')

        return gdf


class PostprocessingPipelineConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `PostprocessingPipeline`

    Attributes:
        gdf: path to the geodataframe
        geodata_postprocessor_config: configuration of the geodata postprocessor
        path: path to export the geodataframe
    """
    gdf: Path
    geodata_postprocessor_config: GeodataPostprocessorConfig = pydantic.Field(alias='geodata_postprocessor')
    path: Path

    # noinspection PyNestedDecorators
    @pydantic.field_validator('gdf')
    @classmethod
    def parse_gdf(
        cls,
        gdf: Path,
    ) -> gpd.GeoDataFrame:
        """Parses the geodataframe."""
        return gpd.read_file(gdf)


class GeodataPostprocessorConfig(pydantic.BaseModel):
    """Configuration for geodata postprocessors

    Attributes:
        name: name of the geodata postprocessor
        config: configuration of the geodata postprocessor
    """
    name: str
    config: (
        ClipPostprocessorConfig |
        CompositePostprocessorConfig |
        FieldNamePostprocessorConfig |
        FillPostprocessorConfig |
        SievePostprocessorConfig |
        SimplifyPostprocessorConfig |
        ValuePostprocessorConfig
    )
