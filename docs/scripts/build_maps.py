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
    build_bounding_box_setter_map()
    build_bounding_box_from_gdf_map()
    build_bounding_box_from_gdf_districts_map()
    build_bounding_box_buffer_1_map()
    build_bounding_box_buffer_2_map()
    build_bounding_box_quantize_map()
    # build_process_area_map()  # noqa: ERA001
    # build_process_area_setter_map()  # noqa: ERA001
    # build_process_area_from_bounding_box_map()  # noqa: ERA001
    # build_process_area_from_bounding_box_tile_size_map()  # noqa: ERA001
    # build_process_area_from_bounding_box_quantize_map()  # noqa: ERA001
    # build_process_area_from_gdf_map()  # noqa: ERA001
    # build_process_area_from_gdf_districts_map()  # noqa: ERA001
    # build_process_area_add_map()  # noqa: ERA001
    # build_process_area_sub_map()  # noqa: ERA001
    # build_process_area_and_map()  # noqa: ERA001
    # build_process_area_append_map()  # noqa: ERA001
    # build_process_area_filter_difference_map()  # noqa: ERA001
    # build_process_area_filter_intersection_map()  # noqa: ERA001


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
    path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps' / 'bounding_box.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_bounding_box_setter_map() -> None:
    """Builds the bounding_box_setter map."""
    bounding_box = aviary.BoundingBox(
        x_min=363148,
        y_min=5715390,
        x_max=363276,
        y_max=5715518,
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
    path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps' / 'bounding_box_setter.html'

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
        'color': '#FF595E',
        'weight': 2,
    }
    gdf_layer = Layer(
        gdf=gdf,
        style=gdf_style,
    )

    layers = [bounding_box_layer, gdf_layer]
    path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps' / 'bounding_box_from_gdf.html'

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
        'color': '#FF595E',
        'weight': 2,
    }
    gdf_layer = Layer(
        gdf=gdf,
        style=gdf_style,
    )

    layers = [bounding_box_layer, gdf_layer]
    path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps' / 'bounding_box_from_gdf_districts.html'

    build_map(
        layers=layers,
        path=path,
        zoom_start=12,
    )


def build_bounding_box_buffer_1_map() -> None:
    """Builds the bounding_box_buffer_1 map."""
    bounding_box = aviary.BoundingBox(
        x_min=363084,
        y_min=5715326,
        x_max=363340,
        y_max=5715582,
    )

    buffered_bounding_box = bounding_box.buffer(buffer_size=64)

    buffered_bounding_box_gdf = buffered_bounding_box.to_gdf(epsg_code=25832)
    buffered_bounding_box_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    buffered_bounding_box_layer = Layer(
        gdf=buffered_bounding_box_gdf,
        style=buffered_bounding_box_style,
    )

    bounding_box_gdf = bounding_box.to_gdf(epsg_code=25832)
    bounding_box_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    bounding_box_layer = Layer(
        gdf=bounding_box_gdf,
        style=bounding_box_style,
    )

    layers = [buffered_bounding_box_layer, bounding_box_layer]
    path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps' / 'bounding_box_buffer_1.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_bounding_box_buffer_2_map() -> None:
    """Builds the bounding_box_buffer_2 map."""
    bounding_box = aviary.BoundingBox(
        x_min=363084,
        y_min=5715326,
        x_max=363340,
        y_max=5715582,
    )

    buffered_bounding_box = bounding_box.buffer(buffer_size=-64)

    buffered_bounding_box_gdf = buffered_bounding_box.to_gdf(epsg_code=25832)
    buffered_bounding_box_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    buffered_bounding_box_layer = Layer(
        gdf=buffered_bounding_box_gdf,
        style=buffered_bounding_box_style,
    )

    bounding_box_gdf = bounding_box.to_gdf(epsg_code=25832)
    bounding_box_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    bounding_box_layer = Layer(
        gdf=bounding_box_gdf,
        style=bounding_box_style,
    )

    layers = [buffered_bounding_box_layer, bounding_box_layer]
    path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps' / 'bounding_box_buffer_2.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_bounding_box_quantize_map() -> None:
    """Builds the bounding_box_quantize map."""
    bounding_box = aviary.BoundingBox(
        x_min=363084,
        y_min=5715326,
        x_max=363340,
        y_max=5715582,
    )

    quantized_bounding_box = bounding_box.quantize(value=128)

    quantized_bounding_box_gdf = quantized_bounding_box.to_gdf(epsg_code=25832)
    quantized_bounding_box_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    quantized_bounding_box_layer = Layer(
        gdf=quantized_bounding_box_gdf,
        style=quantized_bounding_box_style,
    )

    bounding_box_gdf = bounding_box.to_gdf(epsg_code=25832)
    bounding_box_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    bounding_box_layer = Layer(
        gdf=bounding_box_gdf,
        style=bounding_box_style,
    )

    layers = [quantized_bounding_box_layer, bounding_box_layer]
    path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps' / 'bounding_box_quantize.html'

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
