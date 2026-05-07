#  Copyright (C) 2024-2026 Marius Maryniak
#  Copyright (C) 2026 Alexander Roß
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

from .tile_fetcher import (
    CompositeFetcher,
    CompositeFetcherConfig,
    GPKGFetcher,
    GPKGFetcherConfig,
    TileFetcher,
    TileFetcherConfig,
    VRTFetcher,
    VRTFetcherConfig,
    WMSFetcher,
    WMSFetcherConfig,
    register_tile_fetcher,
)
from .tile_loader import TileLoader
from .tile_set import TileSet
from .tiles_exporter import (
    GridExporter,
    GridExporterConfig,
    RasterExporter,
    RasterExporterConfig,
    VectorExporter,
    VectorExporterConfig,
)
from .tiles_processor import (
    AspectProcessor,
    AspectProcessorConfig,
    CopyProcessor,
    CopyProcessorConfig,
    ExpressionProcessor,
    ExpressionProcessorConfig,
    HillshadeProcessor,
    HillshadeProcessorConfig,
    NormalizeProcessor,
    NormalizeProcessorConfig,
    ParallelCompositeProcessor,
    ParallelCompositeProcessorConfig,
    RemoveBufferProcessor,
    RemoveBufferProcessorConfig,
    RemoveProcessor,
    RemoveProcessorConfig,
    SelectProcessor,
    SelectProcessorConfig,
    SequentialCompositeProcessor,
    SequentialCompositeProcessorConfig,
    SlopeProcessor,
    SlopeProcessorConfig,
    StandardizeProcessor,
    StandardizeProcessorConfig,
    TilesProcessor,
    TilesProcessorConfig,
    VectorizeProcessor,
    VectorizeProcessorConfig,
    register_tiles_processor,
)

__all__ = [
    'AspectProcessor',
    'AspectProcessorConfig',
    'CompositeFetcher',
    'CompositeFetcherConfig',
    'CopyProcessor',
    'CopyProcessorConfig',
    'ExpressionProcessor',
    'ExpressionProcessorConfig',
    'GPKGFetcher',
    'GPKGFetcherConfig',
    'GridExporter',
    'GridExporterConfig',
    'HillshadeProcessor',
    'HillshadeProcessorConfig',
    'NormalizeProcessor',
    'NormalizeProcessorConfig',
    'ParallelCompositeProcessor',
    'ParallelCompositeProcessorConfig',
    'RasterExporter',
    'RasterExporterConfig',
    'RemoveBufferProcessor',
    'RemoveBufferProcessorConfig',
    'RemoveProcessor',
    'RemoveProcessorConfig',
    'SelectProcessor',
    'SelectProcessorConfig',
    'SequentialCompositeProcessor',
    'SequentialCompositeProcessorConfig',
    'SlopeProcessor',
    'SlopeProcessorConfig',
    'StandardizeProcessor',
    'StandardizeProcessorConfig',
    'TileFetcher',
    'TileFetcherConfig',
    'TileLoader',
    'TileSet',
    'TilesProcessor',
    'TilesProcessorConfig',
    'VRTFetcher',
    'VRTFetcherConfig',
    'VectorExporter',
    'VectorExporterConfig',
    'VectorizeProcessor',
    'VectorizeProcessorConfig',
    'WMSFetcher',
    'WMSFetcherConfig',
    'register_tile_fetcher',
    'register_tiles_processor',
]
