import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aviary.vector.vector_loader import (
    CompositeLoader,
    GPKGLoader,
    GPKGLoaderConfig,
    VectorLoader,
)


def test_composite_loader_init() -> None:
    vector_loaders = [
        MagicMock(spec=VectorLoader),
        MagicMock(spec=VectorLoader),
        MagicMock(spec=VectorLoader),
    ]
    max_num_threads = None

    composite_loader = CompositeLoader(
        vector_loaders=vector_loaders,
        max_num_threads=max_num_threads,
    )

    assert composite_loader._vector_loaders == vector_loaders
    assert composite_loader._max_num_threads == max_num_threads


def test_composite_loader_init_defaults() -> None:
    signature = inspect.signature(CompositeLoader)
    max_num_threads = signature.parameters['max_num_threads'].default

    expected_max_num_threads = None

    assert max_num_threads == expected_max_num_threads


@pytest.mark.skip(reason='Not implemented')
def test_composite_loader_from_config() -> None:
    pass


@patch('aviary.vector.vector_loader.composite_loader')
def test_composite_loader_call(
    mocked_composite_loader: MagicMock,
    composite_loader: CompositeLoader,
) -> None:
    expected = 'expected'
    mocked_composite_loader.return_value = expected

    vector = composite_loader()

    assert vector == expected
    mocked_composite_loader.assert_called_once_with(
        vector_loaders=composite_loader._vector_loaders,
        max_num_threads=composite_loader._max_num_threads,
    )


def test_gpkg_loader_init() -> None:
    path = Path('test/test.gpkg')
    layer_name = 'custom'

    gpkg_loader = GPKGLoader(
        path=path,
        layer_name=layer_name,
    )

    assert gpkg_loader._path == path
    assert gpkg_loader._layer_name == layer_name


def test_gpkg_loader_from_config() -> None:
    path = Path('test/test.gpkg')
    layer_name = 'custom'
    gpkg_loader_config = GPKGLoaderConfig(
        path=path,
        layer_name=layer_name,
    )

    gpkg_loader = GPKGLoader.from_config(gpkg_loader_config)

    assert gpkg_loader._path == path
    assert gpkg_loader._layer_name == layer_name


@patch('aviary.vector.vector_loader.gpkg_loader')
def test_gpkg_loader_call(
    mocked_gpkg_loader: MagicMock,
    gpkg_loader: GPKGLoader,
) -> None:
    expected = 'expected'
    mocked_gpkg_loader.return_value = expected

    vector = gpkg_loader()

    assert vector == expected
    mocked_gpkg_loader.assert_called_once_with(
        path=gpkg_loader._path,
        layer_name=gpkg_loader._layer_name,
    )
