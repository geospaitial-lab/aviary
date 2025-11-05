from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


if TYPE_CHECKING:
    from aviary.core.vector import Vector
    from aviary.core.vector_layer import VectorLayer


def vector_exporter(
    vector: Vector,
    layer_name: str,
    dir_path: Path,
    gpkg_name: str,
    remove_layer: bool = True,
) -> Vector:
    """Exports the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        dir_path: Path to the directory
        gpkg_name: Name of the geopackage (.gpkg file)
        remove_layer: If True, the layer is removed

    Returns:
        Vector
    """
    layer: VectorLayer = vector[layer_name]

    gdf = layer.data

    if not gdf.empty:
        gpkg_path = dir_path / gpkg_name

        gdf.to_file(
            gpkg_path,
            driver='GPKG',
            mode='w',
        )

    if remove_layer:
        vector = vector.remove(
            layer_names=layer_name,
            inplace=True,
        )

    return vector
