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

import inspect
import pickle

import pytest

from aviary.core.exceptions import AviaryUserError
from aviary.core.vector import Vector
from aviary.core.vector_layer import VectorLayer
from tests.core.data.data_test_vector import (
    data_test_vector_bool,
    data_test_vector_contains,
    data_test_vector_eq,
    data_test_vector_getattr,
    data_test_vector_getitem,
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


def test_vector_layer_names(
    vector: Vector,
) -> None:
    expected = {
        'custom_1',
        'custom_2',
    }

    assert vector.layer_names == expected


@pytest.mark.parametrize(('other', 'expected'), data_test_vector_eq)
def test_vector_eq(
    other: object,
    expected: bool,
    vector: Vector,
) -> None:
    equals = vector == other

    assert equals is expected


def test_vector_len(
    vector: Vector,
) -> None:
    expected = 2

    assert len(vector) == expected


@pytest.mark.parametrize(('vector', 'expected'), data_test_vector_bool)
def test_vector_bool(
    vector: Vector,
    expected: bool,
) -> None:
    assert bool(vector) is expected


@pytest.mark.parametrize(('layer_name', 'expected'), data_test_vector_contains)
def test_vector_contains(
    layer_name: str,
    expected: bool,
    vector: Vector,
) -> None:
    contains = layer_name in vector

    assert contains is expected


@pytest.mark.parametrize(('layer_name', 'expected'), data_test_vector_getattr)
def test_vector_getattr(
    layer_name: str,
    expected: VectorLayer,
    vector: Vector,
) -> None:
    layer = getattr(vector, layer_name)

    assert layer == expected


@pytest.mark.parametrize(('layer_name', 'expected'), data_test_vector_getitem)
def test_vector_getitem(
    layer_name: str,
    expected: VectorLayer,
    vector: Vector,
) -> None:
    layer = vector[layer_name]

    assert layer == expected


def test_vector_iter(
    vector: Vector,
    vector_layers: list[VectorLayer],
) -> None:
    assert list(vector) == vector_layers


def test_vector_copy(
    vector: Vector,
) -> None:
    copied_vector = vector.copy()

    assert copied_vector == vector
    assert copied_vector.is_copied is True
    assert id(copied_vector) != id(vector)
    assert id(copied_vector.layers) != id(vector.layers)

    for copied_layer, layer in zip(copied_vector, vector, strict=True):
        assert id(copied_layer) != id(layer)

    assert id(copied_vector.metadata) != id(vector.metadata)
