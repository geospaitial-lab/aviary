from __future__ import annotations

from typing import TYPE_CHECKING

import geopandas as gpd
import topojson as tp
from shapely.geometry import Polygon

if TYPE_CHECKING:
    from ...geodata.geodata_postprocessor import GeodataPostprocessor


def clip_postprocessor(
    gdf: gpd.GeoDataFrame,
    mask: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Postprocesses the geodata by clipping the polygons based on the mask extent.

    Parameters:
        gdf: geodataframe
        mask: geodataframe of the mask (may contain multiple polygons)

    Returns:
        postprocessed geodataframe
    """
    if gdf.empty:
        return gdf

    gdf = gpd.clip(
        gdf=gdf,
        mask=mask,
        keep_geom_type=True,
    )
    gdf.reset_index(
        drop=True,
        inplace=True,
    )
    return gdf


def composite_postprocessor(
    gdf: gpd.GeoDataFrame,
    geodata_postprocessors: list[GeodataPostprocessor],
) -> gpd.GeoDataFrame:
    """Postprocesses the geodata with each geodata postprocessor.

    Parameters:
        gdf: geodataframe
        geodata_postprocessors: geodata postprocessors

    Returns:
        postprocessed geodataframe
    """
    if gdf.empty:
        return gdf

    for geodata_postprocessor in geodata_postprocessors:
        gdf = geodata_postprocessor(gdf)
    return gdf


def field_name_postprocessor(
    gdf: gpd.GeoDataFrame,
    mapping: dict,
) -> gpd.GeoDataFrame:
    """Postprocesses the geodata by renaming the fields.

    Parameters:
        gdf: geodataframe
        mapping: mapping of the field names (old field name: new field name)

    Returns:
        postprocessed geodataframe
    """
    return gdf.rename(columns=mapping)


def fill_postprocessor(
    gdf: gpd.GeoDataFrame,
    max_area: float,
) -> gpd.GeoDataFrame:
    """Postprocesses the geodata by filling holes in the polygons.

    Parameters:
        gdf: geodataframe
        max_area: maximum area of the holes to retain in square meters

    Returns:
        postprocessed geodataframe
    """
    if gdf.empty:
        return gdf

    gdf = gdf.copy()
    gdf.geometry = gdf.apply(
        lambda row: _fill_polygon(
            polygon=row.geometry,
            max_area=max_area,
        ),
        axis=1,
    )
    return gdf


def _fill_polygon(
    polygon: Polygon,
    max_area: float,
) -> Polygon:
    """Fills the holes in the polygon.

    Parameters:
        polygon: polygon
        max_area: maximum area of the holes to retain in square meters

    Returns:
        filled polygon
    """
    if not polygon.interiors:
        return polygon

    if max_area == 0:
        return Polygon(polygon.exterior.coords)

    interiors = [
        interior
        for interior in polygon.interiors
        if Polygon(interior).area >= max_area
    ]
    return Polygon(polygon.exterior.coords, holes=interiors)


def sieve_postprocessor(
    gdf: gpd.GeoDataFrame,
    min_area: float,
) -> gpd.GeoDataFrame:
    """Postprocesses the geodata by sieving the polygons.

    Parameters:
        gdf: geodataframe
        min_area: minimum area of the polygons to retain in square meters

    Returns:
        postprocessed geodataframe
    """
    if gdf.empty:
        return gdf

    if min_area == 0:
        return gdf

    gdf = gdf[gdf.geometry.area >= min_area]
    gdf.reset_index(
        drop=True,
        inplace=True,
    )
    return gdf


def simplify_postprocessor(
    gdf: gpd.GeoDataFrame,
    tolerance: float,
) -> gpd.GeoDataFrame:
    """Postprocesses the geodata by simplifying the polygons.

    Parameters:
        gdf: geodataframe
        tolerance: tolerance of the Douglas-Peucker algorithm in meters (a lower value will result
            in less simplification, a higher value will result in more simplification,
            a value equal to the ground sampling distance is recommended)

    Returns:
        postprocessed geodataframe
    """
    if gdf.empty:
        return gdf

    topo = tp.Topology(gdf)
    topo.toposimplify(
        epsilon=tolerance,
        simplify_with='simplification',
        inplace=True,
    )
    gdf = topo.to_gdf(
        crs=gdf.crs,
    )
    return gdf


def value_postprocessor(
    gdf: gpd.GeoDataFrame,
    mapping: dict,
    field_name: str = 'class',
) -> gpd.GeoDataFrame:
    """Postprocesses the geodata by mapping the values of a field.

    Parameters:
        gdf: geodataframe
        mapping: mapping of the values (old value: new value)
        field_name: name of the field

    Returns:
        postprocessed geodataframe
    """
    if gdf.empty:
        return gdf

    gdf = gdf.copy()
    gdf[field_name] = gdf[field_name].map(mapping)
    return gdf
