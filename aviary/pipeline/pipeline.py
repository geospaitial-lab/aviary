from __future__ import annotations

import time
from pathlib import Path

import pydantic
from loguru import logger

from aviary.pipeline.tile_pipeline import (
    TilePipeline,
    TilePipelineConfig,
    _TilePipelineFactory,
)
from aviary.pipeline.vector_pipeline import (
    VectorPipeline,
    VectorPipelineConfig,
    _VectorPipelineFactory,
)


class Pipeline:
    """Pre-built pipeline"""

    def __init__(
        self,
        tile_pipeline: TilePipeline,
        vector_pipeline: VectorPipeline,
    ) -> None:
        """
        Parameters:
            tile_pipeline: Tile pipeline
            vector_pipeline: Vector pipeline
        """
        self._tile_pipeline = tile_pipeline
        self._vector_pipeline = vector_pipeline

    @classmethod
    def from_config(
        cls,
        config: PipelineConfig,
    ) -> Pipeline:
        """Creates a pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Pipeline
        """
        tile_pipeline = _TilePipelineFactory.create(config=config.tile_pipeline_config)
        vector_pipeline = _VectorPipelineFactory.create(config=config.vector_pipeline_config)
        return cls(
            tile_pipeline=tile_pipeline,
            vector_pipeline=vector_pipeline,
        )

    def __call__(self) -> None:
        """Runs the pipeline."""
        logger.info('Starting pipeline...')
        pipeline_start_time = time.perf_counter()

        self._tile_pipeline()
        self._vector_pipeline()

        pipeline_elapsed_time = time.perf_counter() - pipeline_start_time
        logger.success(
            'Done in {:.3f} s.',
            pipeline_elapsed_time,
        )


class PipelineConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `Pipeline`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        plugins_dir_path: null

        tile_pipeline_config:
          ...

        vector_pipeline_config:
          ...
        ```

    Attributes:
        plugins_dir_path: Path to the plugins directory -
            defaults to None
        tile_pipeline_config: Configuration for the tile pipeline
        vector_pipeline_config: Configuration for the vector pipeline
    """
    plugins_dir_path: Path | None = None
    tile_pipeline_config: TilePipelineConfig
    vector_pipeline_config: VectorPipelineConfig


class _PipelineFactory:
    """Factory for pipelines"""

    @staticmethod
    def create(
        config: PipelineConfig,
    ) -> Pipeline:
        """Creates a pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Pipeline
        """
        return Pipeline.from_config(config=config)
