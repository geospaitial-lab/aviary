<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/geospaitial-lab/aviary/raw/main/docs/assets/aviary_logo_white.svg">
  <img alt="aviary" src="https://github.com/geospaitial-lab/aviary/raw/main/docs/assets/aviary_logo_black.svg" width="30%">
</picture>

</div>

<div align="center">

[![CI](https://img.shields.io/github/actions/workflow/status/geospaitial-lab/aviary/ci.yaml?branch=main&color=black&label=CI&logo=GitHub)](https://github.com/geospaitial-lab/aviary/actions/workflows/ci.yaml)
[![Coverage](https://img.shields.io/codecov/c/github/geospaitial-lab/aviary/main?color=black&label=Coverage&logo=codecov&logoColor=white)](https://app.codecov.io/gh/geospaitial-lab/aviary)
[![Docs](https://img.shields.io/github/actions/workflow/status/geospaitial-lab/aviary/docs.yaml?branch=main&color=black&label=Docs&logo=materialformkdocs&logoColor=white)](https://geospaitial-lab.github.io/aviary)

</div>

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/geospaitial-lab-aviary?color=black&label=PyPI)](https://pypi.org/project/geospaitial-lab-aviary)
[![Python version](https://img.shields.io/pypi/pyversions/geospaitial-lab-aviary?color=black&label=Python)](https://pypi.org/project/geospaitial-lab-aviary)

</div>

aviary provides composable components for building inference and postprocessing pipelines
for remote sensing data.
This enables you to easily run models on large datasets, export the predictions in a
georeferenced file format and postprocess them for further downstream tasks.<br />
Besides the pipelines, aviary also provides task-specific models for remote sensing applications.

aviary is designed upon the following concepts:

- **High-level Python API**<br />
  Abstract components for building pipelines without boilerplate code

- **Command-line interface (CLI)**<br />
  Run the pre-built pipelines easily without writing any code

- **Customizable pipelines**<br />
  Compose your own pipelines with the provided components

- **Extensible components**<br />
  Add your own components to the pipeline

- **Support for large datasets**<br />
  Tile-based processing for large datasets (local, remote or web services)

- **Support for geospatial data**<br />
  Export predictions as geodata, ready for downstream tasks

## Installation

You can choose between two installation methods, whether you need access to the Python API or
the command-line interface (CLI) only.
If you just want to use the pre-built pipelines with the command-line interface, you can use the Docker image.

### Installation with pip

```
pip install geospaitial-lab-aviary
```

Note that aviary requires Python 3.10 or later.

Have a look at the [installation guide](https://geospaitial-lab.github.io/aviary/how_to_guides/installation/how_to_install_aviary_with_pip)
for further information.

### Installation with Docker

```
docker pull ghcr.io/geospaitial-lab/aviary
```

Have a look at the [installation guide](https://geospaitial-lab.github.io/aviary/how_to_guides/installation/how_to_install_aviary_with_docker)
for further information.

## Next steps

Have a look at the [how-to guides](https://geospaitial-lab.github.io/aviary/how_to_guides)
to get started.

## Documentation

The full documentation is available at [geospaitial-lab.github.io/aviary](https://geospaitial-lab.github.io/aviary).

## About

aviary is developed by the [geospaitial lab](https://github.com/geospaitial-lab)
at the [Westfälische Hochschule - Westphalian University of Applied Sciences](https://w-hs.de)
in Gelsenkirchen, Germany.
