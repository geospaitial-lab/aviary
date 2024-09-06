<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## How to run the postprocessing pipeline

Follow along this step-by-step guide to run the [postprocessing pipeline](../../cli_reference/postprocessing_pipeline.md)
with the command-line interface (CLI).

In this example, we will postprocess the resulting geodataframe of the segmentation pipeline,
as described in the previous [how-to guide](how_to_run_the_segmentation_pipeline.md).

### Step 1: Create a configuration file

Create a configuration file (.yaml file) named `config.yaml`.

In the next steps, we will add the configuration of each component of the pipeline to this file.

---

### Step 2: Configure the path to the geodataframe

``` yaml title="config.yaml"
gdf: path/to/your/output.gpkg
```

---

### Step 3: Configure the geodata postprocessor

To postprocess the geodata,
we will use the [`CompositePostprocessor`](../../api_reference/geodata/geodata_postprocessor/composite_postprocessor.md)
with the following configuration:

``` yaml title="config.yaml"
geodata_postprocessor:
  name: CompositePostprocessor
  config:
    geodata_postprocessors_configs:
      - name: FillPostprocessor
        config:
          max_area: 2
      - name: SievePostprocessor
        config:
          min_area: 2
      - name: SimplifyPostprocessor
        config:
          tolerance: 0.2
      - name: FieldNamePostprocessor
        config:
          mapping:
            class: type
      - name: ValuePostprocessor
        config:
          mapping:
            1: buildings
            2: impervious surfaces
          field_name: type
```

This configuration will postprocess the geodataframe by:

- Filling holes in the polygons with an area of up to 2 square meters
- Sieving the polygons with an area of less than 2 square meters
- Simplifying the polygons with a tolerance of 0.2 meters
- Renaming the field `class` to `type`
- Mapping the values `1` and `2` to `buildings` and `impervious surfaces`
  as stated in the [mapping of the values](../../aviary/index.md#mapping-of-the-values) of the model

Note that there are alternative ways to postprocess the geodata.
You can choose from a collection of [geodata postprocessors](../../api_reference/geodata/geodata_postprocessor/geodata_postprocessor.md)
and compose them as needed.

Have a look at the [API reference](../../api_reference/geodata/geodata_postprocessor/composite_postprocessor.md#aviary.geodata.CompositePostprocessorConfig)
for more details on the configuration options.

---

### Step 4: Configure the output path to the postprocessed geodataframe

``` yaml title="config.yaml"
path: path/to/your/postprocessed_output.gpkg
```

---

### Step 5: Run the postprocessing pipeline

The final configuration file should look like this:

``` yaml title="config.yaml"
gdf: path/to/your/output.gpkg

geodata_postprocessor:
  name: CompositePostprocessor
  config:
    geodata_postprocessors_configs:
      - name: FillPostprocessor
        config:
          max_area: 2
      - name: SievePostprocessor
        config:
          min_area: 2
      - name: SimplifyPostprocessor
        config:
          tolerance: 0.2
      - name: FieldNamePostprocessor
        config:
          mapping:
            class: type
      - name: ValuePostprocessor
        config:
          mapping:
            1: buildings
            2: impervious surfaces
          field_name: type

path: path/to/your/postprocessed_output.gpkg
```

To run the postprocessing pipeline, run the following command:

=== "pip"

    ```
    aviary postprocessing-pipeline path/to/config.yaml
    ```

=== "Docker"

    ```
    docker run --rm \
      -v path/to/config.yaml:/aviary/config.yaml \
      aviary postprocessing-pipeline /aviary/config.yaml
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

After successfully running the postprocessing pipeline, you will find the postprocessed geodataframe
of the impervious surfaces at the specified output path as a geopackage named `postprocessed_output.gpkg`.
