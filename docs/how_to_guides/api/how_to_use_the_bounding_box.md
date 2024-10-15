## How to use the bounding box

Follow along this step-by-step guide to learn about the [`BoundingBox`][BoundingBox].

???+ note "Open in Google Colab"
    Open the how-to guide as an interactive [notebook][notebook colab] in [Google Colab]
    or download the [notebook][notebook github] to run it locally.

  [BoundingBox]: ../../api_reference/bounding_box.md
  [notebook colab]: https://www.githubtocolab.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_bounding_box.ipynb
  [Google Colab]: https://colab.google
  [notebook github]: https://www.github.com/geospaitial-lab/aviary/blob/main/docs/how_to_guides/api/notebooks/how_to_use_the_bounding_box.ipynb

### Create a bounding box

A bounding box specifies the spatial extent of an area of interest.

You can pass the coordinates to the initializer of the [`BoundingBox`][BoundingBox].<br />
You can access the coordinates of the bounding box with the `x_min`, `y_min`, `x_max` and `y_max` attributes.

  [BoundingBox]: ../../api_reference/bounding_box.md

``` python
import aviary

bounding_box = aviary.BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)

print(bounding_box.x_min)
print(bounding_box.y_min)
print(bounding_box.x_max)
print(bounding_box.y_max)
```

``` title="Output"
363084
5715326
363340
5715582
```

We can visualize the bounding box.

<div id="bounding-box"></div>

---

You can set the coordinates of an already created bounding box with the
`x_min`, `y_min`, `x_max` and `y_max` attributes.

``` python
bounding_box.x_min = 363148
bounding_box.y_min = 5715390
bounding_box.x_max = 363276
bounding_box.y_max = 5715518

print(bounding_box.x_min)
print(bounding_box.y_min)
print(bounding_box.x_max)
print(bounding_box.y_max)
```

``` title="Output"
363148
5715390
363276
5715518
```

We can visualize the bounding box.

<div id="bounding-box-setter"></div>

---

A bounding box is an iterable object, so it supports indexing, length and iteration.

You can access the coordinates of the bounding box with the index operator.

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
363148
5715390
363276
5715518
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
363148
5715390
363276
5715518
```

A bounding box has a length, which is obviously 4.

``` python
print(len(bounding_box))
```

``` title="Output"
4
```

You can iterate over the coordinates of the bounding box.

``` python
for coordinate in bounding_box:
    print(coordinate)
```

``` title="Output"
363148
5715390
363276
5715518
```

---

#### Create a bounding box from a geodataframe

You can create a bounding box from a geodataframe with the [`from_gdf`][from_gdf] class method.

  [from_gdf]: ../../api_reference/bounding_box.md#aviary.BoundingBox.from_gdf

``` python
import geopandas as gpd
from shapely.geometry import box

gdf = gpd.GeoDataFrame(
    geometry=[box(363084, 5715326, 363340, 5715582)],
    crs='EPSG:25832',
)
bounding_box = aviary.BoundingBox.from_gdf(gdf=gdf)

print(bounding_box.x_min)
print(bounding_box.y_min)
print(bounding_box.x_max)
print(bounding_box.y_max)
```

``` title="Output"
363084
5715326
363340
5715582
```

We can visualize the bounding box.<br />
The red polygon represents the geodataframe.

<div id="bounding-box-from-gdf"></div>

---

The geodataframe may contain multiple polygons, e.g. the northern districts of Gelsenkirchen.

``` python
url = (
    'https://raw.githubusercontent.com/geospaitial-lab/aviary/main'
    '/docs/how_to_guides/api/data/districts.geojson'
)
gdf = gpd.read_file(url)
bounding_box = aviary.BoundingBox.from_gdf(gdf=gdf)

print(bounding_box.x_min)
print(bounding_box.y_min)
print(bounding_box.x_max)
print(bounding_box.y_max)
```

``` title="Output"
360695
5713811
367384
5721922
```

We can visualize the bounding box.<br />
The red polygons represent the districts.

<div id="bounding-box-from-gdf-districts"></div>

---

### Buffer the bounding box

You can expand the bounding box with the [`buffer`][buffer] method.

  [buffer]: ../../api_reference/bounding_box.md#aviary.BoundingBox.buffer

``` python
bounding_box = aviary.BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)

print(bounding_box.x_min)
print(bounding_box.y_min)
print(bounding_box.x_max)
print(bounding_box.y_max)
```

``` title="Output"
363084
5715326
363340
5715582
```

``` python
buffered_bounding_box = bounding_box.buffer(buffer_size=64)

print(buffered_bounding_box.x_min)
print(buffered_bounding_box.y_min)
print(buffered_bounding_box.x_max)
print(buffered_bounding_box.y_max)
```

``` title="Output"
363020
5715262
363404
5715646
```

We can visualize the bounding box.<br />
The red polygon represents the original bounding box.

<div id="bounding-box-buffer-1"></div>

---

You can also shrink the bounding box with the [`buffer`][buffer] method.

  [buffer]: ../../api_reference/bounding_box.md#aviary.BoundingBox.buffer

``` python
bounding_box = aviary.BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)

print(bounding_box.x_min)
print(bounding_box.y_min)
print(bounding_box.x_max)
print(bounding_box.y_max)
```

``` title="Output"
363084
5715326
363340
5715582
```

``` python
buffered_bounding_box = bounding_box.buffer(buffer_size=-64)

print(buffered_bounding_box.x_min)
print(buffered_bounding_box.y_min)
print(buffered_bounding_box.x_max)
print(buffered_bounding_box.y_max)
```

``` title="Output"
363148
5715390
363276
5715518
```

We can visualize the bounding box.<br />
The red polygon represents the original bounding box.

<div id="bounding-box-buffer-2"></div>

---

### Quantize the bounding box

You can align the bounding box to a grid with the [`quantize`][quantize] method.

  [quantize]: ../../api_reference/bounding_box.md#aviary.BoundingBox.quantize

``` python
bounding_box = aviary.BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)

print(bounding_box.x_min)
print(bounding_box.y_min)
print(bounding_box.x_max)
print(bounding_box.y_max)
```

``` title="Output"
363084
5715326
363340
5715582
```

``` python
quantized_bounding_box = bounding_box.quantize(value=128)

print(quantized_bounding_box.x_min)
print(quantized_bounding_box.y_min)
print(quantized_bounding_box.x_max)
print(quantized_bounding_box.y_max)
```

``` title="Output"
363008
5715200
363392
5715584
```

We can visualize the bounding box.<br />
The red polygon represents the original bounding box.

<div id="bounding-box-quantize"></div>

---

### Convert the bounding box to a geodataframe

You can convert the bounding box to a geodataframe with the [`to_gdf`][to_gdf] method.

  [to_gdf]: ../../api_reference/bounding_box.md#aviary.BoundingBox.to_gdf

``` python
bounding_box = aviary.BoundingBox(
    x_min=363084,
    y_min=5715326,
    x_max=363340,
    y_max=5715582,
)

print(bounding_box.x_min)
print(bounding_box.y_min)
print(bounding_box.x_max)
print(bounding_box.y_max)
```

``` title="Output"
363084
5715326
363340
5715582
```

``` python
gdf = bounding_box.to_gdf(epsg_code=25832)

print(gdf)
```

``` title="Output"
                                            geometry
0  POLYGON ((363340 5715326, 363340 5715582, 3630...
```
