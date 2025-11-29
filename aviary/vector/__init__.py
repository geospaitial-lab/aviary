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

from .vector_exporter import (
    VectorExporter,
    VectorExporterConfig,
)
from .vector_loader import (
    BoundingBoxLoader,
    BoundingBoxLoaderConfig,
    CompositeLoader,
    CompositeLoaderConfig,
    GeoJSONLoader,
    GeoJSONLoaderConfig,
    GPKGLoader,
    GPKGLoaderConfig,
    VectorLoader,
    VectorLoaderConfig,
    register_vector_loader,
)
from .vector_processor import (
    AggregateProcessor,
    AggregateProcessorConfig,
    ClipProcessor,
    ClipProcessorConfig,
    CopyProcessor,
    CopyProcessorConfig,
    FillProcessor,
    FillProcessorConfig,
    MapFieldProcessor,
    MapFieldProcessorConfig,
    ParallelCompositeProcessor,
    ParallelCompositeProcessorConfig,
    QueryProcessor,
    QueryProcessorConfig,
    RemoveProcessor,
    RemoveProcessorConfig,
    RenameFieldsProcessor,
    RenameFieldsProcessorConfig,
    SelectProcessor,
    SelectProcessorConfig,
    SequentialCompositeProcessor,
    SequentialCompositeProcessorConfig,
    SieveProcessor,
    SieveProcessorConfig,
    SimplifyProcessor,
    SimplifyProcessorConfig,
    VectorProcessor,
    VectorProcessorConfig,
    register_vector_processor,
)

__all__ = [
    'AggregateProcessor',
    'AggregateProcessorConfig',
    'BoundingBoxLoader',
    'BoundingBoxLoaderConfig',
    'ClipProcessor',
    'ClipProcessorConfig',
    'CompositeLoader',
    'CompositeLoaderConfig',
    'CopyProcessor',
    'CopyProcessorConfig',
    'FillProcessor',
    'FillProcessorConfig',
    'GPKGLoader',
    'GPKGLoaderConfig',
    'GeoJSONLoader',
    'GeoJSONLoaderConfig',
    'MapFieldProcessor',
    'MapFieldProcessorConfig',
    'ParallelCompositeProcessor',
    'ParallelCompositeProcessorConfig',
    'QueryProcessor',
    'QueryProcessorConfig',
    'RemoveProcessor',
    'RemoveProcessorConfig',
    'RenameFieldsProcessor',
    'RenameFieldsProcessorConfig',
    'SelectProcessor',
    'SelectProcessorConfig',
    'SequentialCompositeProcessor',
    'SequentialCompositeProcessorConfig',
    'SieveProcessor',
    'SieveProcessorConfig',
    'SimplifyProcessor',
    'SimplifyProcessorConfig',
    'VectorExporter',
    'VectorExporterConfig',
    'VectorLoader',
    'VectorLoaderConfig',
    'VectorProcessor',
    'VectorProcessorConfig',
    'register_vector_loader',
    'register_vector_processor',
]
