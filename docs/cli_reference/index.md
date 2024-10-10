<style>
  .md-sidebar--secondary { visibility: hidden }
</style>

aviary provides a command-line interface (CLI) that allows you to run the pre-built pipelines easily
without writing any code, requiring only a declarative configuration file that specifies the components.

To see the available options and commands of the CLI, run the following command:

=== "pip and uv"

    ```
    aviary
    ```

=== "Docker"

    ```
    docker run --rm aviary
    ```

You can choose from the following pipelines:

<div class="grid cards" markdown>

-   [**Segmentation pipeline**](segmentation_pipeline.md)<br />
    Run a segmentation model on your data

-   [**Postprocessing pipeline**](postprocessing_pipeline.md)<br />
    Postprocess geospatial data

</div>
