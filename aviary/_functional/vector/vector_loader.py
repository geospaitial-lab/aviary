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

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import geopandas as gpd
import pandas as pd

from aviary.core.exceptions import AviaryUserError
from aviary.core.vector import Vector
from aviary.core.vector_layer import VectorLayer

if TYPE_CHECKING:
    from aviary.vector.vector_loader import VectorLoader


def composite_loader(
    vector_loaders: list[VectorLoader],
    max_num_threads: int | None = None,
) -> Vector:
    """Loads a vector from the sources.

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
    max_num_threads: int | None = None,
) -> Vector:
    """Loads a vector from the geopackage or the directory containing geopackages.

    Parameters:
        path: Path to the geopackage (.gpkg file) or to the directory containing geopackages (.gpkg files)
            exported by the `tile.VectorExporter`
        layer_name: Layer name
        max_num_threads: Maximum number of threads

    Returns:
        Vector

    Raises:
        AviaryUserError: Invalid `path` (the directory contains no geopackages)
    """
    if path.is_file():
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

    paths = list(path.glob('*.gpkg'))

    if not paths:
        message = (
            'Invalid path! '
            'The directory must contain at least one geopackage.'
        )
        raise AviaryUserError(message)

    if len(paths) == 1:
        data = gpd.read_file(paths[0])
        layer = VectorLayer(
            data=data,
            name=layer_name,
            copy=False,
        )

        return Vector(
            layers=[layer],
            copy=False,
        )

    if max_num_threads == 1:
        data = [gpd.read_file(path) for path in paths]
    else:
        with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
            data = list(executor.map(lambda p: gpd.read_file(p), paths))

    data = pd.concat(
        data,
        ignore_index=True,
        copy=False,
    )
    layer = VectorLayer(
        data=data,
        name=layer_name,
        copy=False,
    )

    return Vector(
        layers=[layer],
        copy=False,
    )
