<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

## Postprocessing pipeline

The postprocessing pipeline is a pre-built pipeline designed to postprocess geospatial data.
It consists of the following components:

- a path to the geodataframe
- a [GeodataPostprocessor](../api_reference/geodata/geodata_postprocessor.md) to postprocess the geodata
- a path to export the geodataframe

These components are set up in a configuration file (.yaml file) that is passed to the pipeline.<br />
The configuration file must have the following structure:

``` yaml
gdf:

geodata_postprocessor:
  name:
  config:

path:
```

The `name` field must be the name of the class that you want to use for the component.<br />
The `config` field must contain its corresponding configuration.<br />
Note that each class has its own configuration, which can be found in the
[API reference](../api_reference/pipeline/postprocessing_pipeline.md#aviary.pipeline.PostprocessingPipelineConfig).

To run the postprocessing pipeline, run the following command:

=== "pip"

    ```
    aviary postprocessing-pipeline path/to/config.yaml
    ```

=== "Docker"

    ```
    docker run --rm aviary postprocessing-pipeline path/to/config.yaml
    ```

---

## Next steps

Have a look at the [how-to guide](../how_to_guides/cli/how_to_run_the_postprocessing_pipeline.md)
on how to run the postprocessing pipeline with an example configuration file.
