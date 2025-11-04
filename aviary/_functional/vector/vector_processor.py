from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import geopandas as gpd
from shapely.geometry import Polygon

from aviary.core.vector import Vector

if TYPE_CHECKING:
    from aviary.vector import VectorProcessor


def _process_data(
    vector: Vector,
    layer_name: str,
    process_data: Callable,
    new_layer_name: str | None = None,
) -> Vector:
    """Processes the data of the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        process_data: Function to process the data
        new_layer_name: New layer name

    Returns:
        Vector
    """
    layer = vector[layer_name]

    if new_layer_name is not None:
        layer = layer.copy()

    data = layer.data

    data = process_data(data=data)

    layer._data = data  # noqa: SLF001

    if new_layer_name is not None:
        layer.name = new_layer_name
        return vector.append(
            layers=layer,
            inplace=True,
        )

    return vector


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
    return _process_data(
        vector=vector,
        layer_name=layer_name,
        process_data=lambda data: _clip_data(
            data=data,
            vector=vector,
            mask_layer_name=mask_layer_name,
        ),
        new_layer_name=new_layer_name,
    )


def _clip_data(
    data: gpd.GeoDataFrame,
    vector: Vector,
    mask_layer_name: str,
) -> gpd.GeoDataFrame:
    """Clips the data.

    Parameters:
        data: Data
        vector: Vector
        mask_layer_name: Mask layer name

    Returns:
        Data
    """
    mask = vector[mask_layer_name]

    mask_data = mask.data

    data = gpd.clip(
        gdf=data,
        mask=mask_data,
        keep_geom_type=True,
    )
    return data.reset_index(drop=True)


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
    return _process_data(
        vector=vector,
        layer_name=layer_name,
        process_data=lambda data: _fill_data(
            data=data,
            threshold=threshold,
        ),
        new_layer_name=new_layer_name,
    )


def _fill_data(
    data: gpd.GeoDataFrame,
    threshold: float,
) -> gpd.GeoDataFrame:
    """Fills the data.

    Parameters:
        data: Data
        threshold: Threshold (the maximum area of the hole within a polygon to retain) in square meters

    Returns:
        Data
    """
    data = data.explode()
    data.geometry = data.apply(
        lambda row: _fill_polygon(
            polygon=row.geometry,
            threshold=threshold,
        ),
        axis=1,
    )
    return data


def _fill_polygon(
    polygon: Polygon,
    threshold: float,
) -> Polygon:
    """Fills the polygon.

    Parameters:
        polygon: Polygon
        threshold: Threshold (the maximum area of the hole within a polygon to retain) in square meters

    Returns:
        Polygon
    """
    if not polygon.interiors:
        return polygon

    if threshold == 0:
        return Polygon(
            shell=polygon.exterior.coords,
        )

    interiors = [
        interior
        for interior in polygon.interiors
        if Polygon(interior).area >= threshold
    ]
    return Polygon(
        shell=polygon.exterior.coords,
        holes=interiors,
    )


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
    return _process_data(
        vector=vector,
        layer_name=layer_name,
        process_data=lambda data: _map_field_data(
            data=data,
            field=field,
            mapping=mapping,
        ),
        new_layer_name=new_layer_name,
    )


def _map_field_data(
    data: gpd.GeoDataFrame,
    field: str,
    mapping: dict[object, object],
) -> gpd.GeoDataFrame:
    """Maps the field of the data.

    Parameters:
        data: Data
        field: Field
        mapping: Mapping of the field names

    Returns:
        Data
    """
    data[field] = data[field].map(mapping)
    return data


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
    return _process_data(
        vector=vector,
        layer_name=layer_name,
        process_data=lambda data: _query_data(
            data=data,
            query_string=query_string,
        ),
        new_layer_name=new_layer_name,
    )


def _query_data(
    data: gpd.GeoDataFrame,
    query_string: str,
) -> gpd.GeoDataFrame:
    """Queries the data.

    Parameters:
        data: Data
        query_string: Query string based on the pandas query syntax

    Returns:
        Data
    """
    return data.query(query_string)


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
    return _process_data(
        vector=vector,
        layer_name=layer_name,
        process_data=lambda data: _rename_fields_data(
            data=data,
            mapping=mapping,
        ),
        new_layer_name=new_layer_name,
    )


def _rename_fields_data(
    data: gpd.GeoDataFrame,
    mapping: dict[object, object],
) -> gpd.GeoDataFrame:
    """Renames the fields of the data.

    Parameters:
        data: Data
        mapping: Mapping of the field names

    Returns:
        Data
    """
    return data.rename(
        columns=mapping,
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
    return _process_data(
        vector=vector,
        layer_name=layer_name,
        process_data=lambda data: _sieve_data(
            data=data,
            threshold=threshold,
        ),
        new_layer_name=new_layer_name,
    )


def _sieve_data(
    data: gpd.GeoDataFrame,
    threshold: float,
) -> gpd.GeoDataFrame:
    """Sieves the data.

    Parameters:
        data: Data
        threshold: Threshold (the minimum area of the polygon to retain) in square meters

    Returns:
        Data
    """
    if threshold == 0:
        return data

    data = data[data.geometry.area >= threshold]
    return data.reset_index(drop=True)


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
    return _process_data(
        vector=vector,
        layer_name=layer_name,
        process_data=lambda data: _simplify_data(
            data=data,
            threshold=threshold,
        ),
        new_layer_name=new_layer_name,
    )


def _simplify_data(
    data: gpd.GeoDataFrame,
    threshold: float,
) -> gpd.GeoDataFrame:
    """Simplifies the data.

    Parameters:
        data: Data
        threshold: Threshold (the minimum area of the triangle defined by three consecutive vertices to retain)

    Returns:
        Data
    """
    data.geometry = data.geometry.simplify_coverage(
        tolerance=threshold,
    )
    return data
