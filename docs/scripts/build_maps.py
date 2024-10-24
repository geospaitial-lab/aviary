from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import folium
import geopandas as gpd


def build_maps() -> None:
    """Builds the maps for the docs."""
    pass  # noqa: PIE790


def build_map(
    layers: list[Layer],
    path: Path,
    zoom_start: int = 16,
) -> None:
    """Builds a map.

    Parameters:
        layers: layers
        path: path
        zoom_start: zoom start
    """
    location = compute_location(
        layers=layers,
    )

    folium_map = folium.Map(
        location=location,
        zoom_start=zoom_start,
        tiles=None,
    )

    osm_layer = folium.TileLayer(
        tiles='OpenStreetMap',
        control=False,
    )
    osm_layer.add_to(folium_map)

    dop_layer = folium.raster_layers.WmsTileLayer(
        url='https://www.wms.nrw.de/geobasis/wms_nw_dop',
        layers='nw_dop_rgb',
        fmt='image/png',
        transparent=True,
        version='1.3.0',
        attr='<a href="https://www.bezreg-koeln.nrw.de/geobasis-nrw">Geobasis NRW</a>',
        name='Orthophotos',
        show=False,
    )
    dop_layer.add_to(folium_map)

    layer_control = folium.LayerControl(
        collapsed=False,
    )
    layer_control.add_to(folium_map)

    for layer in layers:
        geojson_layer = get_geojson_layer(
            layer=layer,
        )
        geojson_layer.add_to(folium_map)

    folium_map.save(path)


@dataclass
class Layer:
    """
    Attributes:
        gdf: geodataframe
        style: style
    """
    gdf: gpd.GeoDataFrame
    style: dict


def compute_location(
    layers: list[Layer],
) -> tuple[float, float]:
    """Computes the coordinates of the location.

    Parameters:
        layers: layers

    Returns:
        coordinates of the location
    """
    gdf = layers[0].gdf

    centroid = gpd.GeoDataFrame(
        geometry=[gdf.union_all().centroid],
        crs=gdf.crs,
    )
    centroid = centroid.to_crs(epsg=4326)

    return (
        centroid.geometry.y.mean(),
        centroid.geometry.x.mean(),
    )


def get_geojson_layer(
    layer: Layer,
) -> folium.GeoJson:
    """Returns a geojson layer.

    Parameters:
        layer: layer

    Returns:
        geojson layer
    """
    gdf, style = layer.gdf, layer.style
    gdf = gdf.to_crs(epsg=4326)
    return folium.GeoJson(
        data=gdf,
        style_function=lambda feature: style,  # noqa: ARG005
        control=False,
    )


if __name__ == '__main__':
    build_maps()
