## How to use the process area

Follow along this step-by-step guide to learn about the [ProcessArea](../../api_reference/process_area.md) class.

???+ note "Open in Google Colab"
    Open the how-to guide as an interactive [notebook](https://githubtocolab.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_process_area.ipynb)
    in [Google Colab](https://colab.google)
    or download the [notebook](https://github.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_process_area.ipynb) to run it locally.

### Create a process area

A process area specifies the area of interest by a set of coordinates of the bottom left corner of each tile.

By default, a new instance of the `ProcessArea` class has no coordinates.<br />
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

If you already have the coordinates, you can pass them to the initializer of the `ProcessArea` class.

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

---

#### Create a process area from a bounding box

You can create a process area from a bounding box with the `from_bounding_box` class method.

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

---

#### Create a process area from a geodataframe

You can create a process area from a geodataframe with the `from_gdf` class method.

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

---

The geodataframe may contain multiple polygons, e.g. the administrative areas of Gelsenkirchen and Recklinghausen.

``` python
url = (
    'https://raw.githubusercontent.com/geospaitial-lab/aviary/main'
    '/docs/how_to_guides/api/notebooks/administrative_areas.geojson'
)
gdf = gpd.read_file(url)
process_area = aviary.ProcessArea.from_gdf(
    gdf=gdf,
    tile_size=128,
    quantize=True,
)

print(process_area.coordinates)
```

``` title="Output"
[[ 368000 5704960]
 [ 368128 5704960]
 [ 367360 5705088]
 ...
 [ 375424 5723648]
 [ 374656 5723776]
 [ 374784 5723776]]
```

---

#### Create a process area from a json string

You can create a process area from a json string with the `from_json` class method.

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

---

### Add or subtract process areas

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

---

### Append coordinates to the process area

You can append coordinates to the process area with the `append` method.

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

You can chunk the process area into multiple process areas with the `chunk` method.<br />
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

TODO

---

### Convert the process area to a geodataframe

You can convert the process area to a geodataframe with the `to_gdf` method.

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

You can convert the process area to a json string with the `to_json` method.

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
