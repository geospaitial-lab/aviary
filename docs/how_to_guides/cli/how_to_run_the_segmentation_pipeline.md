<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## How to run the segmentation pipeline

Follow along this step-by-step guide to run the [segmentation pipeline](../../cli_reference/segmentation_pipeline.md)
with the command-line interface (CLI).

In this example, we will run the segmentation model [sparrow](../../aviary/index.md#sparrow)
on digital orthophotos to detect and classify impervious surfaces.<br />
Assume the data is stored in a virtual raster (.vrt file) and
meets the [requirements](../../aviary/index.md#requirements)
of the model (i.e. 4 channels with RGB (red, green, blue) and NIR (near-infrared) and
a ground sampling distance of at least 0.2m).<br />
Please consider using leaf-off orthophotos for the best results.

### Step 1: Create a configuration file

Create a configuration file (.yaml file) named `config.yaml`.

In the next steps, we will add the configuration of each component of the pipeline to this file.

---

### Step 2: Configure the data fetcher

To fetch the data from the virtual raster,
we will use the [`VRTFetcher`](../../api_reference/data/data_fetcher/vrt_fetcher.md)
with the following configuration:

``` yaml title="config.yaml"
data_fetcher:
  name: VRTFetcher
  config:
    path: path/to/your/data.vrt
    tile_size: 128
    ground_sampling_distance: 0.2
    buffer_size: 32
```

This configuration will fetch the data from the virtual raster in tiles of size 128x128 meters.<br />
In order to increase the quality of the predictions in the border area of the tiles,
a buffer of 32 meters (1/4 of the tile size) is additionally fetched around each tile.
This results in a tile size of 192x192 meters, i.e. 960x960 pixels
given a ground sampling distance of 0.2 meters.

???+ note "Notes"

    - The data is automatically resampled to the specified ground sampling distance
    - You may need to adjust the tile size and the buffer size depending on the available resources

Have a look at the [API reference](../../api_reference/data/data_fetcher/vrt_fetcher.md#aviary.data.VRTFetcherConfig)
for more details on the configuration options.

---

### Step 3: Configure the process area

To specify the area of interest,
we will use the [`ProcessArea`](../../api_reference/process_area.md)
with the following configuration:

``` yaml title="config.yaml"
process_area:
  bounding_box: [x_min, y_min, x_max, y_max]
  tile_size: 128
```

This configuration will create a set of coordinates of the bottom left corner of each tile
in the area of interest.

???+ note "Notes"

    - The coordinates of the bounding box are specified in the projected coordinate system of the data
    - The tile size must match the tile size of the data fetcher
    - You might need to exclude tiles that are already processed in a previous run
      by specifying the path to the JSON file named `processed_coordinates.json`
      containing the coordinates of the bottom left corner of the processed tiles
      (this file is created automatically by the [exporter](#step-6-configure-the-exporter) in the output directory)

Note that there are alternative ways to specify the area of interest,
e.g. by providing a path to a geodataframe (geopackage or shapefile)
containing the area of interest as a single polygon or a set of polygons.

Have a look at the [API reference](../../api_reference/process_area.md#aviary.ProcessAreaConfig)
for more details on the configuration options.

---

### Step 4: Configure the data preprocessor

To preprocess the fetched data,
we will use the [`NormalizePreprocessor`](../../api_reference/data/data_preprocessor/normalize_preprocessor.md)
with the following configuration:

``` yaml title="config.yaml"
data_preprocessor:
  name: NormalizePreprocessor
  config:
    min_values: [0.0, 0.0, 0.0, 0.0]
    max_values: [255.0, 255.0, 255.0, 255.0]
```

This configuration will scale the data to a range of 0 to 1
as stated in the [requirements](../../aviary/index.md#requirements) of the model.<br />
The data is assumed to be of data type `uint8` (8-bit unsigned integer),
where the minimum value is 0 and the maximum value is 255.

???+ note "Notes"

    - The minimum and maximum values are specified for each channel (red, green, blue, near-infrared)

Have a look at the [API reference](../../api_reference/data/data_preprocessor/normalize_preprocessor.md#aviary.data.NormalizePreprocessorConfig)
for more details on the configuration options.

---

### Step 5: Configure the model

To do the inference on the preprocessed data,
we will use the [`ONNXSegmentationModel`](../../api_reference/inference/model/onnx_segmentation_model.md)
with the following configuration:

``` yaml title="config.yaml"
model:
  name: ONNXSegmentationModel
  config:
    name: sparrow
    ground_sampling_distance: 0.2
    buffer_size: 32
```

This configuration will download the weights of the model sparrow.

???+ note "Notes"

    - The ground sampling distance must match the ground sampling distance of the data fetcher
    - The buffer size must match the buffer size of the data fetcher
    - The buffer is removed from the predictions after the inference

Have a look at the [API reference](../../api_reference/inference/model/segmentation_model.md#aviary.inference.SegmentationModelConfig)
for more details on the configuration options.

---

### Step 6: Configure the exporter

To export the predictions dynamically as geospatial data,
we will use the [`SegmentationExporter`](../../api_reference/inference/exporter/segmentation_exporter.md)
with the following configuration:

``` yaml title="config.yaml"
exporter:
  name: SegmentationExporter
  config:
    path: path/to/your/output_directory
    tile_size: 128
    ground_sampling_distance: 0.2
    epsg_code: 25832
    num_workers: 4
```

This configuration will transform the predictions (i.e. raster data) to geospatial data (i.e. vector data)
and export the resulting geodataframe dynamically to a geopackage named `output.gpkg`
in the specified output directory.<br />
The coordinates of the bottom left corner of the processed tiles are exported dynamically to a JSON file
named `processed_coordinates.json`.

???+ note "Notes"

    - The tile size must match the tile size of the data fetcher
    - The ground sampling distance must match the ground sampling distance of the data fetcher
    - You may need to adjust the number of workers depending on the available resources and the number of tiles per batch

Have a look at the [API reference](../../api_reference/inference/exporter/segmentation_exporter.md#aviary.inference.SegmentationExporterConfig)
for more details on the configuration options.

---

### Step 7: Configure the general settings

We will use the following configuration for the general settings:

``` yaml title="config.yaml"
batch_size: 4
num_workers: 4
```

This configuration will do the inference on 4 tiles in parallel.<br />
The number of workers specifies the number of threads that are used for fetching the data.

???+ note "Notes"

    - You may need to adjust the batch size and the number of workers depending on the available resources

---

### Step 8: Run the segmentation pipeline

The final configuration should look like this:

``` yaml title="config.yaml"
data_fetcher:
  name: VRTFetcher
  config:
    path: path/to/your/data.vrt
    tile_size: 128
    ground_sampling_distance: 0.2
    buffer_size: 32

process_area:
  bounding_box: [x_min, y_min, x_max, y_max]
  tile_size: 128

data_preprocessor:
  name: NormalizePreprocessor
  config:
    min_values: [0.0, 0.0, 0.0, 0.0]
    max_values: [255.0, 255.0, 255.0, 255.0]

model:
  name: ONNXSegmentationModel
  config:
    name: sparrow
    ground_sampling_distance: 0.2
    buffer_size: 32

exporter:
  name: SegmentationExporter
  config:
    path: path/to/your/output_directory
    tile_size: 128
    ground_sampling_distance: 0.2
    epsg_code: 25832
    num_workers: 4

batch_size: 4
num_workers: 4
```

To run the segmentation pipeline, run the following command:

=== "pip"

    ```
    aviary segmentation-pipeline path/to/config.yaml
    ```

=== "Docker"

    ```
    docker run --rm \
      -v path/to/config.yaml:/aviary/config.yaml \
      aviary segmentation-pipeline /aviary/config.yaml
    ```

    Note that you need to bind mount all directories and files that are referenced in the configuration file,
    so they're accessible inside the Docker container.<br />
    Add the following options to the command for each directory:

    ```
    -v path/to/directory:/aviary/directory
    ```

    and for each file:

    ```
    -v path/to/file:/aviary/file
    ```

After successfully running the segmentation pipeline, you will find the geodataframe of the impervious surfaces
in the specified output directory as a geopackage named `output.gpkg` and
a JSON file named `processed_coordinates.json` containing the coordinates of the processed tiles.

---

## Next steps:

Have a look at the [how-to guide](how_to_run_the_postprocessing_pipeline.md)
on how to run the postprocessing pipeline on the resulting geodataframe.
