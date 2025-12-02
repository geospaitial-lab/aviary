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

from aviary.core.vector import Vector
from aviary.core.vector_layer import VectorLayer

if TYPE_CHECKING:
    from aviary.core.bounding_box import BoundingBox
    from aviary.core.type_aliases import EPSGCode
    from aviary.vector.vector_loader import VectorLoader


def bounding_box_loader(
    bounding_box: BoundingBox,
    epsg_code: EPSGCode,
    layer_name: str,
) -> Vector:
    """Loads a vector from the bounding box.

    Parameters:
        bounding_box: Bounding box
        epsg_code: EPSG code
        layer_name: Layer name

    Returns:
        Vector
    """
    data = bounding_box.to_gdf(epsg_code=epsg_code)

    layer = VectorLayer(
        data=data,
        name=layer_name,
        copy=False,
    )

    return Vector(
        layers=[layer],
        copy=False,
    )


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


def geojson_loader(
    path: Path,
    epsg_code: EPSGCode,
    layer_name: str,
) -> Vector:
    """Loads a vector from the GeoJSON file.

    Parameters:
        path: Path to the GeoJSON file (.geojson file)
        epsg_code: EPSG code
        layer_name: Layer name

    Returns:
        Vector
    """
    data = gpd.read_file(path)
    epsg_code = f'EPSG:{epsg_code}'
    data = data.to_crs(crs=epsg_code)

    layer = VectorLayer(
        data=data,
        name=layer_name,
        copy=False,
    )

    return Vector(
        layers=[layer],
        copy=False,
    )


def gpkg_loader(
    path: Path,
    epsg_code: EPSGCode,
    layer_name: str,
) -> Vector:
    """Loads a vector from the geopackage.

    Parameters:
        path: Path to the geopackage (.gpkg file)
        epsg_code: EPSG code
        layer_name: Layer name

    Returns:
        Vector
    """
    data = gpd.read_file(path)
    epsg_code = f'EPSG:{epsg_code}'
    data = data.to_crs(crs=epsg_code)

    layer = VectorLayer(
        data=data,
        name=layer_name,
        copy=False,
    )

    return Vector(
        layers=[layer],
        copy=False,
    )
