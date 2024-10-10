## Documentation

The documentation is built with [MkDocs](https://www.mkdocs.org)
and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material) theme.<br />
The API reference is generated with [mkdocstrings](https://mkdocstrings.github.io).

The docs are built and deployed automatically on new releases with the [docs workflow](../.github/workflows/docs.yaml).

## Build the docs locally

Make sure you have the development dependencies installed:

```
pip install -r dev/requirements.txt
```

or:

```
uv pip install -r dev/requirements.txt
```

Build the docs:

```
mkdocs serve -f dev/mkdocs.yaml
```
