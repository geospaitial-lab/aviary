<style>
  @media screen and (min-width: 76.25em) {
    .md-sidebar--primary { visibility: hidden }
  }
  .md-sidebar--secondary { visibility: hidden }
</style>

aviary provides composable components for building inference and postprocessing pipelines
for remote sensing data.
This enables you to easily run models on large datasets, export the predictions in a
georeferenced file format and postprocess them for further downstream tasks.<br />
Besides the pipelines, aviary also provides task-specific models for remote sensing applications.

aviary is designed upon the following concepts:

<div class="grid cards" markdown>

-   **High-level Python API**<br />
    Abstract components for building pipelines without boilerplate code

-   **Command-line interface (CLI)**<br />
    Run the pre-built pipelines easily without writing any code

-   **Customizable pipelines**<br />
    Compose your own pipelines with the provided components

-   **Extensible components**<br />
    Add your own components to the pipeline

-   **Support for large datasets**<br />
    Tile-based processing for large datasets (local, remote or web services)

-   **Support for geospatial data**<br />
    Export predictions as geodata, ready for downstream tasks

</div>

## Installation

You can choose between two installation methods, whether you need access to the Python API or
the command-line interface (CLI) only.
If you just want to use the pre-built pipelines with the command-line interface, you can use the Docker image.

=== "pip"

    ```
    pip install geospaitial-lab-aviary
    ```

    Note that aviary requires Python 3.10 or later.

    Have a look at the [installation guide](how_to_guides/installation/how_to_install_aviary_with_pip.md)
    for further information.

=== "Docker"

    ```
    docker pull ghcr.io/geospaitial-lab/aviary
    ```

    Have a look at the [installation guide](how_to_guides/installation/how_to_install_aviary_with_docker.md)
    for further information.

## Next steps

Have a look at the [how-to guides](how_to_guides/index.md)
to get started.

## About

aviary is developed by the [geospaitial lab](https://github.com/geospaitial-lab)
at the [Westfälische Hochschule - Westphalian University of Applied Sciences](https://w-hs.de)
in Gelsenkirchen, Germany.
