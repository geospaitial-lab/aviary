import geopandas as gpd
import numpy as np
from shapely.geometry import box

coordinates = np.array([[-128, -128], [0, -128], [-128, 0], [0, 0]], dtype=np.int32)

data_test_duplicates_filter = [
    # test case 1: coordinates contains no duplicates
    (
        coordinates,
        coordinates,
    ),
    # test case 2: coordinates contains duplicates
    (
        np.array([[-128, -128], [0, -128], [-128, 0], [0, 0], [-128, 0], [0, 0]], dtype=np.int32),
        coordinates,
    ),
]

grid = gpd.GeoDataFrame(
    geometry=[
        box(-128, -128, 0, 0),
        box(0, -128, 128, 0),
        box(-128, 0, 0, 128),
        box(0, 0, 128, 128),
    ],
    crs='EPSG:25832',
)

data_test__geospatial_filter_difference = [
    # test case 1: gdf contains no polygons
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[],
            crs='EPSG:25832',
        ),
        coordinates,
    ),
    # test case 2: gdf contains a polygon that does not intersect any tile
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-256, -256, -192, -192)],
            crs='EPSG:25832',
        ),
        coordinates,
    ),
    # test case 3: gdf contains a polygon that does not overlap any tile
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-256, -256, -128, -128)],
            crs='EPSG:25832',
        ),
        coordinates,
    ),
    # test case 4: gdf contains a polygon that intersects a tile
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-96, -96, -32, -32)],
            crs='EPSG:25832',
        ),
        coordinates,
    ),
    # test case 5: gdf contains a polygon that overlaps a tile
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-128, -128, 0, 0)],
            crs='EPSG:25832',
        ),
        np.array([[0, -128], [-128, 0], [0, 0]], dtype=np.int32),
    ),
    # test case 6: gdf contains a polygon that intersects multiple tiles
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-64, -64, 64, 64)],
            crs='EPSG:25832',
        ),
        coordinates,
    ),
    # test case 7: gdf contains a polygon that overlaps multiple tiles
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-128, -128, 128, 128)],
            crs='EPSG:25832',
        ),
        np.empty(shape=(0, 2), dtype=np.int32),
    ),
]

data_test__geospatial_filter_intersection = [
    # test case 1: gdf contains no polygons
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[],
            crs='EPSG:25832',
        ),
        np.empty(shape=(0, 2), dtype=np.int32),
    ),
    # test case 2: gdf contains a polygon that does not intersect any tile
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-256, -256, -192, -192)],
            crs='EPSG:25832',
        ),
        np.empty(shape=(0, 2), dtype=np.int32),
    ),
    # test case 3: gdf contains a polygon that does not overlap any tile
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-256, -256, -128, -128)],
            crs='EPSG:25832',
        ),
        np.array([[-128, -128]], dtype=np.int32),
    ),
    # test case 4: gdf contains a polygon that intersects a tile
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-96, -96, -32, -32)],
            crs='EPSG:25832',
        ),
        np.array([[-128, -128]], dtype=np.int32),
    ),
    # test case 5: gdf contains a polygon that overlaps a tile
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-128, -128, 0, 0)],
            crs='EPSG:25832',
        ),
        coordinates,
    ),
    # test case 6: gdf contains a polygon that intersects multiple tiles
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-64, -64, 64, 64)],
            crs='EPSG:25832',
        ),
        coordinates,
    ),
    # test case 7: gdf contains a polygon that overlaps multiple tiles
    (
        coordinates,
        grid,
        gpd.GeoDataFrame(
            geometry=[box(-128, -128, 128, 128)],
            crs='EPSG:25832',
        ),
        coordinates,
    ),
]

data_test_mask_filter = [
    (
        coordinates,
        np.array([0, 1, 0, 1], dtype=np.bool_),
        np.array([[0, -128], [0, 0]], dtype=np.int32),
    ),
]

data_test__set_filter_difference = [
    # test case 1: additional_coordinates contains no coordinates
    (
        coordinates,
        np.empty(shape=(0, 2), dtype=np.int32),
        coordinates,
    ),
    # test case 2: additional_coordinates contains no coordinates of coordinates
    (
        coordinates,
        np.array([[128, -128], [128, 0]], dtype=np.int32),
        coordinates,
    ),
    # test case 3: additional_coordinates contains coordinates of coordinates
    (
        coordinates,
        np.array([[-128, 0], [0, 0]], dtype=np.int32),
        np.array([[-128, -128], [0, -128]], dtype=np.int32),
    ),
    # test case 4: additional_coordinates contains all coordinates of coordinates
    (
        coordinates,
        coordinates,
        np.empty(shape=(0, 2), dtype=np.int32),
    ),
]

data_test__set_filter_intersection = [
    # test case 1: additional_coordinates contains no coordinates
    (
        coordinates,
        np.empty(shape=(0, 2), dtype=np.int32),
        np.empty(shape=(0, 2), dtype=np.int32),
    ),
    # test case 2: additional_coordinates contains no coordinates of coordinates
    (
        coordinates,
        np.array([[128, -128], [128, 0]], dtype=np.int32),
        np.empty(shape=(0, 2), dtype=np.int32),
    ),
    # test case 3: additional_coordinates contains coordinates of coordinates
    (
        coordinates,
        np.array([[-128, 0], [0, 0]], dtype=np.int32),
        np.array([[-128, 0], [0, 0]], dtype=np.int32),
    ),
    # test case 4: additional_coordinates contains all coordinates of coordinates
    (
        coordinates,
        coordinates,
        coordinates,
    ),
]

data_test__set_filter_union = [
    # test case 1: additional_coordinates contains no coordinates
    (
        coordinates,
        np.empty(shape=(0, 2), dtype=np.int32),
        coordinates,
    ),
    # test case 2: additional_coordinates contains no coordinates of coordinates
    (
        coordinates,
        np.array([[128, -128], [128, 0]], dtype=np.int32),
        np.array([[-128, -128], [0, -128], [-128, 0], [0, 0], [128, -128], [128, 0]], dtype=np.int32),
    ),
    # test case 3: additional_coordinates contains coordinates of coordinates
    (
        coordinates,
        np.array([[-128, 0], [0, 0]], dtype=np.int32),
        coordinates,
    ),
    # test case 4: additional_coordinates contains all coordinates of coordinates
    (
        coordinates,
        coordinates,
        coordinates,
    ),
]
