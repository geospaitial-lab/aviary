from __future__ import annotations

from pathlib import Path

import pydantic
from rich.progress import track

# noinspection PyProtectedMember
from aviary._utils.plugins import register_plugins
from aviary.core.grid import (
    Grid,
    GridConfig,
    GridFactory,
)
from aviary.inference.tile_fetcher import (
    TileFetcher,
    TileFetcherConfig,
    TileFetcherFactory,
)
from aviary.inference.tile_loader import TileLoader
from aviary.inference.tile_set import TileSet
from aviary.inference.tiles_processor import (
    TilesProcessor,
    TilesProcessorConfig,
    TilesProcessorFactory,
)


class InferencePipeline:
    """Pre-built inference pipeline"""

    def __init__(
        self,
        grid: Grid,
        tile_fetcher: TileFetcher,
        tiles_processor: TilesProcessor,
        tile_loader_batch_size: int = 1,
        tile_loader_max_num_threads: int | None = None,
        tile_loader_num_prefetched_tiles: int = 1,
        plugins_dir_path: Path | None = None,
    ) -> None:
        """
        Parameters:
            grid: Grid
            tile_fetcher: Tile fetcher
            tiles_processor: Tiles processor
            tile_loader_batch_size: Batch size
            tile_loader_max_num_threads: Maximum number of threads
            tile_loader_num_prefetched_tiles: Number of prefetched tiles
            plugins_dir_path: Path to the plugins directory
        """
        self._grid = grid
        self._tile_fetcher = tile_fetcher
        self._tiles_processor = tiles_processor
        self._tile_loader_batch_size = tile_loader_batch_size
        self._tile_loader_max_num_threads = tile_loader_max_num_threads
        self._tile_loader_num_prefetched_tiles = tile_loader_num_prefetched_tiles
        self._plugins_dir_path = plugins_dir_path

        if self._plugins_dir_path is not None:
            register_plugins(plugins_dir_path=self._plugins_dir_path)

    @classmethod
    def from_config(
        cls,
        config: InferencePipelineConfig,
    ) -> InferencePipeline:
        """Creates an inference pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Inference pipeline
        """
        grid = GridFactory.create(config=config.grid_config)
        tile_fetcher = TileFetcherFactory.create(config=config.tile_fetcher_config)
        tiles_processor = TilesProcessorFactory.create(config=config.tiles_processor_config)
        return cls(
            grid=grid,
            tile_fetcher=tile_fetcher,
            tiles_processor=tiles_processor,
            tile_loader_batch_size=config.tile_loader_config.batch_size,
            tile_loader_max_num_threads=config.tile_loader_config.max_num_threads,
            tile_loader_num_prefetched_tiles=config.tile_loader_config.num_prefetched_tiles,
            plugins_dir_path=config.plugins_dir_path,
        )

    def __call__(self) -> None:
        """Runs the inference pipeline."""
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

        for tiles in track(tile_loader, description='Processing tiles'):
            _ = self._tiles_processor(tiles=tiles)


class TileLoaderConfig(pydantic.BaseModel):
    """Configuration for the tile loader in the inference pipeline

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create a configuration from a config file.

        ``` yaml title="config.yaml"
        batch_size: 1
        max_num_threads: null
        num_prefetched_tiles: 1
        ```

    Attributes:
        batch_size: Batch size -
            defaults to 1
        max_num_threads: Maximum number of threads -
            defaults to None
        num_prefetched_tiles: Number of prefetched tiles -
            defaults to 1
    """
    batch_size: int = 1
    max_num_threads: int | None = None
    num_prefetched_tiles: int = 1


class InferencePipelineConfig(pydantic.BaseModel):
    """Configuration for the `from_config` class method of `InferencePipeline`

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create a configuration from a config file.

        ``` yaml title="config.yaml"
        grid:
          ...
        tile_fetcher:
          ...
        tile_loader:
          batch_size: 1
          max_num_threads: null
          num_prefetched_tiles: 1
        tiles_processor:
          ...
        plugins_dir_path: null
        ```

    Attributes:
        grid_config: Configuration for the grid
        tile_fetcher_config: Configuration for the tile fetcher
        tile_loader_config: Configuration for the tile loader -
            defaults to `TileLoaderConfig`
        tiles_processor_config: Configuration for the tiles processor
        plugins_dir_path: Path to the plugins directory -
            defaults to None
    """
    grid_config: GridConfig = pydantic.Field(validation_alias='grid')
    tile_fetcher_config: TileFetcherConfig = pydantic.Field(validation_alias='tile_fetcher')
    tile_loader_config: TileLoaderConfig = pydantic.Field(
        default=TileLoaderConfig(),
        validation_alias='tile_loader',
    )
    tiles_processor_config: TilesProcessorConfig = pydantic.Field(validation_alias='tiles_processor')
    plugins_dir_path: Path | None = None


class InferencePipelineFactory:
    """Factory for inference pipelines"""

    @staticmethod
    def create(
        config: InferencePipelineConfig,
    ) -> InferencePipeline:
        """Creates an inference pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Inference pipeline
        """
        return InferencePipeline.from_config(config=config)
