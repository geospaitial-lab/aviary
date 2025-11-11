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
from rich.progress import track

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


class _TilePipelineFactory:
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
