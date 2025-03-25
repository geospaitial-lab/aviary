<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://www.github.com/geospaitial-lab/aviary/raw/main/docs/assets/aviary_logo_white.svg">
  <img alt="aviary" src="https://www.github.com/geospaitial-lab/aviary/raw/main/docs/assets/aviary_logo_black.svg" width="30%">
</picture>

</div>

<div align="center">

[![CI][CI Badge]][CI]
[![Coverage][Coverage Badge]][Coverage]
[![Docs][Docs Badge]][Docs]

</div>

<div align="center">

[![PyPI version][PyPI version Badge]][PyPI]
[![Python version][Python version Badge]][PyPI]

</div>

<div align="center">

[![Chat][Chat Badge]][Chat]

</div>

  [CI Badge]: https://img.shields.io/github/actions/workflow/status/geospaitial-lab/aviary/ci.yaml?branch=main&color=black&label=CI&logo=GitHub
  [CI]: https://www.github.com/geospaitial-lab/aviary/actions/workflows/ci.yaml
  [Coverage Badge]: https://img.shields.io/codecov/c/github/geospaitial-lab/aviary/main?color=black&label=Coverage&logo=codecov&logoColor=white
  [Coverage]: https://app.codecov.io/gh/geospaitial-lab/aviary
  [Docs Badge]: https://img.shields.io/github/actions/workflow/status/geospaitial-lab/aviary/docs.yaml?branch=main&color=black&label=Docs&logo=materialformkdocs&logoColor=white
  [Docs]: https://geospaitial-lab.github.io/aviary
  [PyPI version Badge]: https://img.shields.io/pypi/v/geospaitial-lab-aviary?color=black&label=PyPI&logo=PyPI&logoColor=white
  [Python version Badge]: https://img.shields.io/pypi/pyversions/geospaitial-lab-aviary?color=black&label=Python&logo=Python&logoColor=white
  [PyPI]: https://www.pypi.org/project/geospaitial-lab-aviary
  [Chat Badge]: https://img.shields.io/matrix/geospaitial-lab-aviary%3Amatrix.org?color=black&label=Chat&logo=matrix
  [Chat]: https://matrix.to/#/#geospaitial-lab-aviary:matrix.org

aviary provides composable components for tile-based processing of geospatial data.
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

- **Task-agnostic**<br />
  Process geospatial data with a range of machine learning tasks

- **ML-framework agnostic**<br />
  Use your favorite machine learning framework

## Installation

You can choose between two installation methods, whether you need access to the Python API or
the command-line interface (CLI) only.
If you just want to use the pre-built pipelines with the command-line interface, you can use the Docker image.

### Installation with pip

⚠️ **Note**: aviary is currently released as a pre-release version.
To install the latest version, you need to add the `--pre` flag.

```
pip install geospaitial-lab-aviary
```

Note that aviary requires Python 3.10 or later.

Have a look at the [installation guide][installation guide pip] for further information.

  [installation guide pip]: https://geospaitial-lab.github.io/aviary/how_to_guides/installation/how_to_install_aviary_with_pip

### Installation with uv

```
uv pip install geospaitial-lab-aviary
```

Note that aviary requires Python 3.10 or later.

Have a look at the [installation guide][installation guide uv] for further information.

  [installation guide uv]: https://geospaitial-lab.github.io/aviary/how_to_guides/installation/how_to_install_aviary_with_uv

### Installation with Docker

```
docker pull ghcr.io/geospaitial-lab/aviary
```

Have a look at the [installation guide][installation guide docker] for further information.

  [installation guide docker]: https://geospaitial-lab.github.io/aviary/how_to_guides/installation/how_to_install_aviary_with_docker

## Next steps

Have a look at the [how-to guides] to get started.

  [how-to guides]: https://geospaitial-lab.github.io/aviary/how_to_guides

## Documentation

The full documentation is available at [geospaitial-lab.github.io/aviary].

  [geospaitial-lab.github.io/aviary]: https://geospaitial-lab.github.io/aviary

## About

aviary is developed by the [geospaitial lab]
at the [Westfälische Hochschule - Westphalian University of Applied Sciences]
in Gelsenkirchen, Germany.

  [geospaitial lab]: https://www.github.com/geospaitial-lab
  [Westfälische Hochschule - Westphalian University of Applied Sciences]: https://www.w-hs.de
