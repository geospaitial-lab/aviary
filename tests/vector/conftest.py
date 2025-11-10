#  Copyright (C) 2024-2025 Marius Maryniak
#
#  This file is part of aviary.
#
#  aviary is free software: you can redistribute it and / or modify it under the terms of the
#  GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
#  aviary is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with aviary.
#  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from aviary.vector.vector_loader import (
    CompositeLoader,
    GPKGLoader,
    VectorLoader,
)


@pytest.fixture(scope='session')
def composite_loader() -> CompositeLoader:
    vector_loaders = [
        MagicMock(spec=VectorLoader),
        MagicMock(spec=VectorLoader),
        MagicMock(spec=VectorLoader),
    ]
    max_num_threads = None
    return CompositeLoader(
        vector_loaders=vector_loaders,
        max_num_threads=max_num_threads,
    )


@pytest.fixture(scope='session')
def gpkg_loader() -> GPKGLoader:
    path = Path('test/test.gpkg')
    layer_name = 'custom'
    max_num_threads = None
    return GPKGLoader(
        path=path,
        layer_name=layer_name,
        max_num_threads=max_num_threads,
    )
