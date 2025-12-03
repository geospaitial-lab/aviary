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

aviary is the pythonic way to run your AI models on geospatial data
with minimal boilerplate – from quick prototyping to production-grade pipelines.

- **High-level Python API**<br />
  Define and run pipelines from composable components instead of writing ad‑hoc scripts

- **Config‑driven CLI**<br />
  Define and run the same pipelines with the command-line interface using a simple declarative config file

- **Extensible by design**<br />
  Add custom components via a plugin registry and distribute them as a plugin package

- **AI framework-agnostic**<br />
  Use models from PyTorch, TensorFlow, ONNX, or scikit‑learn

---

## Installation

⚠️ **Note**: aviary is currently released as a pre-release version.
To install the latest version, you need to add the `--pre` flag.

### Installation with pip

```bash
pip install geospaitial-lab-aviary
```

Note that aviary requires Python 3.10 or later.

Have a look at the [installation guide][installation guide pip] for further information.

  [installation guide pip]: https://geospaitial-lab.github.io/aviary/how_to_guides/installation/how_to_install_aviary_with_pip

### Installation with uv

```bash
uv pip install geospaitial-lab-aviary
```

Note that aviary requires Python 3.10 or later.

Have a look at the [installation guide][installation guide uv] for further information.

  [installation guide uv]: https://geospaitial-lab.github.io/aviary/how_to_guides/installation/how_to_install_aviary_with_uv

### Installation with Docker

```bash
docker pull ghcr.io/geospaitial-lab/aviary
```

Have a look at the [installation guide][installation guide docker] for further information.

  [installation guide docker]: https://geospaitial-lab.github.io/aviary/how_to_guides/installation/how_to_install_aviary_with_docker

---

## Next steps

Have a look at the [how-to guides] to get started.

  [how-to guides]: https://geospaitial-lab.github.io/aviary/how_to_guides

---

## Documentation

The documentation is available at [geospaitial-lab.github.io/aviary].

  [geospaitial-lab.github.io/aviary]: https://geospaitial-lab.github.io/aviary

---

## License

aviary is licensed under the [GPL-3.0 license].

  [GPL-3.0 license]: LICENSE.md
