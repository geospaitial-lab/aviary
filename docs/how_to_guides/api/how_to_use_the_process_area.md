## How to use the process area

Follow along this step-by-step guide to learn about the [`ProcessArea`][ProcessArea].

???+ note "Open in Google Colab"
    Open the how-to guide as an interactive [notebook][notebook colab] in [Google Colab]
    or download the [notebook][notebook github] to run it locally.

  [ProcessArea]: ../../api_reference/process_area.md
  [notebook colab]: https://www.githubtocolab.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_process_area.ipynb
  [Google Colab]: https://colab.google
  [notebook github]: https://www.github.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_process_area.ipynb

### Create a process area

A process area specifies the area of interest by a set of coordinates of the bottom left corner of each tile
and the tile size.

By default, a new instance of the [`ProcessArea`][ProcessArea] has no coordinates, just a tile size
that you can pass to its initializer.<br />
You can access the coordinates of the process area with the `coordinates` attribute,
which is a numpy array of shape (n, 2) and data type int32.
You can also access the tile size with the `tile_size` attribute.

  [ProcessArea]: ../../api_reference/process_area.md

``` python
import aviary

process_area = aviary.ProcessArea(tile_size=128)

print(process_area.coordinates)
print(process_area.tile_size)
```

``` title="Output"
[]
128
```

---

If you already have the coordinates, you can pass them with the tile size to the initializer
of the [`ProcessArea`][ProcessArea].

  [ProcessArea]: ../../api_reference/process_area.md

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
process_area = aviary.ProcessArea(
    coordinates=coordinates,
    tile_size=128,
)

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
```

We can visualize the process area.

<div id="process-area"></div>

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

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326]],
    tile_size=128,
)
```

We can visualize the process area.

<div id="process-area-setter-coordinates"></div>

---

You can also set the tile size of an already created process area with the `tile_size` attribute.

``` python
process_area.tile_size = 64

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326]],
    tile_size=64,
)
```

We can visualize the process area.

<div id="process-area-setter-tile-size"></div>

---

You can access the area of the process area with the `area` attribute.

``` python
print(process_area.area)
```

``` title="Output"
8192
```

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

print(sliced_process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326]],
    tile_size=64,
)
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

You can create a process area from a bounding box with the [`from_bounding_box`][from_bounding_box] class method.

  [from_bounding_box]: ../../api_reference/process_area.md#aviary.ProcessArea.from_bounding_box

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

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
```

We can visualize the process area.<br />
The red polygon represents the bounding box.

<div id="process-area-from-bounding-box"></div>

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

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363180, 5715326], ..., [363180, 5715518], [363276, 5715518]],
    tile_size=96,
)
```

We can visualize the process area.<br />
The red polygon represents the bounding box.

<div id="process-area-from-bounding-box-tile-size"></div>

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

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363008, 5715200], [363136, 5715200], ..., [363136, 5715456], [363264, 5715456]],
    tile_size=128,
)
```

We can visualize the process area.<br />
The red polygon represents the bounding box.

<div id="process-area-from-bounding-box-quantize"></div>

---

#### Create a process area from a geodataframe

You can create a process area from a geodataframe with the [`from_gdf`][from_gdf] class method.

  [from_gdf]: ../../api_reference/process_area.md#aviary.ProcessArea.from_gdf

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

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
```

We can visualize the process area.<br />
The red polygon represents the geodataframe.

<div id="process-area-from-gdf"></div>

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

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[364288, 5713664], [364544, 5713664], ..., [363264, 5721856], [363520, 5721856]],
    tile_size=256,
)
```

We can visualize the process area.<br />
The red polygons represent the districts.

<div id="process-area-from-gdf-districts"></div>

---

#### Create a process area from a json string

You can create a process area from a json string with the [`from_json`][from_json] class method.

  [from_json]: ../../api_reference/process_area.md#aviary.ProcessArea.from_json

``` python
json_string = (
    '{"coordinates": '
    '[[363084, 5715326], '
    '[363212, 5715326], '
    '[363084, 5715454], '
    '[363212, 5715454]], '
    '"tile_size": 128}'
)
process_area = aviary.ProcessArea.from_json(json_string=json_string)

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
```

We can visualize the process area.

<div id="process-area"></div>

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

print(process_area_1)
print(process_area_2)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
ProcessArea(
    coordinates=[[363212, 5715454], [363340, 5715454], [363212, 5715582], [363340, 5715582]],
    tile_size=128,
)
```

``` python
process_area = process_area_1 + process_area_2

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], ..., [363212, 5715582], [363340, 5715582]],
    tile_size=128,
)
```

We can visualize the process area.<br />
The red polygons represent the first process area and the blue polygons represent the second process area.

<div id="process-area-add"></div>

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

