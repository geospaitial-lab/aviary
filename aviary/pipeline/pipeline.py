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
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
)

if TYPE_CHECKING:
    from collections.abc import Callable

import pydantic
from loguru import logger
from rich.progress import track

if TYPE_CHECKING:
    from pydantic_core.core_schema import ValidationInfo

from aviary.core.exceptions import AviaryUserError
from aviary.core.grid import (
    Grid,
    GridConfig,
    _GridFactory,
)
from aviary.tile.tile_fetcher import (
    TileFetcher,
    TileFetcherConfig,
    _TileFetcherFactory,
)
from aviary.tile.tile_loader import TileLoader
from aviary.tile.tile_set import TileSet
from aviary.tile.tiles_processor import (
    TilesProcessor,
    TilesProcessorConfig,
    _TilesProcessorFactory,
)
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

_PACKAGE = 'aviary'


class Pipeline(Protocol):
    """Protocol for pipelines

    Pipelines are callables that define a pre-built sequence of components.

    Implemented pipelines:
        - `CompositePipeline`: Composes multiple pipelines
        - `TilePipeline`: Fetches and processes tiles
        - `VectorPipeline`: Loads and processes vectors
    """

    def __call__(self) -> None:
        """Runs the pipeline."""
        ...


class PipelineConfig(pydantic.BaseModel):
    """Configuration for pipelines

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'Pipeline'
        config:
          ...
        ```

    Attributes:
        package: Package -
            defaults to 'aviary'
        name: Name
        config: Configuration -
            defaults to None
    """
    package: str = 'aviary'
    name: str
    config: pydantic.BaseModel | None = None

    # noinspection PyNestedDecorators
    @pydantic.field_validator(
        'config',
        mode='before',
    )
    @classmethod
    def _validate_config(
        cls,
        value: Any,  # noqa: ANN401
        info: ValidationInfo,
    ) -> pydantic.BaseModel:
        package = info.data['package']
        name = info.data['name']
        key = (package, name)
        registry_entry = _PipelineFactory.registry.get(key)

        if registry_entry is None:
            message = (
                'Invalid config! '
                f'The pipeline {name} from {package} must be registered.'
            )
            raise ValueError(message)

        _, config_class = registry_entry

        if value is None:
            return config_class()

        if isinstance(value, config_class):
            return value

        return config_class(**value)


class _PipelineFactory:
    """Factory for pipelines"""
    registry: dict[tuple[str, str], tuple[type[Pipeline], type[pydantic.BaseModel]]] = {}  # noqa: RUF012

    @staticmethod
    def create(
        config: PipelineConfig,
    ) -> Pipeline:
        """Creates a pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Pipeline

        Raises:
            AviaryUserError: Invalid `config` (the pipeline is not registered)
        """
        key = (config.package, config.name)
        registry_entry = _PipelineFactory.registry.get(key)

        if registry_entry is None:
            message = (
                'Invalid config! '
                f'The pipeline {config.name} from {config.package} must be registered.'
            )
            raise AviaryUserError(message) from None

        pipeline_class, _ = registry_entry
        # noinspection PyUnresolvedReferences
        return pipeline_class.from_config(config=config.config)

    @staticmethod
    def register(
        pipeline_class: type[Pipeline],
        config_class: type[pydantic.BaseModel],
        package: str = _PACKAGE,
    ) -> None:
        """Registers a pipeline.

        Parameters:
            pipeline_class: Pipeline class
            config_class: Configuration class
            package: Package
        """
        key = (package, pipeline_class.__name__)
        _PipelineFactory.registry[key] = (pipeline_class, config_class)


def register_pipeline(
    config_class: type[pydantic.BaseModel],
) -> Callable:
    """Registers a pipeline.

    Parameters:
        config_class: Configuration class

    Returns:
        Decorator

    Raises:
        AviaryUserError: Invalid registration (the package name is equal to aviary)
    """
    def decorator(
        cls: type[Pipeline],
    ) -> type[Pipeline]:
        package = cls.__module__.split('.')[0]

        if package == _PACKAGE:
            message = (
                'Invalid registration! '
                f'The package name must be different from {_PACKAGE}.'
            )
            raise AviaryUserError(message)

        _PipelineFactory.register(
            pipeline_class=cls,
            config_class=config_class,
            package=package,
        )
        return cls
    return decorator


