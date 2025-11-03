from __future__ import annotations

from typing import TYPE_CHECKING

from aviary.core.vector import Vector

if TYPE_CHECKING:
    from aviary.vector import VectorProcessor


def aggregate_processor(
    vector: Vector,
    layer_name: str,
    aggregation_layer_name: str,
    field: str,
    classes: list[str | int] | None = None,
    background_class: str | int | None = None,
    absolute_area_field_suffix: str = 'absolute_area',
    relative_area_field_suffix: str = 'relative_area',
    new_aggregation_layer_name: str | None = None,
) -> Vector:
    """Aggregates the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        aggregation_layer_name: Aggregation layer name
        field: Field
        classes: Classes (if None, the classes are inferred from the layer)
        background_class: Background class (if None, the background class is ignored)
        absolute_area_field_suffix: Suffix of the absolute area field
        relative_area_field_suffix: Suffix of the relative area field
        new_aggregation_layer_name: New aggregation layer name

    Returns:
        Vector
    """


def clip_processor(
    vector: Vector,
    layer_name: str,
    mask_layer_name: str,
    new_layer_name: str | None = None,
) -> Vector:
    """Clips the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        mask_layer_name: Mask layer name
        new_layer_name: New layer name

    Returns:
        Vector
    """


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


def fill_processor(
    vector: Vector,
    layer_name: str,
    threshold: float,
    new_layer_name: str | None = None,
) -> Vector:
    """Fills the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        threshold: Threshold (the maximum area of the hole within a polygon to retain) in square meters
        new_layer_name: New layer name

    Returns:
        Vector
    """


def map_field_processor(
    vector: Vector,
    layer_name: str,
    field: str,
    mapping: dict[object, object],
    new_layer_name: str | None = None,
) -> Vector:
    """Maps the field of the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        field: Field
        mapping: Mapping of the values
        new_layer_name: New layer name

    Returns:
        Vector
    """


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


def rename_fields_processor(
    vector: Vector,
    layer_name: str,
    mapping: dict[object, object],
    new_layer_name: str | None = None,
) -> Vector:
    """Renames the fields of the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        mapping: Mapping of the field names
        new_layer_name: New layer name

    Returns:
        Vector
    """


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


def sieve_processor(
    vector: Vector,
    layer_name: str,
    threshold: float,
    new_layer_name: str | None = None,
) -> Vector:
    """Sieves the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        threshold: Threshold (the minimum area of the polygon to retain) in square meters
        new_layer_name: New layer name

    Returns:
        Vector
    """


def simplify_processor(
    vector: Vector,
    layer_name: str,
    threshold: float,
    new_layer_name: str | None = None,
) -> Vector:
    """Simplifies the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        threshold: Threshold (the minimum area of the triangle defined by three consecutive vertices to retain)
            in square meters
        new_layer_name: New layer name

    Returns:
        Vector
    """