print(process_area_1)
print(process_area_2)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
ProcessArea(
    coordinates=[[363212, 5715454], [363340, 5715454], [363212, 5715582], [363340, 5715582]],
    tile_size=128,
)
```

``` python
process_area = process_area_1 - process_area_2

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454]],
    tile_size=128,
)
```

We can visualize the process area.<br />
The red polygons represent the first process area and the blue polygons represent the second process area.

<div id="process-area-sub"></div>

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

print(process_area_1)
print(process_area_2)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
ProcessArea(
    coordinates=[[363212, 5715454], [363340, 5715454], [363212, 5715582], [363340, 5715582]],
    tile_size=128,
)
```

``` python
process_area = process_area_1 & process_area_2

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363212, 5715454]],
    tile_size=128,
)
```

We can visualize the process area.<br />
The red polygons represent the first process area and the blue polygons represent the second process area.

<div id="process-area-and"></div>

---

### Append coordinates to the process area

You can append coordinates to the process area with the [`append`][append] method.

  [append]: ../../api_reference/process_area.md#aviary.ProcessArea.append

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
process_area = aviary.ProcessArea(
    coordinates=coordinates,
    tile_size=128,
)

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
```

``` python
process_area = process_area.append((363340, 5715582))

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], ..., [363212, 5715454], [363340, 5715582]],
    tile_size=128,
)
```

We can visualize the process area.

<div id="process-area-append"></div>

---

If you want to append coordinates that already exist, the process area will not change.

``` python
process_area = process_area.append((363340, 5715582))

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], ..., [363212, 5715454], [363340, 5715582]],
    tile_size=128,
)
```

---

### Chunk the process area

You can chunk the process area into multiple process areas with the [`chunk`][chunk] method.<br />
This might be useful when you want to run multiple pipelines in distributed environments.

  [chunk]: ../../api_reference/process_area.md#aviary.ProcessArea.chunk

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
process_area = aviary.ProcessArea(
    coordinates=coordinates,
    tile_size=128,
)

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
```

``` python
process_areas = process_area.chunk(num_chunks=2)

for process_area in process_areas:
    print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326]],
    tile_size=128,
)
ProcessArea(
    coordinates=[[363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
```

---

### Filter the process area

You can filter the process area with the [`filter`][filter] method.<br />
This method applies a [`CoordinatesFilter`][CoordinatesFilter] to the coordinates of the process area.

In this example, we will filter the process area based on geospatial data with the
[`GeospatialFilter`][GeospatialFilter].<br />
You can remove coordinates of tiles that are within the polygons in the geodataframe with the difference mode.

  [filter]: ../../api_reference/process_area.md#aviary.ProcessArea.filter
  [CoordinatesFilter]: ../../api_reference/geodata/coordinates_filter/coordinates_filter.md
  [GeospatialFilter]: ../../api_reference/geodata/coordinates_filter/geospatial_filter.md

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
process_area = aviary.ProcessArea(
    coordinates=coordinates,
    tile_size=128,
)

gdf = gpd.GeoDataFrame(
    geometry=[box(363212, 5715454, 363468, 5715710)],
    crs='EPSG:25832',
)

print(process_area)
print(gdf)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
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

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454]],
    tile_size=128,
)
```

We can visualize the process area.<br />
The red polygon represents the geodataframe.

<div id="process-area-filter-difference"></div>

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
process_area = aviary.ProcessArea(
    coordinates=coordinates,
    tile_size=128,
)

gdf = gpd.GeoDataFrame(
    geometry=[box(363212, 5715454, 363468, 5715710)],
    crs='EPSG:25832',
)

print(process_area)
print(gdf)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
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

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363212, 5715454]],
    tile_size=128,
)
```

We can visualize the process area.<br />
The red polygon represents the geodataframe.

<div id="process-area-filter-intersection"></div>

---

### Convert the process area to a geodataframe

You can convert the process area to a geodataframe with the [`to_gdf`][to_gdf] method.

  [to_gdf]: ../../api_reference/process_area.md#aviary.ProcessArea.to_gdf

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
process_area = aviary.ProcessArea(
    coordinates=coordinates,
    tile_size=128,
)

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
```

``` python
gdf = process_area.to_gdf(epsg_code=25832)

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

You can convert the process area to a json string with the [`to_json`][to_json] method.

  [to_json]: ../../api_reference/process_area.md#aviary.ProcessArea.to_json

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
process_area = aviary.ProcessArea(
    coordinates=coordinates,
    tile_size=128,
)

print(process_area)
```

``` title="Output"
ProcessArea(
    coordinates=[[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]],
    tile_size=128,
)
```

``` python
json_string = process_area.to_json()

print(json_string)
```

``` title="Output"
{"coordinates": [[363084, 5715326], [363212, 5715326], [363084, 5715454], [363212, 5715454]], "tile_size": 128}
```
