from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import folium
import geopandas as gpd
from shapely.geometry import box

import aviary


def build_maps() -> None:
    """Builds the maps for the docs."""
    build_bounding_box_map()
    build_bounding_box_from_gdf_map()
    build_bounding_box_from_gdf_districts_map()
    build_bounding_box_and_map()
    build_bounding_box_or_map()


def build_bounding_box_map() -> None:
    """Builds the bounding_box map."""
    bounding_box = aviary.BoundingBox(
        x_min=363084,
        y_min=5715326,
        x_max=363340,
        y_max=5715582,
    )

    bounding_box_gdf = bounding_box.to_gdf(epsg_code=25832)
    bounding_box_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    bounding_box_layer = Layer(
        gdf=bounding_box_gdf,
        style=bounding_box_style,
    )

    layers = [bounding_box_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_bounding_box_from_gdf_map() -> None:
    """Builds the bounding_box_from_gdf map."""
    gdf = gpd.GeoDataFrame(
        geometry=[box(363084, 5715326, 363340, 5715582)],
        crs='EPSG:25832',
    )

    bounding_box = aviary.BoundingBox.from_gdf(gdf=gdf)

    bounding_box_gdf = bounding_box.to_gdf(epsg_code=25832)
    bounding_box_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    bounding_box_layer = Layer(
        gdf=bounding_box_gdf,
        style=bounding_box_style,
    )

    gdf_style = {
        'fillOpacity': 0.,
        'color': '#E7000B',
        'weight': 2,
    }
    gdf_layer = Layer(
        gdf=gdf,
        style=gdf_style,
    )

    layers = [
        bounding_box_layer,
        gdf_layer,
    ]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box_from_gdf.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_bounding_box_from_gdf_districts_map() -> None:
    """Builds the bounding_box_from_gdf_districts map."""
    gdf = gpd.read_file('docs/how_to_guides/api/data/districts.geojson')

    bounding_box = aviary.BoundingBox.from_gdf(gdf=gdf)

    bounding_box_gdf = bounding_box.to_gdf(epsg_code=25832)
    bounding_box_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    bounding_box_layer = Layer(
        gdf=bounding_box_gdf,
        style=bounding_box_style,
    )

    gdf_style = {
        'fillOpacity': 0.,
        'color': '#E7000B',
        'weight': 2,
    }
    gdf_layer = Layer(
        gdf=gdf,
        style=gdf_style,
    )

    layers = [
        bounding_box_layer,
        gdf_layer,
    ]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box_from_gdf_districts.html'

    build_map(
        layers=layers,
        path=path,
        zoom_start=10,
    )


def build_bounding_box_and_map() -> None:
    """Builds the bounding_box_and map."""
    bounding_box_1 = aviary.BoundingBox(
        x_min=363084,
        y_min=5715326,
        x_max=363340,
        y_max=5715582,
    )

    bounding_box_1_gdf = bounding_box_1.to_gdf(epsg_code=25832)
    bounding_box_1_style = {
        'fillOpacity': 0.,
        'color': '#E7000B',
        'weight': 2,
    }
    bounding_box_1_layer = Layer(
        gdf=bounding_box_1_gdf,
        style=bounding_box_1_style,
    )

    bounding_box_2 = aviary.BoundingBox(
        x_min=363212,
        y_min=5715454,
        x_max=363468,
        y_max=5715710,
    )

    bounding_box_2_gdf = bounding_box_2.to_gdf(epsg_code=25832)
    bounding_box_2_style = {
        'fillOpacity': 0.,
        'color': '#155DFC',
        'weight': 2,
    }
    bounding_box_2_layer = Layer(
        gdf=bounding_box_2_gdf,
        style=bounding_box_2_style,
    )

    bounding_box = bounding_box_1 & bounding_box_2

    bounding_box_gdf = bounding_box.to_gdf(epsg_code=25832)
    bounding_box_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    bounding_box_layer = Layer(
        gdf=bounding_box_gdf,
        style=bounding_box_style,
    )

    layers = [
        bounding_box_layer,
        bounding_box_1_layer,
        bounding_box_2_layer,
    ]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box_and.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_bounding_box_or_map() -> None:
    """Builds the bounding_box_or map."""
    bounding_box_1 = aviary.BoundingBox(
        x_min=363084,
        y_min=5715326,
        x_max=363340,
        y_max=5715582,
    )

    bounding_box_1_gdf = bounding_box_1.to_gdf(epsg_code=25832)
    bounding_box_1_style = {
        'fillOpacity': 0.,
        'color': '#E7000B',
        'weight': 2,
    }
    bounding_box_1_layer = Layer(
        gdf=bounding_box_1_gdf,
        style=bounding_box_1_style,
    )

    bounding_box_2 = aviary.BoundingBox(
        x_min=363212,
        y_min=5715454,
        x_max=363468,
        y_max=5715710,
    )

    bounding_box_2_gdf = bounding_box_2.to_gdf(epsg_code=25832)
    bounding_box_2_style = {
        'fillOpacity': 0.,
        'color': '#155DFC',
        'weight': 2,
    }
    bounding_box_2_layer = Layer(
        gdf=bounding_box_2_gdf,
        style=bounding_box_2_style,
    )

    bounding_box = bounding_box_1 | bounding_box_2

    bounding_box_gdf = bounding_box.to_gdf(epsg_code=25832)
    bounding_box_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    bounding_box_layer = Layer(
        gdf=bounding_box_gdf,
        style=bounding_box_style,
    )

    layers = [
        bounding_box_layer,
        bounding_box_1_layer,
        bounding_box_2_layer,
    ]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box_or.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_map(
    layers: list[Layer],
    path: Path,
    zoom_start: int = 16,
) -> None:
    """Builds a map.

    Parameters:
        layers: Layers
        path: Path
        zoom_start: Zoom start
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
        gdf: Geodataframe
        style: Style
    """
    gdf: gpd.GeoDataFrame
    style: dict


def compute_location(
    layers: list[Layer],
) -> tuple[float, float]:
    """Computes the coordinates of the location.

    Parameters:
        layers: Layers

    Returns:
        Coordinates of the location
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
    """Returns a GeoJSON layer.

    Parameters:
        layer: Layer

    Returns:
        GeoJSON layer
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
