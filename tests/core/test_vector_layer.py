import inspect
import pickle

import geopandas as gpd
import geopandas.testing
import pytest

from aviary.core.vector_layer import VectorLayer
from tests.core.data.data_test_vector_layer import (
    data_test_vector_layer_eq,
    data_test_vector_layer_init,
)


@pytest.mark.parametrize(
    (
        'data',
        'name',
        'metadata',
        'copy',
        'expected_data',
        'expected_name',
        'expected_metadata',
        'expected_copy',
    ),
    data_test_vector_layer_init,
)
def test_vector_layer_init(
    data: gpd.GeoDataFrame,
    name: str,
    metadata: dict[str, object] | None,
    copy: bool,
    expected_data: gpd.GeoDataFrame,
    expected_name: str,
    expected_metadata: dict[str, object],
    expected_copy: bool,
) -> None:
    vector_layer = VectorLayer(
        data=data,
        name=name,
        metadata=metadata,
        copy=copy,
    )

    gpd.testing.assert_geodataframe_equal(vector_layer.data, expected_data)
    assert vector_layer.name == expected_name
    assert vector_layer.metadata == expected_metadata
    assert vector_layer.is_copied is expected_copy


def test_vector_layer_init_defaults() -> None:
    signature = inspect.signature(VectorLayer)
    metadata = signature.parameters['metadata'].default
    copy = signature.parameters['copy'].default

    expected_metadata = None
    expected_copy = False

    assert metadata is expected_metadata
    assert copy is expected_copy


def test_vector_layer_mutability_no_copy(
    vector_layer_data: gpd.GeoDataFrame,
    metadata: dict[str, object],
) -> None:
    name = 'custom'
    copy = False

    vector_layer = VectorLayer(
        data=vector_layer_data,
        name=name,
        metadata=metadata,
        copy=copy,
    )

    assert id(vector_layer._data) == id(vector_layer_data)
    assert id(vector_layer.data) == id(vector_layer._data)
    assert id(vector_layer._metadata) == id(metadata)
    assert id(vector_layer.metadata) == id(vector_layer._metadata)


def test_vector_layer_mutability_copy(
    vector_layer_data: gpd.GeoDataFrame,
    metadata: dict[str, object],
) -> None:
    name = 'custom'
    copy = True

    vector_layer = VectorLayer(
        data=vector_layer_data,
        name=name,
        metadata=metadata,
        copy=copy,
    )

    assert id(vector_layer._data) != id(vector_layer_data)
    assert id(vector_layer.data) == id(vector_layer._data)
    assert id(vector_layer._metadata) != id(metadata)
    assert id(vector_layer.metadata) == id(vector_layer._metadata)


def test_vector_layer_setters(
    vector_layer: VectorLayer,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        vector_layer.data = None


def test_vector_layer_serializability(
    vector_layer: VectorLayer,
) -> None:
    serialized_vector_layer = pickle.dumps(vector_layer)
    deserialized_vector_layer = pickle.loads(serialized_vector_layer)  # noqa: S301

    assert vector_layer == deserialized_vector_layer


@pytest.mark.parametrize(('other', 'expected'), data_test_vector_layer_eq)
def test_vector_layer_eq(
    other: object,
    expected: bool,
    vector_layer: VectorLayer,
) -> None:
    equals = vector_layer == other

    assert equals is expected


def test_vector_layer_len(
    vector_layer: VectorLayer,
) -> None:
    expected = 4

    assert len(vector_layer) == expected


def test_vector_layer_copy(
    vector_layer: VectorLayer,
) -> None:
    copied_vector_layer = vector_layer.copy()

    assert copied_vector_layer == vector_layer
    assert copied_vector_layer.is_copied is True
    assert id(copied_vector_layer) != id(vector_layer)
    assert id(copied_vector_layer.data) != id(vector_layer.data)
    assert id(copied_vector_layer.metadata) != id(vector_layer.metadata)
