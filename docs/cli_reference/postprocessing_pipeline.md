<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## Postprocessing pipeline

The postprocessing pipeline is a pre-built pipeline designed to postprocess geospatial data.
It consists of the following components:

- A path to the geodataframe
- A [`GeodataPostprocessor`][GeodataPostprocessor] to postprocess the geodata
- A path to export the geodataframe

These components are set up in a configuration file (.yaml file) that is passed to the pipeline.<br />
The configuration file must have the following structure:

``` yaml title="config.yaml"
gdf:

geodata_postprocessor:
  name:
  config:

path:
```

The `name` field must be the name of the class that you want to use for the component.<br />
The `config` field must contain its corresponding configuration.<br />
Note that each class has its own configuration, which can be found in the [API reference].

To run the postprocessing pipeline, run the following command:

=== "pip and uv"

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

  [GeodataPostprocessor]: ../api_reference/geodata/geodata_postprocessor/geodata_postprocessor.md
  [API reference]: ../api_reference/pipeline/postprocessing_pipeline.md#aviary.pipeline.PostprocessingPipelineConfig

---

## Next steps

Have a look at the [how-to guide] on how to run the postprocessing pipeline with an example configuration file.

  [how-to guide]: ../how_to_guides/cli/how_to_run_the_postprocessing_pipeline.md
