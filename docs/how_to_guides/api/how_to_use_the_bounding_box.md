## How to use the bounding box

<span class="aviary-skill-level">Skill level: Beginner</span>

A bounding box specifies the spatial extent of an area of interest given its coordinates in meters:

- `x_min`: minimum x coordinate
- `y_min`: minimum y coordinate
- `x_max`: maximum x coordinate
- `y_max`: maximum y coordinate

View [API reference]

!!! colab "Open in Google Colab"
    Open the how-to guide as an interactive [notebook :material-arrow-top-right:][notebook colab] in [Google Colab :material-arrow-top-right:][Google Colab]
    or download the [notebook :material-arrow-top-right:][notebook github] to run it locally.

  [API reference]: ../../api_reference/core/bounding_box.md#aviary.BoundingBox
  [notebook colab]: https://www.githubtocolab.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_bounding_box.ipynb
  [Google Colab]: https://colab.google
  [notebook github]: https://www.github.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_bounding_box.ipynb

### Create a bounding box

You can pass the coordinates to the initializer of the bounding box.

``` python
import aviary

bounding_box = aviary.BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)

print(bounding_box)
```

``` title="Output"
BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)
```

<div id="bounding-box"></div>

You can access its coordinates using the [`x_min`][x_min], [`y_min`][y_min], [`x_max`][x_max], and [`y_max`][y_max] attributes.

  [x_min]: ../../api_reference/core/bounding_box.md#aviary.BoundingBox.x_min
  [y_min]: ../../api_reference/core/bounding_box.md#aviary.BoundingBox.y_min
  [x_max]: ../../api_reference/core/bounding_box.md#aviary.BoundingBox.x_max
  [y_max]: ../../api_reference/core/bounding_box.md#aviary.BoundingBox.y_max

``` python
x_min = bounding_box.x_min
y_min = bounding_box.y_min
x_max = bounding_box.x_max
y_max = bounding_box.y_max

print(x_min)
print(y_min)
print(x_max)
print(y_max)
```

``` title="Output"
363084
5715326
363340
5715582
```

The bounding box is an iterable object, so it supports indexing and iterating.

You can access its coordinates using the index operator.

``` python
x_min = bounding_box[0]
y_min = bounding_box[1]
x_max = bounding_box[2]
y_max = bounding_box[3]

print(x_min)
print(y_min)
print(x_max)
print(y_max)
```

``` title="Output"
363084
5715326
363340
5715582
```

You can also unpack its coordinates.

``` python
x_min, y_min, x_max, y_max = bounding_box

print(x_min)
print(y_min)
print(x_max)
print(y_max)
```

``` title="Output"
363084
5715326
363340
5715582
```

You can iterate over its coordinates.

``` python
for coordinate in bounding_box:
    print(coordinate)
```

``` title="Output"
363084
5715326
363340
5715582
```

The bounding box exposes its area via the [`area`][area] attribute.

  [area]: ../../api_reference/core/bounding_box.md#aviary.BoundingBox.area

``` python
area = bounding_box.area

print(area)
```

``` title="Output"
65536
```

#### Create a bounding box from a geodataframe

You can create a bounding box from a geodataframe using the [`from_gdf`][from_gdf] class method.

  [from_gdf]: ../../api_reference/core/bounding_box.md#aviary.BoundingBox.from_gdf

``` python
from shapely.geometry import box

gdf = gpd.GeoDataFrame(
    geometry=[box(363084, 5715326, 363340, 5715582)],
    crs='EPSG:25832',
)
bounding_box = aviary.BoundingBox.from_gdf(gdf=gdf)

print(bounding_box)
```

``` title="Output"
BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)
```

<div id="bounding-box-from-gdf"></div>

The geodataframe may contain multiple polygons, e.g., the districts of Gelsenkirchen.

``` python
url = (
    'https://raw.githubusercontent.com/geospaitial-lab/aviary/main/docs'
    '/how_to_guides/api/data/districts.geojson'
)
gdf = gpd.read_file(url)
bounding_box = aviary.BoundingBox.from_gdf(gdf=gdf)

print(bounding_box)
```

``` title="Output"
BoundingBox(
    x_min=360695,
    y_min=5705001,
    x_max=371763,
    y_max=5721922,
)
```

<div id="bounding-box-from-gdf-districts"></div>

### Intersect bounding boxes

You can intersect two bounding boxes using the `&` operator.

``` python
bounding_box_1 = aviary.BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)
bounding_box_2 = aviary.BoundingBox(
    x_min=363212,
    y_min=5715454,
    x_max=363468,
    y_max=5715710,
)

print(bounding_box_1)
print(bounding_box_2)
```

``` title="Output"
BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)
BoundingBox(
    x_min=363212,
    y_min=5715454,
    x_max=363468,
    y_max=5715710,
)
```

``` python
bounding_box = bounding_box_1 & bounding_box_2

print(bounding_box)
```

``` title="Output"
BoundingBox(
    x_min=363212,
    y_min=5715454,
    x_max=363340,
    y_max=5715582,
)
```

<div id="bounding-box-and"></div>

### Unite bounding boxes

You can unite two bounding boxes using the `|` operator.

``` python
bounding_box_1 = aviary.BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)
bounding_box_2 = aviary.BoundingBox(
    x_min=363212,
    y_min=5715454,
    x_max=363468,
    y_max=5715710,
)

print(bounding_box_1)
print(bounding_box_2)
```

``` title="Output"
BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)
BoundingBox(
    x_min=363212,
    y_min=5715454,
    x_max=363468,
    y_max=5715710,
)
```

``` python
bounding_box = bounding_box_1 | bounding_box_2

print(bounding_box)
```

``` title="Output"
BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363468,
    y_max=5715710,
)
```

<div id="bounding-box-or"></div>
