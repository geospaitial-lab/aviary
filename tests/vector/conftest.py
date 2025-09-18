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
    return GPKGLoader(
        path=path,
        layer_name=layer_name,
    )
