<style>
  @media screen and (min-width: 76.25em) {
    .md-sidebar--primary { visibility: hidden }
  }
  .md-sidebar--secondary { visibility: hidden }
</style>

aviary is the pythonic way to run your AI models on geospatial data
with minimal boilerplate – from quick prototyping to production-grade pipelines.

<div class="grid cards" markdown>

-   **High-level Python API**<br />
    Define and run pipelines from composable components instead of writing ad‑hoc scripts

-   **Config‑driven CLI**<br />
    Define and run the same pipelines with the command-line interface using a simple declarative config file

-   **Extensible by design**<br />
    Add custom components via a plugin registry and distribute them as a plugin package

-   **AI framework-agnostic**<br />
    Use models from PyTorch, TensorFlow, ONNX, or scikit‑learn

</div>

---

## Installation

=== "pip"

    ```
    pip install geospaitial-lab-aviary
    ```

    Note that aviary requires Python 3.10 or later.

    Have a look at the [installation guide][installation guide pip] for further information.

=== "uv"

    ```
    uv pip install geospaitial-lab-aviary
    ```

    Note that aviary requires Python 3.10 or later.

    Have a look at the [installation guide][installation guide uv] for further information.

=== "Docker"

    ```
    docker pull ghcr.io/geospaitial-lab/aviary
    ```

    Have a look at the [installation guide][installation guide docker] for further information.

  [installation guide pip]: how_to_guides/installation/how_to_install_aviary_with_pip.md
  [installation guide uv]: how_to_guides/installation/how_to_install_aviary_with_uv.md
  [installation guide docker]: how_to_guides/installation/how_to_install_aviary_with_docker.md

---

## Next steps

Have a look at the [how-to guides] to get started.

  [how-to guides]: how_to_guides/index.md

---

## License

aviary is licensed under the [GPL-3.0 license :material-arrow-top-right:][GPL-3.0 license].

  [GPL-3.0 license]: https://github.com/geospaitial-lab/aviary/blob/main/LICENSE.md
