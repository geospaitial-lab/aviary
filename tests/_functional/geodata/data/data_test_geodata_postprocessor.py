import geopandas as gpd
from shapely.affinity import affine_transform
from shapely.geometry import Polygon

empty_gdf = gpd.GeoDataFrame(
    geometry=[],
    crs='EPSG:25832',
)

unit_polygon = Polygon([[0., 0.], [1., 0.], [1., 1.], [0., 1.]])

data_test_field_name_postprocessor = [
    # test case 1: gdf is empty
    (
        empty_gdf,
        {'class': 'type'},
        empty_gdf,
    ),
    # test case 2: gdf is not empty
    (
        gpd.GeoDataFrame(
            data={
                'geometry': [unit_polygon, unit_polygon],
                'class': [0, 1],
            },
            crs='EPSG:25832',
        ),
        {'class': 'type'},
        gpd.GeoDataFrame(
            data={
                'geometry': [unit_polygon, unit_polygon],
                'type': [0, 1],
            },
            crs='EPSG:25832',
        ),
    ),
]

exterior_polygon = affine_transform(unit_polygon, matrix=[64., 0., 0., 64., -32., -32.])
interior_polygons = [
    affine_transform(unit_polygon, matrix=[.5, 0., 0., .5, -16.25, -.25]),
    affine_transform(unit_polygon, matrix=[1., 0., 0., 1., -.5, -.5]),
    affine_transform(unit_polygon, matrix=[10., 0., 0., 10., 11., -5.]),
]

holes = [
    polygon.exterior.coords
    for polygon in interior_polygons
]
polygon = Polygon(exterior_polygon.exterior.coords, holes=holes)

holes_1 = [
    polygon.exterior.coords
    for polygon in interior_polygons
    if polygon.area >= 1.
]
filled_polygon_1 = Polygon(exterior_polygon.exterior.coords, holes=holes_1)

holes_10 = [
    polygon.exterior.coords
    for polygon in interior_polygons
    if polygon.area >= 10.
]
filled_polygon_10 = Polygon(exterior_polygon.exterior.coords, holes=holes_10)

data_test_fill_postprocessor = [
    # test case 1: gdf is empty
    (
        empty_gdf,
        1.,
        empty_gdf,
    ),
    # test case 2: gdf is not empty, max_area is 0
    (
        gpd.GeoDataFrame(
            geometry=[polygon],
            crs='EPSG:25832',
        ),
        0.,
        gpd.GeoDataFrame(
            geometry=[exterior_polygon],
            crs='EPSG:25832',
        ),
    ),
    # test case 3: gdf is not empty, max_area is 1
    (
        gpd.GeoDataFrame(
            geometry=[polygon],
            crs='EPSG:25832',
        ),
        1.,
        gpd.GeoDataFrame(
            geometry=[filled_polygon_1],
            crs='EPSG:25832',
        ),
    ),
    # test case 4: gdf is not empty, max_area is 10
    (
        gpd.GeoDataFrame(
            geometry=[polygon],
            crs='EPSG:25832',
        ),
        10.,
        gpd.GeoDataFrame(
            geometry=[filled_polygon_10],
            crs='EPSG:25832',
        ),
    ),
]

data_test__fill_polygon = [
    # test case 1: polygon has no holes
    (
        exterior_polygon,
        1.,
        exterior_polygon,
    ),
    # test case 2: polygon has holes, max_area is 0
    (
        polygon,
        0.,
        exterior_polygon,
    ),
    # test case 3: polygon has holes, max_area is 1
    (
        polygon,
        1.,
        filled_polygon_1,
    ),
    # test case 4: polygon has holes, max_area is 10
    (
        polygon,
        10.,
        filled_polygon_10,
    ),
]

polygons = [
    affine_transform(unit_polygon, matrix=[.5, 0., 0., .5, -16.25, -.25]),
    affine_transform(unit_polygon, matrix=[1., 0., 0., 1., -.5, -.5]),
    affine_transform(unit_polygon, matrix=[10., 0., 0., 10., 11., -5.]),
]

polygons_1 = [
    polygon
    for polygon in polygons
    if polygon.area >= 1.
]

polygons_10 = [
    polygon
    for polygon in polygons
    if polygon.area >= 10.
]

data_test_sieve_postprocessor = [
    # test case 1: gdf is empty
    (
        empty_gdf,
        1.,
        empty_gdf,
    ),
    # test case 2: gdf is not empty, min_area is 0
    (
        gpd.GeoDataFrame(
            geometry=polygons,
            crs='EPSG:25832',
        ),
        0.,
        gpd.GeoDataFrame(
            geometry=polygons,
            crs='EPSG:25832',
        ),
    ),
    # test case 3: gdf is not empty, min_area is 1
    (
        gpd.GeoDataFrame(
            geometry=polygons,
            crs='EPSG:25832',
        ),
        1.,
        gpd.GeoDataFrame(
            geometry=polygons_1,
            crs='EPSG:25832',
        ),
    ),
    # test case 4: gdf is not empty, min_area is 10
    (
        gpd.GeoDataFrame(
            geometry=polygons,
            crs='EPSG:25832',
        ),
        10.,
        gpd.GeoDataFrame(
            geometry=polygons_10,
            crs='EPSG:25832',
        ),
    ),
]

data_test_value_postprocessor = [
    # test case 1: gdf is empty
    (
        empty_gdf,
        {
            0: 'a',
            1: 'b',
        },
        'class',
        empty_gdf,
    ),
    # test case 2: gdf is not empty
    (
        gpd.GeoDataFrame(
            data={
                'geometry': [polygon, polygon, polygon, polygon],
                'class': [0, 1, 0, 1],
            },
            crs='EPSG:25832',
        ),
        {
            0: 'a',
            1: 'b',
        },
        'class',
        gpd.GeoDataFrame(
            data={
                'geometry': [polygon, polygon, polygon, polygon],
                'class': ['a', 'b', 'a', 'b'],
            },
            crs='EPSG:25832',
        ),
    ),
]
