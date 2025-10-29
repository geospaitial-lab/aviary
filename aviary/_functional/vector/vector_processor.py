from __future__ import annotations

from typing import TYPE_CHECKING

from aviary.core.vector import Vector

if TYPE_CHECKING:
    from aviary.vector import VectorProcessor


def copy_processor(
    vector: Vector,
    layer_name: str,
    new_layer_name: str | None = None,
) -> Vector:
    """Copies the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        new_layer_name: New layer name

    Returns:
        Vector
    """
    if new_layer_name is None:
        return vector

    layer = vector[layer_name]
    layer = layer.copy()

    layer.name = new_layer_name
    return vector.append(
        layers=layer,
        inplace=True,
    )


def parallel_composite_processor(
    vector: Vector,
    vector_processors: list[VectorProcessor],
) -> Vector:
    """Processes the vector with each vector processor.

    Parameters:
        vector: Vector
        vector_processors: Vector processors

    Returns:
        Vector
    """
    vector = [
        vector_processor(vector=vector.copy())
        for vector_processor in vector_processors
    ]
    return Vector.from_vectors(
        vectors=vector,
        copy=False,
    )


def query_processor(
    vector: Vector,
    layer_name: str,
    query_string: str,
    new_layer_name: str | None = None,
) -> Vector:
    """Queries the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        query_string: Query string based on the pandas query syntax
        new_layer_name: New layer name

    Returns:
        Vector
    """
    layer = vector[layer_name]

    if new_layer_name is None:
        layer.query(
            query_string=query_string,
            inplace=True,
        )
        return vector

    layer = layer.query(
        query_string=query_string,
        inplace=False,
    )

    layer.name = new_layer_name
    return vector.append(
        layers=layer,
        inplace=True,
    )


def remove_processor(
    vector: Vector,
    layer_names: str | set[str] | bool | None = True,
) -> Vector:
    """Removes the layers.

    Parameters:
        vector: Vector
        layer_names: Layer name, layer names, no layers (False or None), or all layers (True)

    Returns:
        Vector
    """
    return vector.remove(
        layer_names=layer_names,
        inplace=True,
    )


def select_processor(
    vector: Vector,
    layer_names: str | set[str] | bool | None = True,
) -> Vector:
    """Selects the layers.

    Parameters:
        vector: Vector
        layer_names: Layer name, layer names, no layers (False or None), or all layers (True)

    Returns:
        Vector
    """
    return vector.select(
        layer_names=layer_names,
        inplace=True,
    )


def sequential_composite_processor(
    vector: Vector,
    vector_processors: list[VectorProcessor],
) -> Vector:
    """Processes the vector with each vector processor.

    Parameters:
        vector: Vector
        vector_processors: Vector processors

    Returns:
        Vector
    """
    for vector_processor in vector_processors:
        vector = vector_processor(vector=vector)

    return vector
