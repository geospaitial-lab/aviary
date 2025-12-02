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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


if TYPE_CHECKING:
    from aviary.core.type_aliases import EPSGCode
    from aviary.core.vector import Vector
    from aviary.core.vector_layer import VectorLayer


def vector_exporter(
    vector: Vector,
    layer_name: str,
    epsg_code: EPSGCode,
    path: Path,
    remove_layer: bool = True,
) -> Vector:
    """Exports the layer.

    Parameters:
        vector: Vector
        layer_name: Layer name
        epsg_code: EPSG code
        path: Path to the geopackage (.gpkg file)
        remove_layer: If True, the layer is removed

    Returns:
        Vector
    """
    layer: VectorLayer = vector[layer_name]

    epsg_code = f'EPSG:{epsg_code}'
    gdf = layer.data

    if not gdf.empty:
        gdf = gdf.to_crs(crs=epsg_code)

        gdf.to_file(
            path,
            driver='GPKG',
            mode='w',
        )

    if remove_layer:
        vector = vector.remove(
            layer_names=layer_name,
            inplace=True,
        )

    return vector
