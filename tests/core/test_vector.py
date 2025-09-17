import inspect
import pickle

import pytest

from aviary.core.exceptions import AviaryUserError
from aviary.core.vector import Vector
from aviary.core.vector_layer import VectorLayer
from tests.core.data.data_test_vector import (
    data_test_vector_init,
    data_test_vector_init_exceptions,
)


@pytest.mark.parametrize(
    (
        'layers',
        'metadata',
        'copy',
        'expected_layers',
        'expected_metadata',
        'expected_copy',
    ),
    data_test_vector_init,
)
def test_vector_init(
    layers: list[VectorLayer],
    metadata: dict[str, object] | None,
    copy: bool,
    expected_layers: list[VectorLayer],
    expected_metadata: dict[str, object],
    expected_copy: bool,
) -> None:
    vector = Vector(
        layers=layers,
        metadata=metadata,
        copy=copy,
    )

    assert vector.layers == expected_layers
    assert vector.metadata == expected_metadata
    assert vector.is_copied is expected_copy


@pytest.mark.parametrize(('layers', 'message'), data_test_vector_init_exceptions)
def test_vector_init_exceptions(
    layers: list[VectorLayer],
    message: str,
) -> None:
    metadata = None
    copy = False

    with pytest.raises(AviaryUserError, match=message):
        _ = Vector(
            layers=layers,
            metadata=metadata,
            copy=copy,
        )


def test_vector_init_defaults() -> None:
    signature = inspect.signature(Vector)
    metadata = signature.parameters['metadata'].default
    copy = signature.parameters['copy'].default

    expected_metadata = None
    expected_copy = False

    assert metadata is expected_metadata
    assert copy is expected_copy


def test_vector_mutability_no_copy(
    vector_layers: list[VectorLayer],
    metadata: dict[str, object],
) -> None:
    copy = False

    vector = Vector(
        layers=vector_layers,
        metadata=metadata,
        copy=copy,
    )

    assert id(vector._layers) == id(vector_layers)

    for layer, layer_ in zip(vector, vector_layers, strict=True):
        assert id(layer) == id(layer_)

    assert id(vector.layers) == id(vector._layers)
    assert id(vector._metadata) == id(metadata)
    assert id(vector.metadata) == id(vector._metadata)


def test_vector_mutability_copy(
    vector_layers: list[VectorLayer],
    metadata: dict[str, object],
) -> None:
    copy = True

    vector = Vector(
        layers=vector_layers,
        metadata=metadata,
        copy=copy,
    )

    assert id(vector._layers) != id(vector_layers)

    for layer, layer_ in zip(vector, vector_layers, strict=True):
        assert id(layer) != id(layer_)

    assert id(vector.layers) == id(vector._layers)
    assert id(vector._metadata) != id(metadata)
    assert id(vector.metadata) == id(vector._metadata)


def test_vector_setters(
    vector: Vector,
) -> None:
    with pytest.raises(AttributeError):
        # noinspection PyPropertyAccess
        vector.layers = None


def test_vector_serializability(
    vector: Vector,
) -> None:
    serialized_vector = pickle.dumps(vector)
    deserialized_vector = pickle.loads(serialized_vector)  # noqa: S301

    assert vector == deserialized_vector
