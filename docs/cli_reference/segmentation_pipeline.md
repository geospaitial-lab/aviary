<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## Segmentation pipeline

The segmentation pipeline is a pre-built pipeline designed to run a segmentation model on your data.
It consists of the following components:

- A [`DataFetcher`](../api_reference/data/data_fetcher/data_fetcher.md) to fetch data from a source
- A [`ProcessArea`](../api_reference/process_area.md) to specify the area of interest
- A [`DataPreprocessor`](../api_reference/data/data_preprocessor/data_preprocessor.md) to preprocess the fetched data
- A [`SegmentationModel`](../api_reference/inference/model/segmentation_model.md) to do the inference on the preprocessed data
- An [`SegmentationExporter`](../api_reference/inference/exporter/segmentation_exporter.md) to export the predictions dynamically as geospatial data

These components are set up in a configuration file (.yaml file) that is passed to the pipeline.<br />
The configuration file must have the following structure:

``` yaml title="config.yaml"
data_fetcher:
  name:
  config:

process_area:

data_preprocessor:
  name:
  config:

model:
  name:
  config:

exporter:
  name:
  config:

batch_size: 1
num_workers: 4
```

The `name` field must be the name of the class that you want to use for the component.<br />
The `config` field must contain its corresponding configuration.<br />
Note that each class has its own configuration, which can be found in the
[API reference](../api_reference/pipeline/segmentation_pipeline.md#aviary.pipeline.SegmentationPipelineConfig).

To run the segmentation pipeline, run the following command:

=== "pip and uv"

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

---

## Next steps

Have a look at the [how-to guide](../how_to_guides/cli/how_to_run_the_segmentation_pipeline.md)
on how to run the segmentation pipeline with an example configuration file.
