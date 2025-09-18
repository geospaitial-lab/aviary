from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import geopandas as gpd

from aviary.core.vector import Vector
from aviary.core.vector_layer import VectorLayer

if TYPE_CHECKING:
    from aviary.vector.vector_loader import VectorLoader


def composite_loader(
    vector_loaders: list[VectorLoader],
    max_num_threads: int | None = None,
) -> Vector:
    """Loads vector data from the sources.

    Parameters:
        vector_loaders: Vector loaders
        max_num_threads: Maximum number of threads

    Returns:
        Vector
    """
    if len(vector_loaders) == 1:
        max_num_threads = 1

    if max_num_threads == 1:
        vectors = [
            vector_loader()
            for vector_loader in vector_loaders
        ]
        return Vector.from_vectors(
            vectors=vectors,
            copy=False,
        )

    with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
        vectors = list(executor.map(lambda vector_loader: vector_loader(), vector_loaders))

    return Vector.from_vectors(
        vectors=vectors,
        copy=False,
    )


def gpkg_loader(
    path: Path,
    layer_name: str,
) -> Vector:
    """Loads vector data from the geopackage.

    Parameters:
        path: Path to the geopackage (.gpkg file)
        layer_name: Layer name

    Returns:
        Vector
    """
    data = gpd.read_file(path)
    layer = VectorLayer(
        data=data,
        name=layer_name,
        copy=False,
    )

    return Vector(
        layers=[layer],
        copy=False,
    )
