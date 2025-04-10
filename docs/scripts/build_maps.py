from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import folium
import geopandas as gpd
import numpy as np
from shapely.geometry import box

import aviary
from aviary.geodata import GeospatialFilter


def build_maps() -> None:
    """Builds the maps for the docs."""
    build_bounding_box_map()
    build_bounding_box_setter_map()
    build_bounding_box_from_gdf_map()
    build_bounding_box_from_gdf_districts_map()
    build_bounding_box_buffer_positive_map()
    build_bounding_box_buffer_negative_map()
    build_bounding_box_quantize_map()
    build_process_area_map()
    build_process_area_setter_coordinates_map()
    build_process_area_setter_tile_size_map()
    build_process_area_from_bounding_box_map()
    build_process_area_from_bounding_box_tile_size_map()
    build_process_area_from_bounding_box_quantize_map()
    build_process_area_from_gdf_map()
    build_process_area_from_gdf_districts_map()
    build_process_area_add_map()
    build_process_area_sub_map()
    build_process_area_and_map()
    build_process_area_append_map()
    build_process_area_filter_difference_map()
    build_process_area_filter_intersection_map()


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
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box_setter.html'

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
        'color': '#FF595E',
        'weight': 2,
    }
    gdf_layer = Layer(
        gdf=gdf,
        style=gdf_style,
    )

    layers = [bounding_box_layer, gdf_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box_from_gdf_districts.html'

    build_map(
        layers=layers,
        path=path,
        zoom_start=11,
    )


def build_bounding_box_buffer_positive_map() -> None:
    """Builds the bounding_box_buffer_positive map."""
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
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box_buffer_positive.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_bounding_box_buffer_negative_map() -> None:
    """Builds the bounding_box_buffer_negative map."""
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
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box_buffer_negative.html'

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
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'bounding_box_quantize.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_map() -> None:
    """Builds the process_area map."""
    coordinates = np.array(
        [
            [363084, 5715326],
            [363212, 5715326],
            [363084, 5715454],
            [363212, 5715454],
        ],
        dtype=np.int32,
    )
    process_area = aviary.ProcessArea(
        coordinates=coordinates,
        tile_size=128,
    )

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    layers = [process_area_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_setter_coordinates_map() -> None:
    """Builds the process_area_setter_coordinates map."""
    coordinates = np.array(
        [
            [363084, 5715326],
            [363212, 5715326],
        ],
        dtype=np.int32,
    )
    process_area = aviary.ProcessArea(
        coordinates=coordinates,
        tile_size=128,
    )

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    layers = [process_area_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_setter_coordinates.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_setter_tile_size_map() -> None:
    """Builds the process_area_setter_tile_size map."""
    coordinates = np.array(
        [
            [363084, 5715326],
            [363212, 5715326],
        ],
        dtype=np.int32,
    )
    process_area = aviary.ProcessArea(
        coordinates=coordinates,
        tile_size=64,
    )

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    layers = [process_area_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_setter_tile_size.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_from_bounding_box_map() -> None:
    """Builds the process_area_from_bounding_box map."""
    bounding_box = aviary.BoundingBox(
        x_min=363084,
        y_min=5715326,
        x_max=363340,
        y_max=5715582,
    )

    process_area = aviary.ProcessArea.from_bounding_box(
        bounding_box=bounding_box,
        tile_size=128,
        quantize=False,
    )

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
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

    layers = [process_area_layer, bounding_box_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_from_bounding_box.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_from_bounding_box_tile_size_map() -> None:
    """Builds the process_area_from_bounding_box_tile_size map."""
    bounding_box = aviary.BoundingBox(
        x_min=363084,
        y_min=5715326,
        x_max=363340,
        y_max=5715582,
    )

    process_area = aviary.ProcessArea.from_bounding_box(
        bounding_box=bounding_box,
        tile_size=96,
        quantize=False,
    )

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
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

    layers = [process_area_layer, bounding_box_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_from_bounding_box_tile_size.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_from_bounding_box_quantize_map() -> None:
    """Builds the process_area_from_bounding_box_quantize map."""
    bounding_box = aviary.BoundingBox(
        x_min=363084,
        y_min=5715326,
        x_max=363340,
        y_max=5715582,
    )

    process_area = aviary.ProcessArea.from_bounding_box(
        bounding_box=bounding_box,
        tile_size=128,
        quantize=True,
    )

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
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

    layers = [process_area_layer, bounding_box_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_from_bounding_box_quantize.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_from_gdf_map() -> None:
    """Builds the process_area_from_gdf map."""
    gdf = gpd.GeoDataFrame(
        geometry=[box(363084, 5715326, 363340, 5715582)],
        crs='EPSG:25832',
    )

    process_area = aviary.ProcessArea.from_gdf(
        gdf=gdf,
        tile_size=128,
        quantize=False,
    )

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    gdf_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    gdf_layer = Layer(
        gdf=gdf,
        style=gdf_style,
    )

    layers = [process_area_layer, gdf_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_from_gdf.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_from_gdf_districts_map() -> None:
    """Builds the process_area_from_gdf_districts map."""
    gdf = gpd.read_file('docs/how_to_guides/api/data/districts.geojson')

    process_area = aviary.ProcessArea.from_gdf(
        gdf=gdf,
        tile_size=256,
        quantize=True,
    )

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    gdf_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    gdf_layer = Layer(
        gdf=gdf,
        style=gdf_style,
    )

    layers = [process_area_layer, gdf_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_from_gdf_districts.html'

    build_map(
        layers=layers,
        path=path,
        zoom_start=11,
    )


def build_process_area_add_map() -> None:
    """Builds the process_area_add map."""
    coordinates_1 = np.array(
        [
            [363084, 5715326],
            [363212, 5715326],
            [363084, 5715454],
            [363212, 5715454],
        ],
        dtype=np.int32,
    )
    process_area_1 = aviary.ProcessArea(
        coordinates=coordinates_1,
        tile_size=128,
    )

    coordinates_2 = np.array(
        [
            [363212, 5715454],
            [363340, 5715454],
            [363212, 5715582],
            [363340, 5715582],
        ],
        dtype=np.int32,
    )
    process_area_2 = aviary.ProcessArea(
        coordinates=coordinates_2,
        tile_size=128,
    )

    process_area = process_area_1 + process_area_2

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    process_area_1_gdf = process_area_1.to_gdf(epsg_code=25832)
    process_area_1_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    process_area_1_layer = Layer(
        gdf=process_area_1_gdf,
        style=process_area_1_style,
    )

    process_area_2_gdf = process_area_2.to_gdf(epsg_code=25832)
    process_area_2_style = {
        'fillOpacity': 0,
        'color': '#1982C4',
        'weight': 2,
    }
    process_area_2_layer = Layer(
        gdf=process_area_2_gdf,
        style=process_area_2_style,
    )

    layers = [process_area_layer, process_area_1_layer, process_area_2_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_add.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_sub_map() -> None:
    """Builds the process_area_sub map."""
    coordinates_1 = np.array(
        [
            [363084, 5715326],
            [363212, 5715326],
            [363084, 5715454],
            [363212, 5715454],
        ],
        dtype=np.int32,
    )
    process_area_1 = aviary.ProcessArea(
        coordinates=coordinates_1,
        tile_size=128,
    )

    coordinates_2 = np.array(
        [
            [363212, 5715454],
            [363340, 5715454],
            [363212, 5715582],
            [363340, 5715582],
        ],
        dtype=np.int32,
    )
    process_area_2 = aviary.ProcessArea(
        coordinates=coordinates_2,
        tile_size=128,
    )

    process_area = process_area_1 - process_area_2

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    process_area_1_gdf = process_area_1.to_gdf(epsg_code=25832)
    process_area_1_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    process_area_1_layer = Layer(
        gdf=process_area_1_gdf,
        style=process_area_1_style,
    )

    process_area_2_gdf = process_area_2.to_gdf(epsg_code=25832)
    process_area_2_style = {
        'fillOpacity': 0,
        'color': '#1982C4',
        'weight': 2,
    }
    process_area_2_layer = Layer(
        gdf=process_area_2_gdf,
        style=process_area_2_style,
    )

    layers = [process_area_layer, process_area_1_layer, process_area_2_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_sub.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_and_map() -> None:
    """Builds the process_area_and map."""
    coordinates_1 = np.array(
        [
            [363084, 5715326],
            [363212, 5715326],
            [363084, 5715454],
            [363212, 5715454],
        ],
        dtype=np.int32,
    )
    process_area_1 = aviary.ProcessArea(
        coordinates=coordinates_1,
        tile_size=128,
    )

    coordinates_2 = np.array(
        [
            [363212, 5715454],
            [363340, 5715454],
            [363212, 5715582],
            [363340, 5715582],
        ],
        dtype=np.int32,
    )
    process_area_2 = aviary.ProcessArea(
        coordinates=coordinates_2,
        tile_size=128,
    )

    process_area = process_area_1 & process_area_2

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    process_area_1_gdf = process_area_1.to_gdf(epsg_code=25832)
    process_area_1_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    process_area_1_layer = Layer(
        gdf=process_area_1_gdf,
        style=process_area_1_style,
    )

    process_area_2_gdf = process_area_2.to_gdf(epsg_code=25832)
    process_area_2_style = {
        'fillOpacity': 0,
        'color': '#1982C4',
        'weight': 2,
    }
    process_area_2_layer = Layer(
        gdf=process_area_2_gdf,
        style=process_area_2_style,
    )

    layers = [process_area_layer, process_area_1_layer, process_area_2_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_and.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_append_map() -> None:
    """Builds the process_area_append map."""
    coordinates = np.array(
        [
            [363084, 5715326],
            [363212, 5715326],
            [363084, 5715454],
            [363212, 5715454],
            [363340, 5715582],
        ],
        dtype=np.int32,
    )
    process_area = aviary.ProcessArea(
        coordinates=coordinates,
        tile_size=128,
    )

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    layers = [process_area_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_append.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_filter_difference_map() -> None:
    """Builds the process_area_filter_difference map."""
    coordinates = np.array(
        [
            [363084, 5715326],
            [363212, 5715326],
            [363084, 5715454],
            [363212, 5715454],
        ],
        dtype=np.int32,
    )
    process_area = aviary.ProcessArea(
        coordinates=coordinates,
        tile_size=128,
    )

    gdf = gpd.GeoDataFrame(
        geometry=[box(363212, 5715454, 363468, 5715710)],
        crs='EPSG:25832',
    )

    geospatial_filter = GeospatialFilter(
        tile_size=128,
        gdf=gdf,
        mode=aviary.GeospatialFilterMode.DIFFERENCE,
    )
    process_area = process_area.filter(coordinates_filter=geospatial_filter)

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    gdf_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    gdf_layer = Layer(
        gdf=gdf,
        style=gdf_style,
    )

    layers = [process_area_layer, gdf_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_filter_difference.html'

    build_map(
        layers=layers,
        path=path,
    )


def build_process_area_filter_intersection_map() -> None:
    """Builds the process_area_filter_intersection map."""
    coordinates = np.array(
        [
            [363084, 5715326],
            [363212, 5715326],
            [363084, 5715454],
            [363212, 5715454],
        ],
        dtype=np.int32,
    )
    process_area = aviary.ProcessArea(
        coordinates=coordinates,
        tile_size=128,
    )

    gdf = gpd.GeoDataFrame(
        geometry=[box(363212, 5715454, 363468, 5715710)],
        crs='EPSG:25832',
    )

    geospatial_filter = GeospatialFilter(
        tile_size=128,
        gdf=gdf,
        mode=aviary.GeospatialFilterMode.INTERSECTION,
    )
    process_area = process_area.filter(coordinates_filter=geospatial_filter)

    process_area_gdf = process_area.to_gdf(epsg_code=25832)
    process_area_style = {
        'fillOpacity': .2,
        'color': 'black',
        'weight': 2,
    }
    process_area_layer = Layer(
        gdf=process_area_gdf,
        style=process_area_style,
    )

    gdf_style = {
        'fillOpacity': 0,
        'color': '#FF595E',
        'weight': 2,
    }
    gdf_layer = Layer(
        gdf=gdf,
        style=gdf_style,
    )

    layers = [process_area_layer, gdf_layer]
    dir_path = Path(__file__).parents[1] / 'how_to_guides' / 'api' / 'maps'
    path = dir_path / 'process_area_filter_intersection.html'

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
