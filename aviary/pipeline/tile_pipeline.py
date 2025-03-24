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
from aviary.tile.tile_fetcher import (
    TileFetcher,
    TileFetcherConfig,
    TileFetcherFactory,
)
from aviary.tile.tile_loader import TileLoader
from aviary.tile.tile_set import TileSet
from aviary.tile.tiles_processor import (
    TilesProcessor,
    TilesProcessorConfig,
    TilesProcessorFactory,
)


class TilePipeline:
    """Pre-built tile pipeline"""

    def __init__(
        self,
        grid: Grid,
        tile_fetcher: TileFetcher,
        tiles_processor: TilesProcessor,
        tile_loader_batch_size: int = 1,
        tile_loader_max_num_threads: int | None = None,
        tile_loader_num_prefetched_tiles: int = 0,
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
        config: TilePipelineConfig,
    ) -> TilePipeline:
        """Creates a tile pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Tile pipeline
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

        for tiles in track(tile_loader, description='Processing tiles'):
            _ = self._tiles_processor(tiles=tiles)


class TileLoaderConfig(pydantic.BaseModel):
    """Configuration for the tile loader in the tile pipeline

    Create the configuration from a config file:
        - Use null instead of None

    Example:
        You can create a configuration from a config file.

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

    Example:
        You can create a configuration from a config file.

        ``` yaml title="config.yaml"
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
    grid_config: GridConfig
    tile_fetcher_config: TileFetcherConfig
    tile_loader_config: TileLoaderConfig = pydantic.Field(default=TileLoaderConfig())
    tiles_processor_config: TilesProcessorConfig
    plugins_dir_path: Path | None = None


class TilePipelineFactory:
    """Factory for tile pipelines"""

    @staticmethod
    def create(
        config: TilePipelineConfig,
    ) -> TilePipeline:
        """Creates a tile pipeline from the configuration.

        Parameters:
            config: Configuration

        Returns:
            Tile pipeline
        """
        return TilePipeline.from_config(config=config)
