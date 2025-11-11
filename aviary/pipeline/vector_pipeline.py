#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and/or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import time
from pathlib import Path

import pydantic
from loguru import logger

from aviary.vector.vector_loader import (
    VectorLoader,
    VectorLoaderConfig,
    _VectorLoaderFactory,
)
from aviary.vector.vector_processor import (
    VectorProcessor,
    VectorProcessorConfig,
    _VectorProcessorFactory,
)


class VectorPipeline:
    """Pre-built vector pipeline"""

    def __init__(
        self,
        vector_loader: VectorLoader,
        vector_processor: VectorProcessor,
    ) -> None:
        """
        Parameters:
            vector_loader: Vector loader
            vector_processor: Vector processor
        """
        self._vector_loader = vector_loader
        self._vector_processor = vector_processor

    @classmethod
    def from_config(
        cls,
        config: VectorPipelineConfig,
    ) -> VectorPipeline:
        """Creates a vector pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Vector pipeline
        """
        vector_loader = _VectorLoaderFactory.create(config=config.vector_loader_config)
        vector_processor = _VectorProcessorFactory.create(config=config.vector_processor_config)
        return cls(
            vector_loader=vector_loader,
            vector_processor=vector_processor,
        )

    def __call__(self) -> None:
        """Runs the vector pipeline."""
        logger.info('Starting vector pipeline...')
        vector_pipeline_start_time = time.perf_counter()

        vector = self._vector_loader()
        _ = self._vector_processor(vector=vector)

        vector_pipeline_elapsed_time = time.perf_counter() - vector_pipeline_start_time
        logger.success(
            'Done in {:.3f} s.',
            vector_pipeline_elapsed_time,
        )


class VectorPipelineConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `VectorPipeline`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        plugins_dir_path: null

        vector_loader_config:
          ...

        vector_processor_config:
          ...
        ```

    Attributes:
        plugins_dir_path: Path to the plugins directory -
            defaults to None
        vector_loader_config: Configuration for the vector loader
        vector_processor_config: Configuration for the vector processor
    """
    plugins_dir_path: Path | None = None
    vector_loader_config: VectorLoaderConfig
    vector_processor_config: VectorProcessorConfig


class _VectorPipelineFactory:
    """Factory for vector pipelines"""

    @staticmethod
    def create(
        config: VectorPipelineConfig,
    ) -> VectorPipeline:
        """Creates a vector pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Vector pipeline
        """
        return VectorPipeline.from_config(config=config)
