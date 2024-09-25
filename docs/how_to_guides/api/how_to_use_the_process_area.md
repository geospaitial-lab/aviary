## How to use the process area

Follow along this step-by-step guide to learn about the [`ProcessArea`](../../api_reference/process_area.md).

???+ note "Open in Google Colab"
    Open the how-to guide as an interactive
    [notebook](https://githubtocolab.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_process_area.ipynb)
    in [Google Colab](https://colab.google)
    or download the
    [notebook](https://github.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_process_area.ipynb) to run it locally.

### Create a process area

A process area specifies the area of interest by a set of coordinates of the bottom left corner of each tile.

By default, a new instance of the [`ProcessArea`](../../api_reference/process_area.md) has no coordinates.<br />
You can access the coordinates of the process area with the `coordinates` attribute,
which is a numpy array of shape (n, 2) and data type int32.

``` python
import aviary

process_area = aviary.ProcessArea()

print(process_area.coordinates)
```

``` title="Output"
[]
```

---

If you already have the coordinates, you can pass them to the initializer of the
[`ProcessArea`](../../api_reference/process_area.md).

``` python
import numpy as np

coordinates = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area = aviary.ProcessArea(coordinates=coordinates)

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
```

We can visualize the process area given the tile size.

<iframe src="../maps/process_area.html" width="100%" height="300px"></iframe>

---

You can set the coordinates of an already created process area with the `coordinates` attribute.

``` python
coordinates = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
    ],
    dtype=np.int32,
)
process_area.coordinates = coordinates

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]]
```

We can visualize the process area given the tile size.

<iframe src="../maps/process_area_setter.html" width="100%" height="300px"></iframe>

---

A process area is an iterable object, so it supports indexing, length and iteration.

You can access the coordinates of the process area with the index operator.

``` python
coordinates_1 = process_area[0]
coordinates_2 = process_area[1]

print(coordinates_1)
print(coordinates_2)
```

``` title="Output"
(363084, 5715326)
(363212, 5715326)
```

You can slice the process area to create a new process area of a subset of the coordinates with the index operator
and the colon operator.

``` python
sliced_process_area = process_area[:-1]

print(sliced_process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]]
```

A process area has a length, which is equal to the number of coordinates, i.e. the number of tiles.

``` python
print(len(process_area))
```

``` title="Output"
2
```

You can iterate over the coordinates of the process area.

``` python
for coordinates in process_area:
    print(coordinates)
```

``` title="Output"
(363084, 5715326)
(363212, 5715326)
```

---

#### Create a process area from a bounding box

You can create a process area from a bounding box with the
[`from_bounding_box`](../../api_reference/process_area.md#aviary.ProcessArea.from_bounding_box) class method.

``` python
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

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
```

We can visualize the process area given the tile size.<br />
The red polygon represents the bounding box.

<iframe src="../maps/process_area_from_bounding_box.html" width="100%" height="300px"></iframe>

---

You can set the tile size of the process area with the `tile_size` parameter.<br />
If the bounding box is not divisible by the tile size, the tiles will extend beyond the bounding box.

``` python
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

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363180 5715326]
 [ 363276 5715326]
 [ 363084 5715422]
 [ 363180 5715422]
 [ 363276 5715422]
 [ 363084 5715518]
 [ 363180 5715518]
 [ 363276 5715518]]
```

We can visualize the process area given the tile size.<br />
The red polygon represents the bounding box.

<iframe src="../maps/process_area_from_bounding_box_tile_size.html" width="100%" height="300px"></iframe>

---

You can quantize the process area with the `quantize` parameter.<br />
If the coordinates are not divisible by the tile size, the coordinates will be quantized to the tile size.<br />
This might be useful when you want to ensure matching tiles for different process areas.

``` python
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

print(process_area.coordinates)
```

``` title="Output"
[[ 363008 5715200]
 [ 363136 5715200]
 [ 363264 5715200]
 [ 363008 5715328]
 [ 363136 5715328]
 [ 363264 5715328]
 [ 363008 5715456]
 [ 363136 5715456]
 [ 363264 5715456]]
```

We can visualize the process area given the tile size.<br />
The red polygon represents the bounding box.

<iframe src="../maps/process_area_from_bounding_box_quantize.html" width="100%" height="300px"></iframe>

---

#### Create a process area from a geodataframe

You can create a process area from a geodataframe with the
[`from_gdf`](../../api_reference/process_area.md#aviary.ProcessArea.from_gdf) class method.

``` python
import geopandas as gpd
from shapely.geometry import box

gdf = gpd.GeoDataFrame(
    geometry=[box(363084, 5715326, 363340, 5715582)],
    crs='EPSG:25832',
)
process_area = aviary.ProcessArea.from_gdf(
    gdf=gdf,
    tile_size=128,
    quantize=False,
)

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
```

We can visualize the process area given the tile size.<br />
The red polygon represents the geodataframe.

<iframe src="../maps/process_area_from_gdf.html" width="100%" height="300px"></iframe>

---

The geodataframe may contain multiple polygons, e.g. the northern districts of Gelsenkirchen.

``` python
url = (
    'https://raw.githubusercontent.com/geospaitial-lab/aviary/main'
    '/docs/how_to_guides/api/data/districts.geojson'
)
gdf = gpd.read_file(url)
process_area = aviary.ProcessArea.from_gdf(
    gdf=gdf,
    tile_size=256,
    quantize=True,
)

print(process_area.coordinates)
```

``` title="Output"
[[ 364288 5713664]
 [ 364544 5713664]
 [ 364800 5713664]
 ...
 [ 363008 5721856]
 [ 363264 5721856]
 [ 363520 5721856]]
```

We can visualize the process area given the tile size.<br />
The red polygons represent the districts.

<iframe src="../maps/process_area_from_gdf_districts.html" width="100%" height="300px"></iframe>

---

#### Create a process area from a json string

You can create a process area from a json string with the
[`from_json`](../../api_reference/process_area.md#aviary.ProcessArea.from_json) class method.

``` python
json_string = (
    '[[363084, 5715326], '
    '[363212, 5715326], '
    '[363084, 5715454], '
    '[363212, 5715454]]'
)
process_area = aviary.ProcessArea.from_json(json_string=json_string)

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
```

We can visualize the process area given the tile size.

<iframe src="../maps/process_area.html" width="100%" height="300px"></iframe>

---

### Add, subtract or intersect process areas

You can add two process areas with the `+` operator.<br />
If the process areas overlap, the resulting process area will contain the union of the two process areas.

``` python
coordinates_1 = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area_1 = aviary.ProcessArea(coordinates=coordinates_1)

coordinates_2 = np.array(
    [
        [363212, 5715454],
        [363340, 5715454],
        [363212, 5715582],
        [363340, 5715582],
    ],
    dtype=np.int32,
)
process_area_2 = aviary.ProcessArea(coordinates=coordinates_2)

print(process_area_1.coordinates)
print(process_area_2.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
[[ 363212 5715454]
 [ 363340 5715454]
 [ 363212 5715582]
 [ 363340 5715582]]
```

``` python
process_area = process_area_1 + process_area_2

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]
 [ 363340 5715454]
 [ 363212 5715582]
 [ 363340 5715582]]
```

We can visualize the process area given the tile size.<br />
The red polygons represent the first process area and the blue polygons represent the second process area.

<iframe src="../maps/process_area_add.html" width="100%" height="300px"></iframe>

---

You can subtract two process areas with the `-` operator.

``` python
coordinates_1 = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area_1 = aviary.ProcessArea(coordinates=coordinates_1)

coordinates_2 = np.array(
    [
        [363212, 5715454],
        [363340, 5715454],
        [363212, 5715582],
        [363340, 5715582],
    ],
    dtype=np.int32,
)
process_area_2 = aviary.ProcessArea(coordinates=coordinates_2)

print(process_area_1.coordinates)
print(process_area_2.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
[[ 363212 5715454]
 [ 363340 5715454]
 [ 363212 5715582]
 [ 363340 5715582]]
```

``` python
process_area = process_area_1 - process_area_2

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]]
```

We can visualize the process area given the tile size.<br />
The red polygons represent the first process area and the blue polygons represent the second process area.

<iframe src="../maps/process_area_sub.html" width="100%" height="300px"></iframe>

---

You can intersect two process areas with the `&` operator.

``` python
coordinates_1 = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area_1 = aviary.ProcessArea(coordinates=coordinates_1)

coordinates_2 = np.array(
    [
        [363212, 5715454],
        [363340, 5715454],
        [363212, 5715582],
        [363340, 5715582],
    ],
    dtype=np.int32,
)
process_area_2 = aviary.ProcessArea(coordinates=coordinates_2)

print(process_area_1.coordinates)
print(process_area_2.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
[[ 363212 5715454]
 [ 363340 5715454]
 [ 363212 5715582]
 [ 363340 5715582]]
```

``` python
process_area = process_area_1 & process_area_2

print(process_area.coordinates)
```

``` title="Output"
[[ 363212 5715454]]
```

We can visualize the process area given the tile size.<br />
The red polygons represent the first process area and the blue polygons represent the second process area.

<iframe src="../maps/process_area_and.html" width="100%" height="300px"></iframe>

---

### Append coordinates to the process area

You can append coordinates to the process area with the
[`append`](../../api_reference/process_area.md#aviary.ProcessArea.append) method.

``` python
coordinates = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area = aviary.ProcessArea(coordinates=coordinates)

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
```

``` python
process_area = process_area.append((363340, 5715582))

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]
 [ 363340 5715582]]
```

We can visualize the process area given the tile size.

<iframe src="../maps/process_area_append.html" width="100%" height="300px"></iframe>

---

If you want to append coordinates that already exist, the process area will not change.

``` python
process_area = process_area.append((363340, 5715582))

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]
 [ 363340 5715582]]
```

---

### Chunk the process area

You can chunk the process area into multiple process areas with the
[`chunk`](../../api_reference/process_area.md#aviary.ProcessArea.chunk) method.<br />
This might be useful when you want to run multiple pipelines in distributed environments.

``` python
coordinates = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area = aviary.ProcessArea(coordinates=coordinates)

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
```

``` python
process_areas = process_area.chunk(num_chunks=2)

for process_area in process_areas:
    print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]]
[[ 363084 5715454]
 [ 363212 5715454]]
```

---

### Filter the process area

You can filter the process area with the
[`filter`](../../api_reference/process_area.md#aviary.ProcessArea.filter) method.<br />
This method applies a
[`CoordinatesFilter`](../../api_reference/geodata/coordinates_filter/coordinates_filter.md)
to the coordinates of the process area.

In this example, we will filter the process area based on geospatial data with the
[`GeospatialFilter`](../../api_reference/geodata/coordinates_filter/geospatial_filter.md).<br />
You can remove coordinates of tiles that are within the polygons in the geodataframe with the difference mode.

``` python
coordinates = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area = aviary.ProcessArea(coordinates=coordinates)

gdf = gpd.GeoDataFrame(
    geometry=[box(363212, 5715454, 363468, 5715710)],
    crs='EPSG:25832',
)

print(process_area.coordinates)
print(gdf)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
                                            geometry
0  POLYGON ((363468 5715454, 363468 5715710, 3632...
```

``` python
from aviary.geodata import GeospatialFilter

geospatial_filter = GeospatialFilter(
    tile_size=128,
    gdf=gdf,
    mode=aviary.GeospatialFilterMode.DIFFERENCE,
)
process_area = process_area.filter(coordinates_filter=geospatial_filter)

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]]
```

We can visualize the process area given the tile size.<br />
The red polygon represents the geodataframe.

<iframe src="../maps/process_area_filter_difference.html" width="100%" height="300px"></iframe>

---

You can remove coordinates of tiles that don't intersect with the polygons in the geodataframe
with the intersection mode.

``` python
coordinates = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area = aviary.ProcessArea(coordinates=coordinates)

gdf = gpd.GeoDataFrame(
    geometry=[box(363212, 5715454, 363468, 5715710)],
    crs='EPSG:25832',
)

print(process_area.coordinates)
print(gdf)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
                                            geometry
0  POLYGON ((363468 5715454, 363468 5715710, 3632...
```

``` python
geospatial_filter = GeospatialFilter(
    tile_size=128,
    gdf=gdf,
    mode=aviary.GeospatialFilterMode.INTERSECTION,
)
process_area = process_area.filter(coordinates_filter=geospatial_filter)

print(process_area.coordinates)
```

``` title="Output"
[[ 363212 5715454]]
```

We can visualize the process area given the tile size.<br />
The red polygon represents the geodataframe.

<iframe src="../maps/process_area_filter_intersection.html" width="100%" height="300px"></iframe>

---

### Convert the process area to a geodataframe

You can convert the process area to a geodataframe with the
[`to_gdf`](../../api_reference/process_area.md#aviary.ProcessArea.to_gdf) method.

``` python
coordinates = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area = aviary.ProcessArea(coordinates=coordinates)

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
```

``` python
gdf = process_area.to_gdf(
    epsg_code=25832,
    tile_size=128,
)

print(gdf)
```

``` title="Output"
                                            geometry
0  POLYGON ((363212 5715326, 363212 5715454, 3630...
1  POLYGON ((363340 5715326, 363340 5715454, 3632...
2  POLYGON ((363212 5715454, 363212 5715582, 3630...
3  POLYGON ((363340 5715454, 363340 5715582, 3632...
```

---

### Convert the process area to a json string

You can convert the process area to a json string with the
[`to_json`](../../api_reference/process_area.md#aviary.ProcessArea.to_json) method.

``` python
coordinates = np.array(
    [
        [363084, 5715326],
        [363212, 5715326],
        [363084, 5715454],
        [363212, 5715454],
    ],
    dtype=np.int32,
)
process_area = aviary.ProcessArea(coordinates=coordinates)

print(process_area.coordinates)
```

``` title="Output"
[[ 363084 5715326]
 [ 363212 5715326]
 [ 363084 5715454]
 [ 363212 5715454]]
```

``` python
json_string = process_area.to_json()

print(json_string)
```

``` title="Output"
[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]]
```