class CompositePipeline:
    """Pipeline that composes multiple pipelines

    Implements the `Pipeline` protocol.
    """

    def __init__(
        self,
        pipelines: list[Pipeline],
    ) -> None:
        """
        Parameters:
            pipelines: Pipelines
        """
        self._pipelines = pipelines

    @classmethod
    def from_config(
        cls,
        config: CompositePipelineConfig,
    ) -> CompositePipeline:
        """Creates a composite pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Composite pipeline
        """
        pipelines = [
            _PipelineFactory.create(config=pipeline_config)
            for pipeline_config in config.pipeline_configs
        ]
        return cls(
            pipelines=pipelines,
        )

    def __call__(self) -> None:
        """Runs the composite pipeline."""
        num_pipelines = len(self._pipelines)
        logger.info(
            'Starting composite pipeline with {} pipelines...',
            num_pipelines,
        )
        i_len = len(str(num_pipelines))
        composite_pipeline_start_time = time.perf_counter()

        for i, pipeline in enumerate(self._pipelines, start=1):
            logger.info(
                'Pipeline {:>{}} / {}:',
                i,
                i_len,
                num_pipelines,
            )
            pipeline()

        composite_pipeline_elapsed_time = time.perf_counter() - composite_pipeline_start_time
        composite_pipeline_average_time = composite_pipeline_elapsed_time / num_pipelines if num_pipelines else 0.
        logger.success(
            'Done with {} pipelines in {:.3f} s and {:.3f} s/pipeline.',
            num_pipelines,
            composite_pipeline_elapsed_time,
            composite_pipeline_average_time,
        )


class CompositePipelineConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `CompositePipeline`

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'CompositePipeline'
        config:
          pipeline_configs:
            - ...
            ...
        ```

    Attributes:
        pipeline_configs: Configurations of the pipelines
    """
    pipeline_configs: list[PipelineConfig]


_PipelineFactory.register(
    pipeline_class=CompositePipeline,
    config_class=CompositePipelineConfig,
    package=_PACKAGE,
)


class TilePipeline:
    """Pipeline that fetches and processes tiles

    Implements the `Pipeline` protocol.
    """

    def __init__(
        self,
        grid: Grid,
        tile_fetcher: TileFetcher,
        tiles_processor: TilesProcessor,
        tile_loader_batch_size: int = 1,
        tile_loader_max_num_threads: int | None = None,
        tile_loader_num_prefetched_tiles: int = 0,
        show_progress: bool = True,
    ) -> None:
        """
        Parameters:
            grid: Grid
            tile_fetcher: Tile fetcher
            tiles_processor: Tiles processor
            tile_loader_batch_size: Batch size
            tile_loader_max_num_threads: Maximum number of threads
            tile_loader_num_prefetched_tiles: Number of prefetched tiles
            show_progress: If True, show the progress in a progress bar
        """
        self._grid = grid
        self._tile_fetcher = tile_fetcher
        self._tiles_processor = tiles_processor
        self._tile_loader_batch_size = tile_loader_batch_size
        self._tile_loader_max_num_threads = tile_loader_max_num_threads
        self._tile_loader_num_prefetched_tiles = tile_loader_num_prefetched_tiles
        self._show_progress = show_progress

    @classmethod
    def from_config(
        cls,
        config: TilePipelineConfig,
    ) -> TilePipeline:
        """Creates a tile pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Tile pipeline
        """
        grid = _GridFactory.create(config=config.grid_config)
        tile_fetcher = _TileFetcherFactory.create(config=config.tile_fetcher_config)
        tiles_processor = _TilesProcessorFactory.create(config=config.tiles_processor_config)
        return cls(
            grid=grid,
            tile_fetcher=tile_fetcher,
            tiles_processor=tiles_processor,
            tile_loader_batch_size=config.tile_loader_config.batch_size,
            tile_loader_max_num_threads=config.tile_loader_config.max_num_threads,
            tile_loader_num_prefetched_tiles=config.tile_loader_config.num_prefetched_tiles,
            show_progress=config.show_progress,
        )

    def __call__(self) -> None:
        """Runs the tile pipeline."""
        tile_set = TileSet(
            grid=self._grid,
            tile_fetcher=self._tile_fetcher,
        )
        tile_loader = TileLoader(
            tile_set=tile_set,
            batch_size=self._tile_loader_batch_size,
            max_num_threads=self._tile_loader_max_num_threads,
            num_prefetched_tiles=self._tile_loader_num_prefetched_tiles,
        )

        num_tiles = len(tile_set)
        logger.info(
            'Starting tile pipeline with {} tiles...',
            num_tiles,
        )
        num_tiles = len(tile_loader)
        i_len = len(str(num_tiles))
        tile_pipeline_start_time = time.perf_counter()

        progress_bar = track(
            tile_loader,
            description='Processing tiles',
            disable=not self._show_progress,
        )

        for i, tiles in enumerate(progress_bar, start=1):
            batch_size = tiles.batch_size
            logger.info(
                'Processing {} tiles {:>{}} / {}...',
                batch_size,
                i,
                i_len,
                num_tiles,
            )
            start_time = time.perf_counter()

            _ = self._tiles_processor(tiles=tiles)

            elapsed_time = time.perf_counter() - start_time
            logger.success(
                'Processed  {} tiles {:>{}} / {} in {:.3f} s.',
                batch_size,
                i,
                i_len,
                num_tiles,
                elapsed_time,
            )

        tile_pipeline_elapsed_time = time.perf_counter() - tile_pipeline_start_time
        num_tiles = len(tile_set)
        tile_pipeline_average_time = tile_pipeline_elapsed_time / num_tiles if num_tiles else 0.
        logger.success(
            'Done with {} tiles in {:.3f} s and {:.3f} s/tile.',
            num_tiles,
            tile_pipeline_elapsed_time,
            tile_pipeline_average_time,
        )


class TileLoaderConfig(pydantic.BaseModel):
    """Configuration for the tile loader in the tile pipeline

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        batch_size: 1
        max_num_threads: null
        num_prefetched_tiles: 0
        ```

    Attributes:
        batch_size: Batch size -
            defaults to 1
        max_num_threads: Maximum number of threads -
            defaults to None
        num_prefetched_tiles: Number of prefetched tiles -
            defaults to 0
    """
    batch_size: int = 1
    max_num_threads: int | None = None
    num_prefetched_tiles: int = 0


class TilePipelineConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `TilePipeline`

    Create the configuration from a config file:
        - Use null instead of None
        - Use false or true instead of False or True

    Example:
        You can create the configuration from a config file.

        ``` yaml title="config.yaml"
        package: 'aviary'
        name: 'TilePipeline'
        config:
          plugins_dir_path: null
          show_progress: true

          grid_config:
            ...

          tile_fetcher_config:
            ...

          tile_loader_config:
            batch_size: 1
            max_num_threads: null
            num_prefetched_tiles: 0

          tiles_processor_config:
            ...
        ```

    Attributes:
        plugins_dir_path: Path to the plugins directory -
            defaults to None
        show_progress: If True, show the progress in a progress bar -
            defaults to True
        grid_config: Configuration for the grid
        tile_fetcher_config: Configuration for the tile fetcher
        tile_loader_config: Configuration for the tile loader -
            defaults to `TileLoaderConfig`
        tiles_processor_config: Configuration for the tiles processor
    """
    plugins_dir_path: Path | None = None
    show_progress: bool = True
    grid_config: GridConfig
    tile_fetcher_config: TileFetcherConfig
    tile_loader_config: TileLoaderConfig = pydantic.Field(default=TileLoaderConfig())
    tiles_processor_config: TilesProcessorConfig


_PipelineFactory.register(
    pipeline_class=TilePipeline,
    config_class=TilePipelineConfig,
    package=_PACKAGE,
)


class VectorPipeline:
    """Pipeline that loads and processes vectors

    Implements the `Pipeline` protocol.
    """

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
        package: 'aviary'
        name: 'VectorPipeline'
        config:
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


_PipelineFactory.register(
    pipeline_class=VectorPipeline,
    config_class=VectorPipelineConfig,
    package=_PACKAGE,
)
